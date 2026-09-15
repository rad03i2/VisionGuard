"""
Multi-Object Tracking (MOT) module with persistent IDs, trajectory history, and speed estimation.
"""

from collections import deque
import time
import math
from typing import List, Dict, Tuple, Optional
import numpy as np
from visionguard.detection.base import Detection


class TrackedObject:
    """Represents an active trackable entity across multiple video frames."""

    def __init__(self, track_id: int, detection: Detection, max_history: int = 64):
        self.track_id = track_id
        self.class_id = detection.class_id
        self.class_name = detection.class_name
        self.bbox = detection.bbox
        self.confidence = detection.confidence

        self.first_seen = time.time()
        self.last_seen = self.first_seen
        self.missed_frames = 0
        self.hits = 1

        # Trajectory history: deque of (x, y, timestamp)
        self.trajectory: deque = deque(maxlen=max_history)
        self.trajectory.append((self.centroid[0], self.centroid[1], self.first_seen))

        # Motion analysis
        self.velocity: Tuple[float, float] = (0.0, 0.0)

    @property
    def centroid(self) -> Tuple[int, int]:
        x1, y1, x2, y2 = self.bbox
        return int((x1 + x2) / 2), int((y1 + y2) / 2)

    @property
    def duration_seconds(self) -> float:
        return self.last_seen - self.first_seen

    def update(self, detection: Detection):
        """Update track with a newly matched detection."""
        now = time.time()
        prev_centroid = self.centroid

        self.bbox = detection.bbox
        self.confidence = detection.confidence
        self.last_seen = now
        self.missed_frames = 0
        self.hits += 1

        new_centroid = self.centroid
        dt = max(0.001, now - self.trajectory[-1][2]) if self.trajectory else 0.033
        vx = (new_centroid[0] - prev_centroid[0]) / dt
        vy = (new_centroid[1] - prev_centroid[1]) / dt
        self.velocity = (vx, vy)

        self.trajectory.append((new_centroid[0], new_centroid[1], now))

    def mark_missed(self):
        self.missed_frames += 1


class SimpleByteTracker:
    """
    High-speed, robust IoU and distance-based Multi-Object Tracker (MOT)
    designed for low-latency CCTV video surveillance.
    """

    def __init__(
        self,
        max_lost_frames: int = 30,
        iou_threshold: float = 0.25,
        max_distance_threshold: float = 120.0,
    ):
        self.max_lost_frames = max_lost_frames
        self.iou_threshold = iou_threshold
        self.max_distance_threshold = max_distance_threshold
        self._next_id = 1
        self.tracks: Dict[int, TrackedObject] = {}

    def update(self, detections: List[Detection]) -> List[TrackedObject]:
        """Update existing tracks with incoming detections and spawn new ones."""
        active_track_ids = list(self.tracks.keys())
        num_tracks = len(active_track_ids)
        num_dets = len(detections)

        matched_tracks = set()
        matched_dets = set()

        # Step 1: Match by IoU
        if num_tracks > 0 and num_dets > 0:
            iou_matrix = np.zeros((num_tracks, num_dets), dtype=float)
            for i, tid in enumerate(active_track_ids):
                track_box = self.tracks[tid].bbox
                for j, det in enumerate(detections):
                    if self.tracks[tid].class_name == det.class_name:
                        iou_matrix[i, j] = self._calculate_iou(track_box, det.bbox)

            while True:
                max_iou = np.max(iou_matrix)
                if max_iou < self.iou_threshold:
                    break

                i, j = np.unravel_index(np.argmax(iou_matrix), iou_matrix.shape)
                tid = active_track_ids[i]

                self.tracks[tid].update(detections[j])
                matched_tracks.add(tid)
                matched_dets.add(j)

                iou_matrix[i, :] = -1.0
                iou_matrix[:, j] = -1.0

        # Step 2: Match remaining unmatched tracks by Centroid Euclidean Distance
        remaining_track_ids = [tid for tid in active_track_ids if tid not in matched_tracks]
        remaining_det_indices = [j for j in range(num_dets) if j not in matched_dets]

        if remaining_track_ids and remaining_det_indices:
            for tid in remaining_track_ids:
                track = self.tracks[tid]
                tc = track.centroid

                best_j = None
                min_dist = float("inf")

                for j in remaining_det_indices:
                    if j in matched_dets:
                        continue
                    det = detections[j]
                    if track.class_name != det.class_name:
                        continue

                    dc = det.centroid
                    dist = math.hypot(tc[0] - dc[0], tc[1] - dc[1])
                    if dist < min_dist and dist <= self.max_distance_threshold:
                        min_dist = dist
                        best_j = j

                if best_j is not None:
                    track.update(detections[best_j])
                    matched_tracks.add(tid)
                    matched_dets.add(best_j)

        # Mark unmatched tracks as missed
        for tid in active_track_ids:
            if tid not in matched_tracks:
                self.tracks[tid].mark_missed()

        # Prune dead tracks
        dead_ids = [
            tid for tid, trk in self.tracks.items() if trk.missed_frames > self.max_lost_frames
        ]
        for tid in dead_ids:
            del self.tracks[tid]

        # Spawn new tracks for unmatched detections
        for j, det in enumerate(detections):
            if j not in matched_dets:
                new_track = TrackedObject(track_id=self._next_id, detection=det)
                self.tracks[self._next_id] = new_track
                self._next_id += 1

        return [t for t in self.tracks.values() if t.missed_frames == 0]

    @staticmethod
    def _calculate_iou(boxA: Tuple[int, int, int, int], boxB: Tuple[int, int, int, int]) -> float:
        """Calculate Intersection over Union (IoU) between two bounding boxes."""
        xA = max(boxA[0], boxB[0])
        yA = max(boxA[1], boxB[1])
        xB = min(boxA[2], boxB[2])
        yB = min(boxA[3], boxB[3])

        inter_width = max(0, xB - xA)
        inter_height = max(0, yB - yA)
        inter_area = inter_width * inter_height

        if inter_area == 0:
            return 0.0

        boxA_area = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
        boxB_area = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])

        iou = inter_area / float(boxA_area + boxB_area - inter_area)
        return float(iou)
