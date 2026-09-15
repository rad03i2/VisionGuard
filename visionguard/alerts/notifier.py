"""
Multi-channel notification engine (Telegram, Discord/Slack Webhooks, Email, Local Disk).
"""

import os
import time
import logging
from typing import Dict, Any, Optional
import cv2
import numpy as np
import requests
from visionguard.analytics.zones import IntrusionEvent
from visionguard.alerts.storage import SQLiteEventStore

logger = logging.getLogger("visionguard.alerts")


class AlertManager:
    """
    Central alerting coordinator. Formats incident messages, saves snapshot frames,
    enforces cooldown limits, and dispatches via configured channels.
    """

    def __init__(self, config: Dict[str, Any], event_store: Optional[SQLiteEventStore] = None):
        self.config = config.get("alerts", {})
        self.cooldown_sec = self.config.get("cooldown_sec", 10.0)
        self.save_snapshots = self.config.get("save_snapshots", True)
        self.snapshots_dir = self.config.get("snapshots_dir", "snapshots")
        self.event_store = event_store or SQLiteEventStore()

        # Cooldown tracker: {(zone_id, track_id): last_alert_time}
        self._last_alert_times: Dict[tuple, float] = {}

        if self.save_snapshots:
            os.makedirs(self.snapshots_dir, exist_ok=True)

    def process_event(self, event: IntrusionEvent, frame: Optional[np.ndarray] = None):
        """Process and dispatch an intrusion event if cooldown elapsed."""
        now = time.time()
        cooldown_key = (event.zone_id, event.track_id)

        last_time = self._last_alert_times.get(cooldown_key, 0.0)
        if now - last_time < self.cooldown_sec:
            return  # Suppress alert due to active cooldown window

        self._last_alert_times[cooldown_key] = now

        # Save incident snapshot
        snapshot_path = None
        if self.save_snapshots and frame is not None:
            snapshot_path = self._save_frame(frame, event)

        # Log to local database
        self.event_store.record_event(
            zone_id=event.zone_id,
            zone_name=event.zone_name,
            track_id=event.track_id,
            class_name=event.class_name,
            duration_seconds=event.duration_seconds,
            is_loitering=event.is_loitering,
            snapshot_path=snapshot_path,
            timestamp=event.timestamp,
        )

        title = "LOITERING ALERT" if event.is_loitering else "INTRUSION DETECTED"
        message = (
            f"🚨 [VisionGuard Alert] {title}!\n"
            f"• Zone: {event.zone_name} ({event.zone_id})\n"
            f"• Entity: {event.class_name.upper()} (Track ID #{event.track_id})\n"
            f"• Dwell Duration: {event.duration_seconds}s\n"
            f"• Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(event.timestamp))}"
        )

        logger.warning(message)

        # Dispatch integrations
        self._send_telegram(message, snapshot_path)
        self._send_webhook(message, event)

    def _save_frame(self, frame: np.ndarray, event: IntrusionEvent) -> str:
        """Annotate and write incident snapshot frame to disk."""
        annotated = frame.copy()
        ts_str = time.strftime("%Y%m%d_%H%M%S")
        filename = f"breach_{event.zone_id}_track{event.track_id}_{ts_str}.jpg"
        filepath = os.path.join(self.snapshots_dir, filename)

        # Draw red alert banner
        h, w = annotated.shape[:2]
        cv2.rectangle(annotated, (0, 0), (w, 50), (0, 0, 180), -1)
        alert_msg = f"SECURITY ALERT: {event.zone_name} | {event.class_name} #{event.track_id}"
        cv2.putText(annotated, alert_msg, (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        cv2.imwrite(filepath, annotated)
        return filepath

    def _send_telegram(self, message: str, snapshot_path: Optional[str]):
        """Send message and snapshot to Telegram Bot."""
        tg_cfg = self.config.get("telegram", {})
        if not tg_cfg.get("enabled", False):
            return

        bot_token = tg_cfg.get("bot_token")
        chat_id = tg_cfg.get("chat_id")
        if not bot_token or not chat_id or bot_token.startswith("${"):
            return

        try:
            if snapshot_path and os.path.exists(snapshot_path):
                url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
                with open(snapshot_path, "rb") as photo:
                    requests.post(url, data={"chat_id": chat_id, "caption": message}, files={"photo": photo}, timeout=5)
            else:
                url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                requests.post(url, json={"chat_id": chat_id, "text": message}, timeout=5)
        except Exception as e:
            logger.error(f"Failed to deliver Telegram notification: {e}")

    def _send_webhook(self, message: str, event: IntrusionEvent):
        """Send JSON payload to Slack / Discord / Custom webhook."""
        wh_cfg = self.config.get("webhook", {})
        if not wh_cfg.get("enabled", False):
            return

        url = wh_cfg.get("url")
        if not url or url.startswith("${"):
            return

        payload = {
            "source": "VisionGuard",
            "event_type": "security_intrusion",
            "zone_id": event.zone_id,
            "zone_name": event.zone_name,
            "track_id": event.track_id,
            "class_name": event.class_name,
            "duration": event.duration_seconds,
            "timestamp": event.timestamp,
            "text": message,
        }

        try:
            requests.post(url, json=payload, timeout=5)
        except Exception as e:
            logger.error(f"Failed to post to Webhook: {e}")
