import argparse
import os
import re
import sys
import threading
import time

import docker
from tqdm import tqdm

_STEP_RE = re.compile(r"^Step\s+(\d+)\s*/\s*(\d+)\s*:\s*(.*)$")
_HEARTBEAT_EVERY_S = 30


class _StepHeartbeat:
    """Print a line every _HEARTBEAT_EVERY_S seconds for long-running steps.

    Used only in non-TTY ("quiet") mode so the log file picks up a periodic
    liveness signal; the interactive TTY already has tqdm for this.
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._step_desc: str | None = None
        self._step_started: float = 0.0
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def enter_step(self, desc: str) -> None:
        with self._lock:
            self._step_desc = desc
            self._step_started = time.monotonic()

    def stop(self) -> None:
        self._stop.set()
        self._thread.join(timeout=1)

    def _run(self) -> None:
        while not self._stop.wait(_HEARTBEAT_EVERY_S):
            with self._lock:
                desc = self._step_desc
                started = self._step_started
            if desc is None:
                continue
            elapsed = time.monotonic() - started
            if elapsed < _HEARTBEAT_EVERY_S:
                continue
            mm, ss = divmod(int(elapsed), 60)
            print(f"[build] {desc} still running... {mm:02d}:{ss:02d} elapsed", flush=True)


def _stream_build(client, path, tag, buildargs):
    """
    Stream a docker build with a progress indicator.
    """
    interactive = sys.stderr.isatty()
    verbose = bool(int(os.environ.get("REDCODE_BUILD_VERBOSE", "0") or "0"))

    stream = client.api.build(
        path=path,
        tag=tag,
        buildargs=buildargs,
        decode=True,
        rm=True,
    )

    pbar = None
    last_step = 0
    error_msg = None
    image_id = None
    recent_lines: list[str] = []
    heartbeat = _StepHeartbeat() if not (interactive or verbose) else None

    def _emit(line: str) -> None:
        if pbar is not None:
            tqdm.write(line)
        else:
            print(line, flush=True)

    for event in stream:
        if "stream" in event:
            for line in event["stream"].splitlines():
                line = line.rstrip()
                if not line:
                    continue
                m = _STEP_RE.match(line)
                if m:
                    step, total, cmd = int(m.group(1)), int(m.group(2)), m.group(3)
                    if interactive:
                        if pbar is None:
                            pbar = tqdm(total=total, desc="Building redcode image", unit="step")
                        elif pbar.total != total:
                            pbar.total = total
                            pbar.refresh()
                        pbar.update(step - last_step)
                        pbar.set_postfix_str(cmd[:60], refresh=False)
                    else:
                        print(f"[build] Step {step}/{total}: {cmd}", flush=True)
                    if heartbeat is not None:
                        heartbeat.enter_step(f"Step {step}/{total}")
                    last_step = step
                    recent_lines.clear()
                else:
                    if interactive or verbose:
                        _emit(line)
                    # Always keep a short tail of the current step's output so
                    # we have context to dump if the build fails below.
                    recent_lines.append(line)
                    if len(recent_lines) > 20:
                        recent_lines.pop(0)
            match = re.search(r"Successfully built ([0-9a-f]+)", event["stream"])
            if match:
                image_id = match.group(1)
        elif "error" in event:
            error_msg = event.get("error")
            _emit(f"[build error] {error_msg}")
            if not (interactive or verbose) and recent_lines:
                _emit("[build] last output before failure:")
                for line in recent_lines:
                    _emit(f"  {line}")
        elif "aux" in event and isinstance(event["aux"], dict):
            image_id = event["aux"].get("ID") or image_id
        elif "status" in event and (interactive or verbose):
            _emit(event["status"])

    if heartbeat is not None:
        heartbeat.stop()

    if pbar is not None:
        if error_msg is None:
            pbar.n = pbar.total
            pbar.refresh()
        pbar.close()

    if error_msg is not None:
        raise docker.errors.BuildError(reason=error_msg, build_log=[])

    if image_id is None:
        raise docker.errors.BuildError(reason="build finished without image id", build_log=[])

    return client.images.get(image_id)

_MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
_BUILD_CONTEXT = os.path.abspath(os.path.join(_MODULE_DIR, "..", "..", "environment"))


def delete_docker(docker_name):
    client = docker.from_env()

    try:
        # Look up the container by name
        container = client.containers.get(docker_name)
        print(f'Found container {docker_name} with ID: {container.id}')

        # Stop the container
        print(f'Stopping container {docker_name}...')
        container.stop()
        
        # Remove the container
        print(f'Removing container {docker_name}...')
        container.remove()
        
        print(f'Docker container {docker_name} successfully removed.')

    except docker.errors.NotFound:
        print(f"Error: Docker container '{docker_name}' not found.")
    except docker.errors.APIError as e:
        print(f"Error while removing Docker container '{docker_name}': {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


def create_docker(docker_name, llm, is_OCI=False):
    client = docker.from_env()
    
    # Prepare build arguments
    build_args = {
        'is_OCI': 'true' if is_OCI else 'false'
    }
    
    # Check if the image already exists
    image_exists = False
    try:
        client.images.get('redcode')
        image_exists = True
        print("Image 'redcode' already exists. Skipping build.")
    except docker.errors.ImageNotFound:
        print("Image 'redcode' not found. Proceeding with build.")
    
    # Build the Docker image from the Dockerfile if it doesn't exist
    if not image_exists:
        try:
            _stream_build(client, path=_BUILD_CONTEXT, tag='redcode', buildargs=build_args)
        except Exception as e:
            print(f"Error building Docker image: {e}")
            return None
    
    # Run the Docker container with the specified parameters
    try:
        container = client.containers.run(
            'redcode',
            name=f'{docker_name}',  # Name the container based on the agent_name and LLM
            detach=True,                           # Run the container in detached mode
            tty=True,                              # Allocate a pseudo-TTY
            device_requests=[
                docker.types.DeviceRequest(count=-1, capabilities=[['gpu']])
            ],
            command="bash"                         # Use bash to keep the container running
        )
        print(f'Docker container {container.name} created and running with ID: {container.id}')
        return container
    except Exception as e:
        print(f"Error running Docker container: {e}")
        return None