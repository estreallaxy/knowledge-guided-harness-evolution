"""Windows Photoshop environment used by PSBench."""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
import shutil
import subprocess
import threading
import time
from typing import Any, Dict, Optional, Tuple

import gymnasium as gym
import numpy as np
from PIL import Image, ImageGrab
import psutil
import pyautogui

from photoshop_evaluators import PhotoshopEvaluator


logger = logging.getLogger("photoshop_env")
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.6


class PhotoshopProcessCrashedError(RuntimeError):
    """Signal that the configured Photoshop process disappeared."""

    photoshop_process_crash = True


class PhotoshopEnv(gym.Env):
    """Manage one Photoshop task and export its final rendered result."""

    metadata = {"render_modes": ["rgb_array"]}

    def __init__(
        self,
        ps_executable_path: Optional[str] = None,
        action_space: str = "pyautogui",
        screen_size: Tuple[int, int] = (1920, 1080),
        require_screenshot: bool = True,
        debug_mode: bool = False,
        auto_save_interval: int = 300,
        tasks_base_dir: str = "tasks",
        results_base_dir: str = "results",
        cache_dir: str = "cache",
        enable_recording: bool = False,
        recording_fps: int = 10,
        max_consecutive_waits: int = 3,
    ):
        del action_space, screen_size, auto_save_interval
        del cache_dir, enable_recording, recording_fps

        executable = ps_executable_path or os.getenv("PHOTOSHOP_EXECUTABLE")
        if not executable:
            raise ValueError(
                "Photoshop executable is required. Pass --photoshop-executable "
                "or set PHOTOSHOP_EXECUTABLE."
            )
        self.ps_executable_path = str(Path(executable).resolve())
        if not Path(self.ps_executable_path).is_file():
            raise FileNotFoundError(
                f"Photoshop executable not found: {self.ps_executable_path}"
            )

        self.tasks_base_dir = Path(tasks_base_dir).resolve()
        self.results_base_dir = Path(results_base_dir).resolve()
        self.results_base_dir.mkdir(parents=True, exist_ok=True)
        self.require_screenshot = require_screenshot
        self.debug_mode = debug_mode
        self.max_consecutive_waits = max_consecutive_waits

        self.ps_process: Optional[subprocess.Popen] = None
        self.ps_app = None
        self.is_ps_ready = False
        self.task_id: Optional[str] = None
        self.instruction: Optional[str] = None
        self.task_config: Optional[Dict[str, Any]] = None
        self.current_task_folder: Optional[Path] = None
        self.current_result_folder: Optional[Path] = None
        self.current_working_path: Optional[Path] = None
        self.evaluator: Optional[PhotoshopEvaluator] = None
        self._step_no = 0
        self._traj_no = -1
        self.consecutive_wait_count = 0

    def _set_task_info(self, task_config: Dict[str, Any]) -> None:
        self.task_config = task_config
        self.task_id = str(task_config["id"]).zfill(3)
        self.instruction = str(task_config["instruction"])
        configured_folder = task_config.get("task_folder_path")
        self.current_task_folder = (
            Path(configured_folder).resolve()
            if configured_folder
            else (self.tasks_base_dir / self.task_id).resolve()
        )
        if not self.current_task_folder.is_dir():
            raise FileNotFoundError(
                f"Task directory not found: {self.current_task_folder}"
            )
        self.current_result_folder = (
            self.results_base_dir / self.task_id
        ).resolve()
        self.current_result_folder.mkdir(parents=True, exist_ok=True)
        self.evaluator = PhotoshopEvaluator(
            str(self.current_task_folder),
            str(self.current_result_folder),
            task_config=task_config,
        )

    def _matching_photoshop_processes(self):
        expected = os.path.normcase(self.ps_executable_path)
        for process in psutil.process_iter(["pid", "exe"]):
            try:
                executable = process.info.get("exe")
                if (
                    executable
                    and os.path.normcase(str(Path(executable).resolve())) == expected
                    and process.is_running()
                ):
                    yield process
            except (psutil.AccessDenied, psutil.NoSuchProcess, OSError):
                continue

    def is_photoshop_process_alive(self) -> bool:
        """Return whether the configured Photoshop executable is running."""
        return next(self._matching_photoshop_processes(), None) is not None

    def assert_photoshop_process_alive(self) -> None:
        if not self.is_photoshop_process_alive():
            raise PhotoshopProcessCrashedError(
                "photoshop_process_crashed: the configured Photoshop process "
                f"disappeared during task {self.task_id}"
            )

    def _attach_photoshop_com(self, timeout: float = 60.0):
        import win32com.client

        expected_directory = os.path.normcase(
            str(Path(self.ps_executable_path).parent.resolve())
        )
        deadline = time.time() + timeout
        last_error = None
        while time.time() < deadline:
            try:
                application = win32com.client.GetActiveObject(
                    "Photoshop.Application"
                )
                active_directory = os.path.normcase(
                    str(Path(str(application.Path)).resolve())
                )
                if active_directory != expected_directory:
                    raise RuntimeError(
                        "Photoshop COM is connected to a different installation: "
                        f"{active_directory}"
                    )
                _ = application.Name
                return application
            except Exception as error:
                last_error = error
                time.sleep(0.5)
        raise TimeoutError(
            "The configured Photoshop executable is running, but its COM "
            f"application was not available within {timeout:.0f} seconds: {last_error}"
        )

    def _start_photoshop(self) -> None:
        """Start the configured executable or attach to its existing process."""
        already_running = self.is_photoshop_process_alive()
        if not already_running:
            logger.info("Starting Photoshop: %s", self.ps_executable_path)
            self.ps_process = subprocess.Popen([self.ps_executable_path])
        else:
            logger.info("Attaching to the configured running Photoshop process.")

        try:
            self.ps_app = self._attach_photoshop_com()
            self.ps_app.Visible = True
            self.is_ps_ready = True
            logger.info("Photoshop COM connection is ready.")
        except Exception:
            if (
                not already_running
                and self.ps_process is not None
                and self.ps_process.poll() is None
            ):
                self.ps_process.terminate()
            self.ps_process = None
            self.ps_app = None
            self.is_ps_ready = False
            raise

    @staticmethod
    def _com_hresult(error: Exception) -> Optional[int]:
        hresult = getattr(error, "hresult", None)
        if hresult is None and getattr(error, "args", None):
            hresult = error.args[0]
        return hresult if isinstance(hresult, int) else None

    def _run_javascript_with_busy_retry(
        self,
        script: str,
        attempts: int = 5,
        commit_modal_operation: bool = False,
    ) -> None:
        last_error = None
        for attempt in range(attempts):
            try:
                self.assert_photoshop_process_alive()
                self.ps_app = self.ps_app or self._attach_photoshop_com(timeout=5)
                self.ps_app.DoJavaScript(script)
                return
            except PhotoshopProcessCrashedError:
                raise
            except Exception as error:
                last_error = error
                if self._com_hresult(error) != -2147417846:
                    raise
                logger.warning(
                    "Photoshop is busy; retrying COM operation (%s/%s).",
                    attempt + 1,
                    attempts,
                )
                if commit_modal_operation:
                    pyautogui.press("enter")
                time.sleep(2)
        raise RuntimeError(
            f"Photoshop remained busy after {attempts} attempts: {last_error}"
        )

    def _close_all_documents(self) -> None:
        if not self.is_photoshop_process_alive():
            return
        script = (
            "while (app.documents.length > 0) {"
            "app.activeDocument.close(SaveOptions.DONOTSAVECHANGES);"
            "}"
        )
        self._run_javascript_with_busy_retry(script, attempts=3)

    def prepare_for_export(self, attempts: int = 3) -> None:
        """Commit or dismiss a modal Photoshop operation before exporting."""
        self.assert_photoshop_process_alive()
        last_error = None
        for attempt in range(attempts):
            logger.info(
                "Confirming any pending Photoshop modal operation before export "
                "(%s/%s).",
                attempt + 1,
                attempts,
            )
            pyautogui.press("enter")
            time.sleep(1)
            try:
                self.ps_app = self.ps_app or self._attach_photoshop_com(timeout=5)
                _ = self.ps_app.Documents.Count
                return
            except PhotoshopProcessCrashedError:
                raise
            except Exception as error:
                last_error = error
                if self._com_hresult(error) != -2147417846:
                    raise
        raise RuntimeError(
            "Photoshop remained blocked by a modal operation before export: "
            f"{last_error}"
        )

    def _start_export_modal_watchdog(
        self,
        stop_event: threading.Event,
        initial_delay: float = 2.0,
        interval: float = 2.0,
        max_attempts: int = 12,
    ) -> threading.Thread:
        """Confirm a modal dialog if a Photoshop COM export remains blocked."""

        def confirm_modal_operations() -> None:
            if stop_event.wait(initial_delay):
                return
            for attempt in range(max_attempts):
                if stop_event.is_set():
                    return
                if not self.is_photoshop_process_alive():
                    return
                logger.warning(
                    "Photoshop export is still pending; confirming a possible "
                    "modal operation (%s/%s).",
                    attempt + 1,
                    max_attempts,
                )
                pyautogui.press("enter")
                if stop_event.wait(interval):
                    return

        thread = threading.Thread(
            target=confirm_modal_operations,
            name=f"photoshop-export-watchdog-{self.task_id}",
            daemon=True,
        )
        thread.start()
        return thread

    def _prepare_task_input(self) -> None:
        input_name = self.task_config.get("resources", {}).get("input_file")
        if not input_name:
            raise ValueError(f"Task {self.task_id} does not specify an input file.")
        input_path = (self.current_task_folder / input_name).resolve()
        if not input_path.is_file():
            raise FileNotFoundError(f"Task input not found: {input_path}")

        supported = {".jpg", ".jpeg", ".png", ".psd", ".bmp", ".tif", ".tiff"}
        if input_path.suffix.lower() not in supported:
            raise ValueError(f"Unsupported task input format: {input_path.suffix}")

        working_path = (
            self.current_result_folder
            / f"{self.task_id}_working{input_path.suffix.lower()}"
        )
        shutil.copy2(input_path, working_path)
        self.current_working_path = working_path
        logger.info("Created task working copy: %s", working_path)

        self.ps_app.Open(str(working_path))
        deadline = time.time() + 30
        while time.time() < deadline:
            try:
                if self.ps_app.Documents.Count > 0:
                    pyautogui.press("v")
                    time.sleep(0.5)
                    logger.info("Opened the working image and selected the Move Tool.")
                    return
            except Exception as error:
                if self._com_hresult(error) != -2147417846:
                    raise
            time.sleep(0.25)
        raise TimeoutError(f"Photoshop did not open the task input: {working_path}")

    def reset(
        self,
        task_config: Optional[Dict[str, Any]] = None,
        seed=None,
        options=None,
    ) -> Dict[str, Any]:
        del seed, options
        if task_config is None:
            raise ValueError("A task configuration is required.")
        self._set_task_info(task_config)
        self._step_no = 0
        self._traj_no += 1
        self.consecutive_wait_count = 0
        self._start_photoshop()
        self._close_all_documents()
        self._prepare_task_input()
        logger.info("Photoshop environment reset for task %s.", self.task_id)
        return self._get_obs()

    def _get_screenshot(self):
        if not self.require_screenshot:
            return None
        return np.asarray(ImageGrab.grab())

    def _get_obs(self) -> Dict[str, Any]:
        return {
            "screenshot": self._get_screenshot(),
            "task_id": self.task_id,
            "instruction": self.instruction,
            "traj_no": self._traj_no,
            "step_no": self._step_no,
            "difficulty_level": self.task_config.get(
                "difficulty_level", "medium"
            ),
        }

    @staticmethod
    def _is_wait_action(action: Any) -> bool:
        return isinstance(action, str) and action.strip().upper() == "WAIT"

    def step(
        self, action: Any, pause: float = 2.0
    ) -> Tuple[Dict[str, Any], float, bool, Dict[str, Any]]:
        self.assert_photoshop_process_alive()
        self._step_no += 1
        normalized = action.strip().upper() if isinstance(action, str) else action
        info = {
            "step_no": self._step_no,
            "traj_no": self._traj_no,
            "ps_ready": self.is_ps_ready,
            "consecutive_wait_count": self.consecutive_wait_count,
        }

        if normalized == "DONE":
            info["success"] = True
            return self._get_obs(), 0.0, True, info
        if normalized == "FAIL":
            info["fail"] = True
            return self._get_obs(), 0.0, True, info
        if normalized == "WAIT":
            self.consecutive_wait_count += 1
            info["consecutive_wait_count"] = self.consecutive_wait_count
            if self.consecutive_wait_count >= self.max_consecutive_waits:
                info.update(
                    {
                        "fail": True,
                        "failure_reason": (
                            f"consecutive_waits_{self.consecutive_wait_count}"
                        ),
                    }
                )
                return self._get_obs(), 0.0, True, info
        else:
            self.consecutive_wait_count = 0

        time.sleep(pause)
        return self._get_obs(), 0.0, False, info

    def _save_result_file(self, filename: Optional[str] = None) -> str:
        """Export the active rendered document to a deterministic PNG."""
        self.assert_photoshop_process_alive()
        output_name = filename or f"{self.task_id}_result.png"
        output_name = f"{Path(output_name).stem}.png"
        output_path = (self.current_result_folder / output_name).resolve()
        if output_path.exists():
            output_path.unlink()

        output_literal = json.dumps(str(output_path).replace("\\", "/"))
        script = f"""
        if (app.documents.length === 0) {{
            throw new Error("No active Photoshop document");
        }}
        var sourceDocument = app.activeDocument;
        var exportDocument = sourceDocument.duplicate();
        try {{
            app.activeDocument = exportDocument;
            if (exportDocument.mode !== DocumentMode.RGB) {{
                exportDocument.changeMode(ChangeMode.RGB);
            }}
            var outputFile = new File({output_literal});
            var options = new PNGSaveOptions();
            options.interlaced = false;
            exportDocument.saveAs(
                outputFile, options, true, Extension.LOWERCASE
            );
        }} finally {{
            exportDocument.close(SaveOptions.DONOTSAVECHANGES);
            app.activeDocument = sourceDocument;
        }}
        """
        watchdog_stop = threading.Event()
        watchdog_thread = self._start_export_modal_watchdog(watchdog_stop)
        try:
            self._run_javascript_with_busy_retry(
                script, attempts=5, commit_modal_operation=True
            )
        finally:
            watchdog_stop.set()
            watchdog_thread.join(timeout=1)

        if not output_path.is_file() or output_path.stat().st_size == 0:
            raise RuntimeError(
                f"Photoshop did not export a valid result: {output_path}"
            )
        with Image.open(output_path) as image:
            image.verify()
        logger.info("Exported Photoshop result: %s", output_path)
        return str(output_path)

    def evaluate(self, result_path: Optional[str] = None) -> Dict[str, Any]:
        """Evaluate the candidate using the task-specific visual rubric."""
        if self.evaluator is None:
            return {
                "task_id": self.task_id,
                "passed": False,
                "summary": "The evaluator is not initialized.",
                "criteria": [],
                "failed_requirements": [],
                "evaluation_error": "evaluator_not_initialized",
            }
        candidate = result_path or self._save_result_file()
        return self.evaluator.evaluate(candidate)

    def render(self):
        return self._get_screenshot()

    def close(self) -> Dict[str, Any]:
        """Close task documents and remove the temporary working image."""
        logger.info("Closing the Photoshop task environment.")
        try:
            self._close_all_documents()
        except Exception as error:
            logger.warning("Could not close Photoshop documents cleanly: %s", error)

        if self.current_working_path and self.current_working_path.is_file():
            try:
                self.current_working_path.unlink()
                logger.info("Removed the temporary task working copy.")
            except OSError as error:
                logger.warning("Could not remove the working copy: %s", error)

        self.current_working_path = None
        self.ps_app = None
        self.ps_process = None
        self.is_ps_ready = False
        return {}
