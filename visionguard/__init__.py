"""
VisionGuard: Enterprise AI CCTV Surveillance, Real-time Tracking & Intrusion Detection System
Copyright (c) 2026 rad03i2. All rights reserved.
"""

__version__ = "1.0.0"
__author__ = "rad03i2"

from visionguard.core.camera import CameraStream, MockCameraStream
from visionguard.core.pipeline import VisionPipeline
from visionguard.detection.yolo_detector import YOLODetector
from visionguard.tracking.tracker import SimpleByteTracker
from visionguard.analytics.zones import PolygonZone
from visionguard.alerts.notifier import AlertManager

__all__ = [
    "CameraStream",
    "MockCameraStream",
    "VisionPipeline",
    "YOLODetector",
    "SimpleByteTracker",
    "PolygonZone",
    "AlertManager",
]
