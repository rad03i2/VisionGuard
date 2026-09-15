"""
VisionGuard Command Line Interface (CLI).
"""

import argparse
import sys
import yaml
import logging
import cv2

from visionguard.core.camera import CameraStream, MockCameraStream
from visionguard.core.pipeline import VisionPipeline
from visionguard.web import app as web_app

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("visionguard.cli")


def load_config(config_path: str) -> dict:
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        logger.warning(f"Could not load config file ({e}). Using default settings.")
        return {}


def main():
    parser = argparse.ArgumentParser(
        description="VisionGuard AI: Smart CCTV Tracking & Surveillance Platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--source",
        type=str,
        default="mock",
        help="Video source: RTSP URL ('rtsp://...'), webcam index ('0'), or 'mock' for simulation",
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config/settings.yaml",
        help="Path to YAML configuration file",
    )
    parser.add_argument(
        "--web",
        action="store_true",
        help="Launch the modern FastAPI web dashboard and MJPEG stream",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host for web dashboard server (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for web dashboard server (default: 8000)",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run without local GUI OpenCV window (recommended for servers/docker)",
    )

    args = parser.parse_args()
    config = load_config(args.config)

    logger.info("Initializing VisionGuard AI Enterprise Surveillance...")

    if args.web:
        logger.info(f"Starting web dashboard on http://{args.host}:{args.port}")
        web_app.run(host=args.host, port=args.port, source=args.source)
        return

    # Terminal / OpenCV Window mode
    if args.source == "mock":
        camera = MockCameraStream(name="HQ Entrance Simulator").start()
    else:
        camera = CameraStream(source=args.source, name="CCTV Stream").start()

    pipeline = VisionPipeline(config=config)

    logger.info("Surveillance pipeline running. Press 'q' to exit.")

    try:
        while True:
            ret, frame = camera.read()
            if not ret or frame is None:
                continue

            annotated = pipeline.process_frame(frame)

            if not args.headless:
                cv2.imshow("VisionGuard AI - Security Monitor", annotated)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
    except KeyboardInterrupt:
        logger.info("Shutting down VisionGuard gracefully...")
    finally:
        camera.stop()
        if not args.headless:
            cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
