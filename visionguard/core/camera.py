"""
Multi-source video ingestion module for RTSP streams, Webcams, video files, and mock generators.
"""

import cv2
import time
import threading
import numpy as np
import logging
from typing import Optional, Tuple, Union

logger = logging.getLogger("visionguard.camera")


class CameraStream:
    """
    Threaded, low-latency video streamer supporting RTSP, HTTP, Webcams, and MP4 files.
    Features automated auto-reconnect logic and thread-safe frame reading.
    """

    def __init__(
        self,
        source: Union[int, str] = 0,
        name: str = "Default Camera",
        reconnect_interval: float = 5.0,
        buffer_size: int = 1,
    ):
        self.source = int(source) if str(source).isdigit() else source
        self.name = name
        self.reconnect_interval = reconnect_interval
        self.buffer_size = buffer_size

        self.cap: Optional[cv2.VideoCapture] = None
        self.frame: Optional[np.ndarray] = None
        self.is_running = False
        self.is_connected = False
        self.fps = 0.0
        self.frame_count = 0

        self._lock = threading.Lock()
        self._thread: Optional[threading.Thread] = None

    def start(self) -> "CameraStream":
        """Start the background ingestion thread."""
        self.is_running = True
        self._connect()
        self._thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._thread.start()
        logger.info(f"Started camera stream [{self.name}] on source: {self.source}")
        return self

    def _connect(self) -> bool:
        """Establish connection with the video source."""
        if self.cap is not None:
            self.cap.release()

        logger.info(f"Connecting to video source [{self.name}]...")
        self.cap = cv2.VideoCapture(self.source)

        if self.cap.isOpened():
            self.is_connected = True
            logger.info(f"Successfully connected to [{self.name}]")
            return True
        else:
            self.is_connected = False
            logger.warning(f"Failed to connect to [{self.name}]")
            return False

    def _capture_loop(self):
        """Continuous background thread pulling frames at max speed to prevent buffer lag."""
        prev_time = time.time()
        frames_in_second = 0

        while self.is_running:
            if not self.is_connected or self.cap is None or not self.cap.isOpened():
                time.sleep(self.reconnect_interval)
                self._connect()
                continue

            ret, frame = self.cap.read()
            if not ret or frame is None:
                # If reading from file and reached EOF, loop or reconnect
                if isinstance(self.source, str) and not self.source.startswith("rtsp"):
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue

                self.is_connected = False
                logger.warning(f"Connection lost on [{self.name}]. Reconnecting in {self.reconnect_interval}s...")
                time.sleep(self.reconnect_interval)
                self._connect()
                continue

            with self._lock:
                self.frame = frame
                self.frame_count += 1

            # Calculate FPS
            frames_in_second += 1
            now = time.time()
            elapsed = now - prev_time
            if elapsed >= 1.0:
                self.fps = frames_in_second / elapsed
                frames_in_second = 0
                prev_time = now

        if self.cap:
            self.cap.release()

    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        """Safely fetch the latest frame."""
        with self._lock:
            if self.frame is None:
                return False, None
            return True, self.frame.copy()

    def stop(self):
        """Stop capture loop and release camera resource."""
        self.is_running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        if self.cap:
            self.cap.release()
        self.is_connected = False
        logger.info(f"Stopped camera stream [{self.name}]")


class MockCameraStream:
    """
    Synthetic CCTV camera stream generator for zero-hardware demos, unit testing,
    and visual validation. Simulates moving surveillance targets and restricted zone scenes.
    """

    def __init__(self, name: str = "Mock Camera 01", width: int = 1280, height: int = 720, fps: int = 30):
        self.name = name
        self.width = width
        self.height = height
        self.target_fps = fps
        self.is_running = False
        self.is_connected = True
        self.frame_count = 0
        self.fps = float(fps)

        # Simulation state
        self._x = 100.0
        self._y = 300.0
        self._vx = 4.0
        self._vy = 1.5

    def start(self) -> "MockCameraStream":
        self.is_running = True
        logger.info(f"Started Mock Camera Stream [{self.name}] ({self.width}x{self.height} @ {self.target_fps}fps)")
        return self

    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        """Generate a realistic synthetic CCTV frame."""
        if not self.is_running:
            return False, None

        self.frame_count += 1
        time.sleep(1.0 / self.target_fps)

        # Create dark CCTV background
        frame = np.full((self.height, self.width, 3), 28, dtype=np.uint8)

        # Add subtle grid lines
        for y in range(0, self.height, 80):
            cv2.line(frame, (0, y), (self.width, y), (40, 40, 40), 1)
        for x in range(0, self.width, 80):
            cv2.line(frame, (x, 0), (x, self.height), (40, 40, 40), 1)

        # Move synthetic target
        self._x += self._vx
        self._y += self._vy

        if self._x > self.width - 200 or self._x < 80:
            self._vx *= -1
        if self._y > self.height - 250 or self._y < 120:
            self._vy *= -1

        # Render simulated human/vehicle entity
        tx, ty = int(self._x), int(self._y)
        cv2.rectangle(frame, (tx, ty), (tx + 90, ty + 180), (60, 160, 60), -1)
        cv2.circle(frame, (tx + 45, ty + 35), 25, (80, 200, 80), -1)

        # CCTV timestamp and telemetry HUD
        timestamp_str = time.strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(frame, f"CAM: {self.name} | LIVE | REC", (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.putText(frame, timestamp_str, (30, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

        return True, frame

    def stop(self):
        self.is_running = False
        logger.info(f"Stopped mock camera [{self.name}]")
