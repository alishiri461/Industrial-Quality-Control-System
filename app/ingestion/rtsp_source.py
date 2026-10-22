from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass
from queue import Empty, Full, Queue
from typing import Any

from app.ingestion.camera_config import CameraConfig

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class FramePacket:
    camera_id: str
    captured_monotonic: float
    frame: Any


@dataclass(frozen=True)
class CameraStatus:
    camera_id: str
    enabled: bool
    connected: bool
    state: str
    reconnect_count: int
    frames_read: int
    last_frame_age_seconds: float | None
    last_error: str | None


class RTSPCameraWorker:
    """One reconnecting reader per camera; queue size one drops stale frames."""

    def __init__(self, config: CameraConfig) -> None:
        self.config = config
        self.frames: Queue[FramePacket] = Queue(maxsize=1)
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._lock = threading.Lock()
        self._connected = False
        self._state = "stopped"
        self._reconnect_count = 0
        self._frames_read = 0
        self._last_frame_at: float | None = None
        self._last_error: str | None = None

    def start(self) -> None:
        if not self.config.enabled:
            self._set_state("disabled")
            return
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(
            target=self._run,
            name=f"rtsp-camera-{self.config.id}",
            daemon=True,
        )
        self._thread.start()

    def stop(self, timeout: float = 3.0) -> None:
        self._stop.set()
        thread = self._thread
        if thread:
            thread.join(timeout=max(0.0, timeout))
        with self._lock:
            if not thread or not thread.is_alive():
                self._connected = False
                self._state = "stopped"
            else:
                self._state = "stopping"
        self._clear_latest_frame()

    def latest_frame(self) -> FramePacket | None:
        try:
            return self.frames.get_nowait()
        except Empty:
            return None

    def status(self) -> CameraStatus:
        with self._lock:
            age = None if self._last_frame_at is None else max(0.0, time.monotonic() - self._last_frame_at)
            return CameraStatus(
                camera_id=self.config.id,
                enabled=self.config.enabled,
                connected=self._connected,
                state=self._state,
                reconnect_count=self._reconnect_count,
                frames_read=self._frames_read,
                last_frame_age_seconds=round(age, 3) if age is not None else None,
                last_error=self._last_error,
            )

    def _set_state(self, state: str, error: str | None = None) -> None:
        with self._lock:
            self._state = state
            self._connected = state == "connected"
            if error:
                # Do not persist/log source URLs: OpenCV errors may contain endpoint details.
                self._last_error = error[:240]

    def _clear_latest_frame(self) -> None:
        while True:
            try:
                self.frames.get_nowait()
            except Empty:
                return

    def _publish(self, packet: FramePacket) -> None:
        try:
            self.frames.put_nowait(packet)
        except Full:
            try:
                self.frames.get_nowait()
            except Empty:
                pass
            try:
                self.frames.put_nowait(packet)
            except Full:
                # Another consumer/producer race is harmless; next frame will replace it.
                pass

    def _run(self) -> None:
        try:
            import cv2
        except ImportError:
            self._set_state("error", "OpenCV is not installed; install the optional 'vision' extra")
            return

        delay = self.config.reconnect_initial_seconds
        while not self._stop.is_set():
            self._set_state("connecting")
            capture = None
            try:
                # OpenCV backend support for timeout properties varies by build/transport.
                capture = cv2.VideoCapture()
                params: list[int] = []
                if hasattr(cv2, "CAP_PROP_OPEN_TIMEOUT_MSEC"):
                    params.extend([cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, self.config.open_timeout_ms])
                if hasattr(cv2, "CAP_PROP_READ_TIMEOUT_MSEC"):
                    params.extend([cv2.CAP_PROP_READ_TIMEOUT_MSEC, self.config.read_timeout_ms])
                url = self.config.source_url.get_secret_value()
                try:
                    if params and hasattr(cv2, "CAP_FFMPEG"):
                        opened = capture.open(url, cv2.CAP_FFMPEG, params)
                    else:
                        opened = capture.open(url)
                except (TypeError, cv2.error):
                    # Some OpenCV builds do not support open-timeout parameters. The fallback
                    # is functional but may not provide bounded read/shutdown latency.
                    capture.release()
                    capture = cv2.VideoCapture(url)
                    opened = capture.isOpened()
                    logger.warning(
                        "OpenCV timeout parameters unsupported; validate shutdown behavior: camera_id=%s",
                        self.config.id,
                    )
                if not opened or not capture.isOpened():
                    raise RuntimeError("Unable to open RTSP stream")
                delay = self.config.reconnect_initial_seconds
                self._set_state("connected")
                logger.info("RTSP camera connected: camera_id=%s", self.config.id)

                while not self._stop.is_set():
                    ok, frame = capture.read()
                    if not ok or frame is None:
                        raise RuntimeError("RTSP frame read failed")
                    now = time.monotonic()
                    with self._lock:
                        self._frames_read += 1
                        self._last_frame_at = now
                        self._last_error = None
                    self._publish(FramePacket(self.config.id, now, frame))
            except Exception as exc:
                if not self._stop.is_set():
                    with self._lock:
                        self._reconnect_count += 1
                    # Error message is deliberately generalized to avoid leaking RTSP credentials.
                    self._set_state("reconnecting", type(exc).__name__)
                    logger.warning(
                        "RTSP camera disconnected; retry scheduled: camera_id=%s error_type=%s",
                        self.config.id,
                        type(exc).__name__,
                    )
            finally:
                if capture is not None:
                    capture.release()
            if self._stop.wait(delay):
                break
            delay = min(delay * 2.0, self.config.reconnect_max_seconds)
        self._set_state("stopped")
