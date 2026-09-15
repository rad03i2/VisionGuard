"""
FastAPI web server & live CCTV surveillance monitoring dashboard.
"""

import time
from typing import Generator
import cv2
from fastapi import FastAPI, Response
from fastapi.responses import StreamingResponse, HTMLResponse
import uvicorn

from visionguard.core.camera import MockCameraStream, CameraStream
from visionguard.core.pipeline import VisionPipeline
from visionguard.alerts.storage import SQLiteEventStore

app = FastAPI(
    title="VisionGuard AI Surveillance API",
    description="Real-time multi-camera intelligent tracking and intrusion analytics",
    version="1.0.0",
)

# Global instances initialized on startup
camera_stream = None
pipeline = None
event_store = SQLiteEventStore()


def init_runtime(source=None, config=None):
    global camera_stream, pipeline
    if source == "mock" or source is None:
        camera_stream = MockCameraStream(name="HQ Main Gate").start()
    else:
        camera_stream = CameraStream(source=source, name="Primary Feed").start()

    pipeline = VisionPipeline(config=config)


def generate_frames() -> Generator[bytes, None, None]:
    """Yield MJPEG stream frames with real-time AI overlays."""
    while True:
        if camera_stream is None or pipeline is None:
            time.sleep(0.1)
            continue

        ret, frame = camera_stream.read()
        if not ret or frame is None:
            time.sleep(0.03)
            continue

        processed = pipeline.process_frame(frame)
        ret, buffer = cv2.imencode(".jpg", processed, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
        if not ret:
            continue

        frame_bytes = buffer.tobytes()
        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
        )


@app.get("/video_feed")
def video_feed():
    """Live MJPEG video stream endpoint with real-time AI computer vision overlays."""
    return StreamingResponse(
        generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


@app.get("/api/status")
def get_status():
    """System health, streaming FPS, and active security status."""
    return {
        "status": "online",
        "fps": round(pipeline.fps if pipeline else 0.0, 1),
        "camera_connected": camera_stream.is_connected if camera_stream else False,
        "active_zones": len(pipeline.zones) if pipeline else 0,
        "timestamp": time.time(),
    }


@app.get("/api/alerts")
def get_alerts(limit: int = 20):
    """Fetch recent intrusion events and security breaches."""
    return event_store.get_recent_events(limit=limit)


@app.get("/", response_class=HTMLResponse)
def index():
    """Enterprise Dark-Mode Surveillance Dashboard UI."""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>VisionGuard AI · Enterprise Surveillance</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
        <style>
            :root {
                --bg-main: #0B0F19;
                --bg-card: #151D2F;
                --bg-card-hover: #1E293B;
                --border-color: #2D3748;
                --text-primary: #F8FAFC;
                --text-secondary: #94A3B8;
                --accent-blue: #3B82F6;
                --accent-green: #10B981;
                --accent-red: #EF4444;
            }
            * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', sans-serif; }
            body { background: var(--bg-main); color: var(--text-primary); padding: 24px; min-height: 100vh; }
            .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; padding-bottom: 16px; border-bottom: 1px solid var(--border-color); }
            .title { display: flex; align-items: center; gap: 12px; font-size: 22px; font-weight: 700; letter-spacing: -0.5px; }
            .badge-live { background: rgba(239, 68, 68, 0.2); color: var(--accent-red); border: 1px solid var(--accent-red); padding: 4px 10px; border-radius: 9999px; font-size: 12px; font-weight: 600; animation: pulse 2s infinite; }
            @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
            .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 24px; }
            .stat-card { background: var(--bg-card); border: 1px solid var(--border-color); padding: 18px; border-radius: 12px; }
            .stat-label { color: var(--text-secondary); font-size: 13px; margin-bottom: 6px; }
            .stat-val { font-size: 26px; font-weight: 700; color: var(--text-primary); }
            .content-grid { display: grid; grid-template-columns: 2fr 1fr; gap: 24px; }
            .video-container { background: #000; border-radius: 14px; overflow: hidden; border: 1px solid var(--border-color); position: relative; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5); }
            .video-feed { width: 100%; height: auto; display: block; }
            .alerts-panel { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 14px; padding: 20px; display: flex; flex-direction: column; max-height: 600px; }
            .alerts-title { font-size: 16px; font-weight: 600; margin-bottom: 16px; display: flex; justify-content: space-between; align-items: center; }
            .alert-list { overflow-y: auto; display: flex; flex-direction: column; gap: 10px; }
            .alert-item { background: rgba(239, 68, 68, 0.08); border-left: 4px solid var(--accent-red); padding: 12px; border-radius: 6px; font-size: 13px; }
            .alert-item-time { color: var(--text-secondary); font-size: 11px; margin-top: 4px; }
            @media (max-width: 968px) { .content-grid { grid-template-columns: 1fr; } }
        </style>
    </head>
    <body>
        <div class="header">
            <div class="title">
                <span>🛡️ VisionGuard AI</span>
                <span class="badge-live">● LIVE FEED</span>
            </div>
            <div>
                <span style="color: var(--text-secondary); font-size: 14px;">Next-Gen CCTV Tracking Engine</span>
            </div>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">SYSTEM STATUS</div>
                <div class="stat-val" style="color: var(--accent-green)">ARMED</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">STREAM PERFORMANCE</div>
                <div class="stat-val" id="fps-val">30.0 FPS</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">RESTRICTED ZONES</div>
                <div class="stat-val">ACTIVE</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">AI TRACKER</div>
                <div class="stat-val" style="color: var(--accent-blue)">ByteTrack</div>
            </div>
        </div>

        <div class="content-grid">
            <div class="video-container">
                <img class="video-feed" src="/video_feed" alt="VisionGuard Surveillance Live Feed">
            </div>

            <div class="alerts-panel">
                <div class="alerts-title">
                    <span>🚨 Real-Time Security Breaches</span>
                    <span style="font-size: 11px; color: var(--text-secondary);">Auto-Refreshing</span>
                </div>
                <div class="alert-list" id="alert-list">
                    <div class="alert-item">
                        <strong>Perimeter Monitor Active</strong>
                        <div class="alert-item-time">Monitoring entrance and restricted polygon boundaries...</div>
                    </div>
                </div>
            </div>
        </div>

        <script>
            async function fetchAlerts() {
                try {
                    const res = await fetch('/api/alerts?limit=10');
                    const alerts = await res.json();
                    if (alerts.length > 0) {
                        const list = document.getElementById('alert-list');
                        list.innerHTML = alerts.map(a => `
                            <div class="alert-item">
                                <strong>⚠️ ${a.zone_name}: ${a.class_name.toUpperCase()} (ID #${a.track_id})</strong>
                                <div>Dwell: ${a.duration_seconds}s ${a.is_loitering ? '· [Loitering Detected]' : ''}</div>
                                <div class="alert-item-time">${a.created_at || new Date(a.timestamp*1000).toLocaleTimeString()}</div>
                            </div>
                        `).join('');
                    }
                } catch (e) {
                    console.error(e);
                }
            }
            setInterval(fetchAlerts, 2500);
        </script>
    </body>
    </html>
    """


def run(host: str = "0.0.0.0", port: int = 8000, source: str = "mock"):
    """Entrypoint to launch web server."""
    init_runtime(source=source)
    uvicorn.run(app, host=host, port=port)
