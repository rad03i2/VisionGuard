"""
Polygon geofencing and restricted zone intrusion detection.
"""

from dataclasses import dataclass, field
import time
from typing import List, Tuple, Dict, Set, Optional
import cv2
import numpy as np
from visionguard.tracking.tracker import TrackedObject


@dataclass
class IntrusionEvent:
    zone_id: str
    zone_name: str
    track_id: int
    class_name: str
    duration_seconds: float
    timestamp: float
    centroid: Tuple[int, int]
    is_loitering: bool = False


class PolygonZone:
    """
    Arbitrary geometric polygon zone representing restricted areas,
    perimeter boundaries, or security gates.
    """

    def __init__(
        self,
        zone_id: str,
        name: str,
        polygon_points: List[Tuple[int, int]],
        alert_on_classes: Optional[List[str]] = None,
        loitering_time_sec: float = 0.0,
        color_bgr: Tuple[int, int, int] = (0, 0, 255),
    ):
        self.zone_id = zone_id
        self.name = name
        self.polygon = np.array(polygon_points, dtype=np.int32)
        self.alert_on_classes: Optional[Set[str]] = set(alert_on_classes) if alert_on_classes else None
        self.loitering_time_sec = loitering_time_sec
        self.color = color_bgr

        # Track state inside zone: {track_id: enter_timestamp}
        self._occupants: Dict[int, float] = {}

    def contains_point(self, point: Tuple[int, int]) -> bool:
        """Test if a 2D point lies inside the polygon using cv2.pointPolygonTest."""
        dist = cv2.pointPolygonTest(self.polygon, (float(point[0]), float(point[1])), measureDist=False)
        return dist >= 0

    def evaluate(self, tracks: List[TrackedObject]) -> List[IntrusionEvent]:
        """
        Evaluate all active tracked objects against this zone.
        Returns triggered intrusion/loitering events.
        """
        now = time.time()
        events: List[IntrusionEvent] = []
        current_frame_occupants = set()

        for track in tracks:
            # Filter by class if specified
            if self.alert_on_classes and track.class_name not in self.alert_on_classes:
                continue

            # Check if object centroid or bottom-center is inside polygon
            bx1, by1, bx2, by2 = track.bbox
            feet_point = (int((bx1 + bx2) / 2), by2)
            is_inside = self.contains_point(feet_point) or self.contains_point(track.centroid)

            if is_inside:
                current_frame_occupants.add(track.track_id)
                if track.track_id not in self._occupants:
                    self._occupants[track.track_id] = now

                dwell_time = now - self._occupants[track.track_id]
                is_loitering = self.loitering_time_sec > 0 and dwell_time >= self.loitering_time_sec

                # Trigger intrusion or loitering event
                events.append(
                    IntrusionEvent(
                        zone_id=self.zone_id,
                        zone_name=self.name,
                        track_id=track.track_id,
                        class_name=track.class_name,
                        duration_seconds=round(dwell_time, 2),
                        timestamp=now,
                        centroid=track.centroid,
                        is_loitering=is_loitering,
                    )
                )

        # Clean up tracks that left the zone
        left_ids = set(self._occupants.keys()) - current_frame_occupants
        for lid in left_ids:
            del self._occupants[lid]

        return events

    def draw(self, frame: np.ndarray, is_alerting: bool = False, alpha: float = 0.25) -> np.ndarray:
        """Draw transparent alpha-blended polygon overlay onto the frame."""
        overlay = frame.copy()
        draw_color = (0, 0, 255) if is_alerting else self.color

        cv2.fillPoly(overlay, [self.polygon], draw_color)
        cv2.polylines(frame, [self.polygon], isClosed=True, color=draw_color, thickness=2)

        # Blend transparency
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

        # Zone label
        cx = int(np.mean(self.polygon[:, 0]))
        cy = int(np.mean(self.polygon[:, 1]))
        label = f"[ZONE: {self.name}]"
        if is_alerting:
            label += " ! BREACH !"

        cv2.putText(
            frame,
            label,
            (max(10, cx - 80), max(20, cy)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            draw_color,
            2,
        )
        return frame
