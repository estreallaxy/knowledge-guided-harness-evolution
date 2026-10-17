"""Claude Computer Use implementation used by PSBench."""

import base64
import io
import json
import os
import time
from typing import Any, Dict, List, Optional

from anthropic import Anthropic
from PIL import Image, ImageGrab
import pyautogui

from .agent_base import BaseAgent


class ClaudeCUAAgent(BaseAgent):
    """Run a complete Claude Computer Use loop against Adobe Photoshop."""

    MODEL_WIDTH = 1024
    MODEL_HEIGHT = 640
    STEP_LIMITS = {"easy": 15, "medium": 30, "hard": 50}

    def __init__(self):
        super().__init__("Claude-CUA")
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY is not configured.")

        self.model_name = os.getenv("CLAUDE_MODEL", "claude-opus-4-6")
        self.base_url = os.getenv("ANTHROPIC_BASE_URL")
        self.tool_type = os.getenv(
            "CLAUDE_COMPUTER_TOOL_TYPE", "computer_20251124"
        )
        self.computer_use_beta = os.getenv(
            "CLAUDE_COMPUTER_USE_BETA", "computer-use-2025-11-24"
        )
        self.screen_width = int(os.getenv("PSBENCH_SCREEN_WIDTH", "1920"))
        self.screen_height = int(os.getenv("PSBENCH_SCREEN_HEIGHT", "1080"))
        self._current_instruction = ""

        if self.base_url:
            self.client = Anthropic(api_key=api_key, base_url=self.base_url)
        else:
            self.client = Anthropic(api_key=api_key)

    def reset(self) -> None:
        super().reset()
        self._current_instruction = ""
        self.logger.info("%s was reset.", self.name)

    def plan_task(
        self, instruction: str, screenshot: Optional[Any] = None
    ) -> List[str]:
        self._current_instruction = instruction
        plan = ["Complete the task through the Claude Computer Use loop."]
        self.log_semantic_plan(plan)
        return plan

    def _validate_display(self) -> None:
        actual_width, actual_height = pyautogui.size()
        if (actual_width, actual_height) != (
            self.screen_width,
            self.screen_height,
        ):
            raise RuntimeError(
                "Display size mismatch: Claude-CUA is configured for "
                f"{self.screen_width}x{self.screen_height}, but the active display is "
                f"{actual_width}x{actual_height}. Set Windows display scaling to 100% "
                "and configure PSBENCH_SCREEN_WIDTH/PSBENCH_SCREEN_HEIGHT if needed."
            )

    def _take_screenshot_b64(self) -> str:
        self.assert_environment_healthy()
        image = ImageGrab.grab()
        image = image.resize(
            (self.MODEL_WIDTH, self.MODEL_HEIGHT), Image.Resampling.LANCZOS
        )
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode("ascii")

    def _remap_coord(self, model_x: int, model_y: int) -> tuple[int, int]:
        real_x = round(model_x * self.screen_width / self.MODEL_WIDTH)
        real_y = round(model_y * self.screen_height / self.MODEL_HEIGHT)
        real_x = max(0, min(real_x, self.screen_width - 1))
        real_y = max(0, min(real_y, self.screen_height - 1))
        return real_x, real_y

    @staticmethod
    def _parse_key_string(key_string: str) -> List[str]:
        key_map = {
            "Return": "enter",
            "Escape": "escape",
            "BackSpace": "backspace",
            "Delete": "delete",
            "Tab": "tab",
            "space": "space",
            "Space": "space",
            "ctrl": "ctrl",
            "alt": "alt",
            "shift": "shift",
            "super": "win",
            "cmd": "win",
            "Up": "up",
            "Down": "down",
            "Left": "left",
            "Right": "right",
            "Home": "home",
            "End": "end",
            "Page_Up": "pageup",
            "Page_Down": "pagedown",
        }
        keys = []
        for part in key_string.split("+"):
            part = part.strip()
            keys.append(key_map.get(part, part.lower()))
        return keys

    def _execute_cua_action(self, action_input: Dict[str, Any]) -> None:
        self.assert_environment_healthy()
        action = action_input.get("action")
        self.logger.info("Claude CUA action: %s", action_input)

        if action == "screenshot":
            return

        if action in {
            "click",
            "left_click",
            "right_click",
            "middle_click",
            "double_click",
            "triple_click",
            "mouse_move",
        }:
            coordinate = action_input.get("coordinate", [0, 0])
            if isinstance(coordinate, str):
                coordinate = json.loads(coordinate)
            x, y = self._remap_coord(int(coordinate[0]), int(coordinate[1]))

            if action == "right_click":
                pyautogui.rightClick(x, y)
            elif action == "middle_click":
                pyautogui.middleClick(x, y)
            elif action == "double_click":
                pyautogui.doubleClick(x, y)
            elif action == "triple_click":
                pyautogui.tripleClick(x, y)
            elif action == "mouse_move":
                pyautogui.moveTo(x, y)
            else:
                modifier = action_input.get("text", "")
                keys = self._parse_key_string(modifier) if modifier else []
                for key in keys:
                    pyautogui.keyDown(key)
                try:
                    pyautogui.click(x, y)
                finally:
                    for key in reversed(keys):
                        pyautogui.keyUp(key)
            time.sleep(0.3)
            return

        if action == "left_click_drag":
            start = action_input.get("start_coordinate", [0, 0])
            end = action_input.get("stop_coordinate", [0, 0])
            start_x, start_y = self._remap_coord(int(start[0]), int(start[1]))
            end_x, end_y = self._remap_coord(int(end[0]), int(end[1]))
            pyautogui.moveTo(start_x, start_y)
            pyautogui.dragTo(end_x, end_y, duration=1)
            time.sleep(0.3)
            return

        if action == "scroll":
            coordinate = action_input.get("coordinate", [0, 0])
            x, y = self._remap_coord(int(coordinate[0]), int(coordinate[1]))
            direction = action_input.get("scroll_direction", "down")
            amount = int(action_input.get("scroll_amount", 3))
            if direction == "down":
                pyautogui.scroll(-amount, x=x, y=y)
            elif direction == "up":
                pyautogui.scroll(amount, x=x, y=y)
            elif direction == "left":
                pyautogui.hscroll(-amount, x=x, y=y)
            elif direction == "right":
                pyautogui.hscroll(amount, x=x, y=y)
            time.sleep(0.2)
            return

        if action == "type":
            pyautogui.write(action_input.get("text", ""), interval=0.05)
            time.sleep(0.2)
            return

        if action == "key":
            keys = self._parse_key_string(action_input.get("text", ""))
            if len(keys) == 1:
                pyautogui.press(keys[0])
            elif keys:
                pyautogui.hotkey(*keys)
            time.sleep(0.2)
            return

        if action == "hold_key":
            keys = self._parse_key_string(action_input.get("text", ""))
            duration = float(action_input.get("duration", 1))
            if keys:
                pyautogui.keyDown(keys[0])
                try:
                    time.sleep(duration)
                finally:
                    pyautogui.keyUp(keys[0])
            return

        if action == "wait":
            time.sleep(2)
            return

        raise ValueError(f"Unsupported Claude Computer Use action: {action!r}")

    def act(self, observation: Dict[str, Any]) -> str:
        self.assert_environment_healthy()
        self._validate_display()

        instruction = observation.get("instruction") or self._current_instruction
        self._current_instruction = instruction
        difficulty = observation.get("difficulty_level", "medium")
        max_steps = self.STEP_LIMITS.get(difficulty, 30)
        self.logger.info(
            "Claude CUA difficulty=%s, internal_step_limit=%s",
            difficulty,
            max_steps,
        )

        messages: List[Dict[str, Any]] = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Complete the following task in Adobe Photoshop:\n"
                            f"{instruction}\n\n"
                            "Use the computer tool to interact only with Photoshop. "
                            "Never close Photoshop or the current document. Do not use "
                            "File > Exit, Ctrl+Q, Alt+F4, or a window close button. "
                            "When the requested visible result is complete, stop using "
                            "the computer tool and reply with TASK COMPLETED."
                        ),
                    }
                ],
            }
        ]

        try:
            for internal_step in range(max_steps):
                self.assert_environment_healthy()
                self.logger.info(
                    "Claude CUA internal step %s/%s",
                    internal_step + 1,
                    max_steps,
                )
                response = self.client.beta.messages.create(
                    model=self.model_name,
                    max_tokens=4096,
                    tools=[
                        {
                            "type": self.tool_type,
                            "name": "computer",
                            "display_width_px": self.MODEL_WIDTH,
                            "display_height_px": self.MODEL_HEIGHT,
                        }
                    ],
                    messages=messages,
                    betas=[self.computer_use_beta],
                )
                self.assert_environment_healthy()
                self.logger.info("Claude stop reason: %s", response.stop_reason)
                messages.append({"role": "assistant", "content": response.content})

                tool_use = next(
                    (
                        block
                        for block in response.content
                        if block.type == "tool_use"
                    ),
                    None,
                )
                if tool_use is None or response.stop_reason == "end_turn":
                    self.step_count = internal_step + 1
                    self.update_conversation_history(observation, "DONE")
                    self.logger.info("Claude CUA completed the task.")
                    return "DONE"

                self._execute_cua_action(tool_use.input)
                time.sleep(1)
                screenshot = self._take_screenshot_b64()
                messages.append(
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": tool_use.id,
                                "content": [
                                    {
                                        "type": "image",
                                        "source": {
                                            "type": "base64",
                                            "media_type": "image/png",
                                            "data": screenshot,
                                        },
                                    }
                                ],
                            }
                        ],
                    }
                )
                if len(messages) > 9:
                    messages = messages[:1] + messages[-8:]

            self.step_count = max_steps
            self.update_conversation_history(observation, "FAIL")
            self.logger.warning("Claude CUA reached its internal step limit.")
            return "FAIL"
        except Exception as error:
            if getattr(error, "photoshop_process_crash", False):
                raise
            self.logger.exception("Claude CUA failed: %s", error)
            self.update_conversation_history(observation, "FAIL")
            return "FAIL"


def create_agent() -> ClaudeCUAAgent:
    """Create the only agent included in the Claude-CUA release."""
    return ClaudeCUAAgent()

