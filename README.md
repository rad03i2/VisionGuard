<div align="center">

# 🛡️ VisionGuard AI
### Enterprise Intelligent CCTV Surveillance, Multi-Camera Tracking & Perimeter Intrusion Detection System
#### نظام المراقبة الذكي بالذكاء الاصطناعي لتتبع الكاميرات واكتشاف التهديدات اللحظي

[![Python Version](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![YOLOv8 / YOLOv11](https://img.shields.io/badge/AI%20Engine-YOLOv8%20%2F%20YOLOv11-00FFFF?style=for-the-badge&logo=yolo&logoColor=black)](https://ultralytics.com)
[![OpenCV](https://img.shields.io/badge/OpenCV-5.0+-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)](https://opencv.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Modern%20Dashboard-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Docker Ready](https://img.shields.io/badge/Docker-Containerized-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

<br/>

[English Documentation](#-english-overview) • [التوثيق باللغة العربية](#-نظرة-عامة-باللغة-العربية) • [Quick Start](#-quick-start) • [Architecture](#-system-architecture) • [Commercial Solutions](#-commercial-inquiries--custom-solutions)

</div>

---

## 🌟 Highlights

Traditional CCTV systems are purely reactive—recording incidents after the damage has already occurred. **VisionGuard AI** transforms passive IP cameras and RTSP streams into an **autonomous real-time intelligence network**. It tracks moving subjects with persistent IDs, enforces geometric restricted zones, detects unauthorized loitering, and dispatches instant visual alarms across enterprise channels.

---

## 🚀 Key Features

| Capability | Description |
| :--- | :--- |
| 📹 **Multi-Source Streaming** | Ingests RTSP streams, ONVIF cameras, USB webcams, and MP4 files with automatic thread-level reconnect. |
| 🧠 **State-of-the-Art Detection** | Powered by Ultralytics YOLOv8 / YOLOv11 with GPU CUDA acceleration and CPU fallback. |
| 🎯 **ByteTrack Multi-Object Tracking** | Assigns persistent tracking IDs, draws dynamic motion trails, and calculates target velocity vectors. |
| 🛑 **Polygon Geofencing** | Define arbitrary polygon perimeters for restricted areas, server rooms, and warehouse bays. |
| ⏳ **Anti-Loitering Detection** | Monitors dwell time; alerts security when an entity remains in a sensitive area beyond a threshold. |
| 🚶 **Tripwire Directional Counting** | Virtual optical tripwires track directional pedestrian and vehicle flow (`IN` / `OUT`). |
| 🚨 **Multi-Channel Alerting** | Instant push alerts via **Telegram Bot** (with snapshot photos), **Webhooks** (Slack/Discord), and Email. |
| 📊 **Modern Web Dashboard** | Low-latency MJPEG live stream player, real-time alert logs, and telemetry counters. |
| 🗄️ **Persistent Event Store** | Local SQLite incident auditing database with timestamped snapshot capture. |
| 🐳 **Docker & Production Ready** | Packaged with `Dockerfile` and `docker-compose.yml` for zero-friction cloud/edge deployment. |

---

## 🏛️ System Architecture

```text
       [ RTSP Streams / IP Cameras / Webcams ]
                          │
                          ▼
            ┌───────────────────────────┐
            │  Threaded Camera Ingest   │  ◄── Auto-Reconnect & Frame Buffering
            └─────────────┬─────────────┘
                          │
                          ▼
            ┌───────────────────────────┐
            │   AI Detection Engine     │  ◄── YOLOv8 / YOLOv11 Deep Learning
            └─────────────┬─────────────┘
                          │
                          ▼
            ┌───────────────────────────┐
            │    ByteTrack MOT Engine   │  ◄── Persistent IDs & Trajectory History
            └─────────────┬─────────────┘
                          │
            ┌─────────────┴─────────────┐
            ▼                           ▼
 ┌─────────────────────┐     ┌─────────────────────┐
 │ Polygon Geofencing  │     │ Tripwire Directional│
 │ & Loitering Check   │     │ Line Crossing Count │
 └──────────┬──────────┘     └──────────┬──────────┘
            │                           │
            └─────────────┬─────────────┘
                          │
                          ▼
 ┌────────────────────────────────────────────────────────┐
 │                   Dispatch & Output                    │
 ├─────────────────────────┬──────────────────────────────┤
 │  🚨 Instant Alerts      │  🌐 Web Dashboard & API      │
 │  • Telegram (Snapshots) │  • Real-Time Video Feed      │
 │  • Webhooks / Slack     │  • SQLite Incident Logs      │
 │  • Local Snapshots      │  • Telemetry Status (FPS)    │
 └─────────────────────────┴──────────────────────────────┘
```

---

## ⚡ Quick Start

### 1. Clone & Install
```bash
git clone https://github.com/rad03i2/VisionGuard.git
cd VisionGuard

# Install dependencies
pip install -r requirements.txt
```

### 2. Launch Web Dashboard (Simulation / Demo Mode)
You can run VisionGuard immediately without physical cameras using the built-in synthetic CCTV simulator:
```bash
python -m visionguard.cli --web
```
Open **`http://localhost:8000`** in your browser to view the real-time dark-mode security operations center.

### 3. Connect to a Real RTSP Camera or Webcam
```bash
# Connect to your local USB webcam:
python -m visionguard.cli --source 0 --web

# Connect to an IP Camera RTSP feed:
python -m visionguard.cli --source "rtsp://admin:password@192.168.1.100:554/stream1" --web
```

### 4. Deploy with Docker Compose
```bash
docker-compose up -d --build
```

---

## ⚙️ Configuration (`config/settings.yaml`)

Customizing cameras, detection classes, and restricted zones is done via YAML:

```yaml
cameras:
  - id: "cam-main-entrance"
    name: "Main Facility Gate"
    source: "rtsp://admin:pass@192.168.1.50:554/h264Preview_01_main"
    fps: 30

detection:
  model_path: "yolov8n.pt"
  confidence_threshold: 0.45
  target_classes: [0, 2, 7] # person, car, truck

analytics:
  intrusion_zones:
    - id: "vault_perimeter"
      name: "Restricted Vault Zone"
      polygon:
        - [200, 150]
        - [600, 150]
        - [650, 480]
        - [150, 480]
      loitering_time_sec: 5 # Alert if stationary > 5s
```

---

## 📡 REST API & Streaming Endpoints

| Endpoint | Method | Description |
| :--- | :---: | :--- |
| `/` | `GET` | Responsive dark-mode live surveillance control room |
| `/video_feed` | `GET` | Low-latency MJPEG video stream with real-time AI bounding boxes & HUD |
| `/api/status` | `GET` | Telemetry endpoint (FPS, camera health, active zones) |
| `/api/alerts` | `GET` | Audit log of security intrusions and breach incidents |

---

## 🇸🇦 نظرة عامة باللغة العربية

### ما هو نظام VisionGuard AI؟
**VisionGuard AI** هو نظام ذكي متكامل مصمم لتحويل كاميرات المراقبة التقليدية (CCTV / RTSP) إلى منظومة مراقبة وأمان ذاتية التشغيل مدعومة بأحدث خوارزميات الرؤية الحاسوبية والذكاء الاصطناعي.

### أبرز القدرات والمميزات:
1. **التعرف والتتبع اللحظي (Multi-Object Tracking)**:
   - تحديد الأشخاص، المركبات، والآليات بدقة فائقة مع منح كل كائن معرفاً رقمياً ثابتاً (`ID`) ورسم مسار حركته الحية.
2. **سياج أمني جغرافي للمناطق المحظورة (Polygon Geofencing)**:
   - إمكانية رسم مناطق مخصصة متعددة الأضلاع لحماية المستودعات، غرف الخوادم، أو بوابات المنشأة.
3. **كشف التسكع والاشتباه (Anti-Loitering Detection)**:
   - رصد الأشخاص الذين يتواجدون داخل المنطقة المحظورة لفترة أطول من الوقت المسموح به وإطلاق إنذار فوري.
4. **عدادات افتراضية ذكية (Tripwires)**:
   - إحصاء دقيق لحركة الدخول والخروج للمشاة والسيارات لمراقبة حركة المرور والمنشآت.
5. **تنبيهات أمنية فورية متعددة القنوات**:
   - إرسال إشعارات لحظية مع صور التسلل عبر تطبيق **Telegram**، بالإضافة إلى أنظمة **Webhooks** للربط مع Slack أو برامج إدارة المنشآت.
6. **لوحة تحكم تفاعلية متطورة**:
   - واجهة مستخدم مبنية بـ FastAPI وبث مباشر فوري (MJPEG) مع عرض حي لسجلات الاختراق وأداء الكاميرات.

---

## 💼 Commercial Inquiries & Custom Solutions
### استفسارات التعاقد وتطوير الحلول المخصصة للشركات والمنشآت

Are you looking to deploy an enterprise AI surveillance solution, enhance your security infrastructure, or develop customized computer vision software for your company?

هل تبحث عن حلول ذكاء اصطناعي ورؤية حاسوبية مخصصة لمنشأتك أو شركتك لرفع كفاءة الأمان والمراقبة؟

#### Specialized Services Offered / الخدمات المتوفرة:
- 🏢 **Custom Model Fine-Tuning**: Training custom YOLO models for industry-specific objects (PPE safety gear, helmets, license plates, industrial defects).
- 🏷️ **ANPR / LPR Systems**: Automatic Number Plate Recognition for parking gates and vehicle checkpoints.
- ⚡ **Edge AI Optimization**: Compiling models for NVIDIA Jetson, TensorRT, Intel OpenVINO, and low-power embedded hardware.
- 📱 **Custom Cloud & Mobile Integrations**: Native iOS/Android alert apps, cloud recording backends, and WhatsApp/SMS emergency alerts.

📩 **Get in Touch / تواصل معي مباشرة:**
- **GitHub Profile**: [@rad03i2](https://github.com/rad03i2)
- **Email**: Contact through GitHub profile
- **Freelance & Consulting**: Open for contract and enterprise projects.

---

## 🧪 Testing

Run the automated test suite:
```bash
python -m unittest tests/test_visionguard.py
# or using pytest
pytest -v tests/
```

---

## 📄 License
This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

<div align="center">
Developed with ❤️ by <a href="https://github.com/rad03i2">rad03i2</a>
</div>
