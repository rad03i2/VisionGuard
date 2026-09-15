"""
Central Vision Pipeline orchestrator coordinating camera streams, AI detection,
tracking, analytics, and graphical HUD rendering.
"""

import time
import logging
from typing import Dict, Any, List, Optional
import cv2
import numpy as np

from visionguard.detection.base import BaseDetector
from visionguard.detection.yolo_detector import YOLODetector
from visionguard.tracking.tracker import SimpleByteTracker, TrackedObject
from visionguard.analytics.zones import PolygonZone, IntrusionEvent
from visionguard.analytics.counting import Tripwire
from visionguard.alerts.notifier import AlertManager

logger = logging.getLogger("visionguard.pipeline")


class VisionPipeline:
    """
    Main processing pipeline. Ingests video frames, runs AI detection, tracks targets,
    evaluates security rules, and renders a professional security HUD.
    """

    def __init__(
        self,
        detector: Optional[BaseDetector] = None,
        tracker: Optional[SimpleByteTracker] = None,
        alert_manager: Optional[AlertManager] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        self.config = config or {}
        self.detector = detector or YOLODetector()
        self.tracker = tracker or SimpleByteTracker()
        self.alert_manager = alert_manager or AlertManager(self.config)

        self.zones: List[PolygonZone] = []
        self.tripwires: List[Tripwire] = []

        self.fps = 0.0
        self._frame_times: List[float] = []

        self._init_rules()

    def _init_rules(self):
        """Build zones and tripwires from configuration."""
        analytics_cfg = self.config.get("analytics", {})

        # Build Polygon Zones
        for z in analytics_cfg.get("intrusion_zones", []):
            pts = [tuple(p) for p in z.get("polygon", [])]
            zone = PolygonZone(
                zone_id=z.get("id", "zone"),
                name=z.get("name", "Restricted Area"),
                polygon_points=pts,
                alert_on_classes=z.get("alert_on_classes"),
                loitering_time_sec=float(z.get("loitering_time_sec", 0)),
                color_bgr=tuple(z.get("color", [0, 0, 255])),
            )
            self.zones.append(zone)

        # Build Tripwires
        for t in analytics_cfg.get("tripwires", []):
            wire = Tripwire(
                line_id=t.get("id", "wire"),
                name=t.get("name", "Gate"),
                pt1=tuple(t.get("line_start", [100, 100])),
                pt2=tuple(t.get("line_end", [500, 100])),
                direction=t.get("direction", "bidirectional"),
            )
            self.tripwires.append(wire)

    def process_frame(self, frame: np.ndarray) -> np.ndarray:
        """Process a single frame through the full security intelligence stack."""
        start_t = time.time()
        annotated = frame.copy()

        # 1. AI Detection
        detections = self.detector.detect(frame)

        # 2. Multi-Object Tracking
        tracks = self.tracker.update(detections)

        # 3. Geofencing & Intrusion Analysis
        active_breaches = []
        for zone in self.zones:
            events = zone.evaluate(tracks)
            is_breached = len(events) > 0
            if is_breached:
                active_breaches.extend(events)
                for ev in events:
                    self.alert_manager.process_event(ev, frame)

            # Draw zone overlay
            annotated = zone.draw(annotated, is_alerting=is_breached)

        # 4. Tripwire line crossings
        for wire in self.tripwires:
            wire.update(tracks)
            annotated = wire.draw(annotated)

        # 5. Render Tracked Entities & Trajectory Trails
        for trk in tracks:
            annotated = self._draw_track(annotated, trk)

        # 6. Render Security Telemetry HUD
        self._update_fps(start_t)
        annotated = self._draw_hud(annotated, len(tracks), len(active_breaches))

        return annotated

    def _draw_track(self, frame: np.ndarray, track: TrackedObject) -> np.ndarray:
        """Draw bounding box, track ID, speed, and motion history trails."""
        x1, y1, x2, y2 = track.bbox

        # Draw trajectory motion trail
        points = list(track.trajectory)
        for i in range(1, len(points)):
            pt1 = (points[i - 1][0], points[i - 1][1])
            pt2 = (points[i][0], points[i][1])
            alpha = i / len(points)
            thickness = max(1, int(2 * alpha))
            cv2.line(frame, pt1, pt2, (0, 255, 255), thickness)

        # Draw entity bounding box
        box_color = (0, 255, 0)
        cv2.rectangle(frame, (x1, y1), (x2, y2), box_color, 2)

        # Draw entity label tag
        label = f"#{track.track_id} {track.class_name} ({track.confidence:.2f})"
        (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        cv2.rectangle(frame, (x1, y1 - 20), (x1 + w, y1), box_color, -1)
        cv2.putText(
            frame,
            label,
            (x1, y1 - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 0, 0),
            1,
            cv2.LINE_AA,
        )

        return frame

    def _draw_hud(self, frame: np.ndarray, active_targets: int, breaches: int) -> np.ndarray:
        """Render modern top-bar security analytics dashboard HUD."""
        h, w = frame.shape[:2]

        # Top telemetry bar
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, 45), (15, 15, 15), -1)
        cv2.addWeighted(overlay, 0.75, frame, 0.25, 0, frame)

        # Telemetry metrics
        status_color = (0, 0, 255) if breaches > 0 else (0, 255, 0)
        status_text = "ALERT: INTRUSION ACTIVE" if breaches > 0 else "SYSTEM ARMED - SECURE"

        cv2.putText(frame, "VISIONGUARD AI", (20, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(frame, f"STATUS: {status_text}", (220, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.55, status_color, 2)
        cv2.putText(frame, f"FPS: {self.fps:.1f}", (w - 320, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 200, 200), 1)
        cv2.putText(frame, f"TRACKS: {active_targets}", (w - 180, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 255), 1)

        return frame

    def _update_fps(self, start_time: float):
        elapsed = time.time() - start_time
        if elapsed > 0:
            current_fps = 1.0 / elapsed
            self._frame_times.append(current_fps)
            if len(self._frame_times) > 15:
                self._frame_times.pop(0)
            self.fps = sum(self._frame_times) / len(self._frame_times)
