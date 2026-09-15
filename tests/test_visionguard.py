"""
Unit tests for VisionGuard AI Core, Tracker, Analytics, and Pipeline.
Compatible with standard unittest and pytest.
"""

import sys
import os
import unittest
import tempfile
import numpy as np

# Ensure root directory is on python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from visionguard.detection.base import Detection
from visionguard.tracking.tracker import SimpleByteTracker
from visionguard.analytics.zones import PolygonZone
from visionguard.analytics.counting import Tripwire
from visionguard.alerts.storage import SQLiteEventStore
from visionguard.core.pipeline import VisionPipeline


class TestVisionGuard(unittest.TestCase):

    def test_tracker_id_persistence(self):
        """Verify that multi-object tracker maintains track ID across frames."""
        tracker = SimpleByteTracker(iou_threshold=0.3)

        det1 = [Detection(bbox=(100, 100, 150, 150), confidence=0.9, class_id=0, class_name="person")]
        tracks_f1 = tracker.update(det1)
        self.assertEqual(len(tracks_f1), 1)
        tid = tracks_f1[0].track_id

        det2 = [Detection(bbox=(105, 105, 155, 155), confidence=0.88, class_id=0, class_name="person")]
        tracks_f2 = tracker.update(det2)
        self.assertEqual(len(tracks_f2), 1)
        self.assertEqual(tracks_f2[0].track_id, tid)
        self.assertEqual(len(tracks_f2[0].trajectory), 2)

    def test_polygon_zone_intrusion(self):
        """Verify geofencing polygon containment and intrusion alerts."""
        pts = [(100, 100), (300, 100), (300, 300), (100, 300)]
        zone = PolygonZone(zone_id="test_zone", name="Test Perimeter", polygon_points=pts)

        self.assertTrue(zone.contains_point((200, 200)))
        self.assertFalse(zone.contains_point((50, 50)))

        tracker = SimpleByteTracker()
        det = [Detection(bbox=(180, 180, 220, 220), confidence=0.95, class_id=0, class_name="person")]
        tracks = tracker.update(det)

        events = zone.evaluate(tracks)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].zone_id, "test_zone")
        self.assertEqual(events[0].class_name, "person")

    def test_tripwire_crossing(self):
        """Verify virtual tripwire line crossing detection."""
        wire = Tripwire("line1", "Entry Line", pt1=(100, 200), pt2=(300, 200))
        tracker = SimpleByteTracker()

        # Step 1: Object above line (y=180)
        t1 = tracker.update([Detection(bbox=(190, 170, 210, 190), confidence=0.9, class_id=0, class_name="person")])
        wire.update(t1)
        self.assertEqual(wire.total_crossings, 0)

        # Step 2: Object crosses to below line (y=220)
        t2 = tracker.update([Detection(bbox=(190, 210, 210, 230), confidence=0.9, class_id=0, class_name="person")])
        crossings = wire.update(t2)
        self.assertEqual(crossings, 1)
        self.assertEqual(wire.total_crossings, 1)

    def test_sqlite_event_store(self):
        """Verify incident recording and retrieval in SQLite."""
        temp_dir = tempfile.mkdtemp()
        db_file = os.path.join(temp_dir, "test_events.db")
        try:
            store = SQLiteEventStore(db_path=db_file)

            event_id = store.record_event(
                zone_id="z1",
                zone_name="Main Gate",
                track_id=42,
                class_name="person",
                duration_seconds=3.5,
                is_loitering=False,
            )
            self.assertGreater(event_id, 0)

            recent = store.get_recent_events(limit=5)
            self.assertEqual(len(recent), 1)
            self.assertEqual(recent[0]["track_id"], 42)
            self.assertEqual(recent[0]["zone_name"], "Main Gate")
        finally:
            if os.path.exists(db_file):
                try:
                    os.remove(db_file)
                except Exception:
                    pass
            try:
                os.rmdir(temp_dir)
            except Exception:
                pass

    def test_pipeline_execution(self):
        """Verify end-to-end vision pipeline with synthetic frame."""
        pipeline = VisionPipeline()
        dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)

        processed = pipeline.process_frame(dummy_frame)
        self.assertIsNotNone(processed)
        self.assertEqual(processed.shape, dummy_frame.shape)


if __name__ == "__main__":
    unittest.main()
