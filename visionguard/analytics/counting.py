"""
Tripwire virtual lines for counting entries, exits, and bidirectional crossings.
"""

from typing import Tuple, List, Dict, Set
import cv2
import numpy as np
from visionguard.tracking.tracker import TrackedObject


class Tripwire:
    """
    Virtual tripwire line segment that counts moving entities crossing in specific directions.
    """

    def __init__(
        self,
        line_id: str,
        name: str,
        pt1: Tuple[int, int],
        pt2: Tuple[int, int],
        direction: str = "bidirectional",  # "in", "out", or "bidirectional"
        color_bgr: Tuple[int, int, int] = (255, 255, 0),
    ):
        self.line_id = line_id
        self.name = name
        self.pt1 = pt1
        self.pt2 = pt2
        self.direction = direction
        self.color = color_bgr

        self.in_count = 0
        self.out_count = 0
        self.total_crossings = 0
        self._crossed_tracks: Set[int] = set()

    def update(self, tracks: List[TrackedObject]) -> int:
        """
        Check track trajectories against the line segment.
        Returns count of new crossings in this frame.
        """
        new_crossings = 0

        for track in tracks:
            if track.track_id in self._crossed_tracks:
                continue

            if len(track.trajectory) < 2:
                continue

            # Check if line between last two centroid positions intersects tripwire
            prev_pt = (track.trajectory[-2][0], track.trajectory[-2][1])
            curr_pt = (track.trajectory[-1][0], track.trajectory[-1][1])

            if self._intersect(self.pt1, self.pt2, prev_pt, curr_pt):
                self._crossed_tracks.add(track.track_id)
                self.total_crossings += 1
                new_crossings += 1

                # Calculate side of line to determine IN vs OUT direction
                v_line = (self.pt2[0] - self.pt1[0], self.pt2[1] - self.pt1[1])
                v_move = (curr_pt[0] - prev_pt[0], curr_pt[1] - prev_pt[1])
                cross_product = v_line[0] * v_move[1] - v_line[1] * v_move[0]

                if cross_product > 0:
                    self.in_count += 1
                else:
                    self.out_count += 1

        return new_crossings

    def draw(self, frame: np.ndarray) -> np.ndarray:
        """Render tripwire and counter stats onto the frame."""
        cv2.line(frame, self.pt1, self.pt2, self.color, 3)
        mid_x = int((self.pt1[0] + self.pt2[0]) / 2)
        mid_y = int((self.pt1[1] + self.pt2[1]) / 2)

        stats_text = f"{self.name}: IN={self.in_count} | OUT={self.out_count}"
        cv2.putText(
            frame,
            stats_text,
            (mid_x - 60, mid_y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            self.color,
            2,
        )
        return frame

    @staticmethod
    def _ccw(A: Tuple[int, int], B: Tuple[int, int], C: Tuple[int, int]) -> bool:
        return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])

    def _intersect(
        self,
        A: Tuple[int, int],
        B: Tuple[int, int],
        C: Tuple[int, int],
        D: Tuple[int, int],
    ) -> bool:
        """Return True if line segments AB and CD intersect."""
        return (self._ccw(A, C, D) != self._ccw(B, C, D)) and (self._ccw(A, B, C) != self._ccw(A, B, D))
