# VisionGuard

A local-first Python computer-vision toolkit for camera/video ingestion, object detection, tracking, zone analytics, alerts, incident storage, and a FastAPI monitoring dashboard.

> VisionGuard is a developer-oriented project, not a certified physical-security product. Detection quality depends on the model, camera placement, lighting, hardware, and configuration.

## English

### Overview
VisionGuard connects OpenCV-readable video sources to an Ultralytics YOLO detector, tracking and zone-analysis components, alert/storage helpers, and a web dashboard. It exists as a practical foundation for experimenting with privacy-conscious local video analytics without requiring a hosted AI API.

### Key features
- Camera/video ingestion through OpenCV, including webcams, files, and compatible network streams.
- Ultralytics YOLO object detection with configurable confidence/classes.
- Multi-object tracking and trajectory state.
- Polygon zone and dwell/loitering analysis.
- Directional counting utilities.
- Local incident/event persistence and snapshot support.
- Alert integrations implemented by the notifier module.
- FastAPI dashboard/API with MJPEG streaming support.
- YAML configuration, CLI entry point, Docker assets, and automated tests.

### Requirements
- Python 3.10–3.12
- A camera, video file, or network stream for real input
- CPU is supported by the underlying libraries; GPU acceleration depends on your PyTorch/Ultralytics environment

### Installation
```bash
git clone https://github.com/rad03i2/VisionGuard.git
cd VisionGuard
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
```

Editable package installation is also supported:
```bash
pip install -e .
visionguard --help
```

### Usage
Inspect the CLI before connecting a source:
```bash
python -m visionguard.cli --help
```

Run with a webcam and web mode:
```bash
python -m visionguard.cli --source 0 --web
```

Run with an OpenCV-compatible stream:
```bash
python -m visionguard.cli --source "rtsp://USER:PASSWORD@camera.example/stream" --web
```
Never commit a real camera URL containing credentials.

### Configuration
The example/default configuration lives at `config/settings.yaml`. Review camera sources, detection thresholds/classes, analytics zones, storage, and notification settings before deployment. Keep secrets out of committed YAML; prefer environment variables or a secret manager for real deployments.

### Web preview
When web mode is enabled, open the address printed by the application (commonly `http://localhost:8000`). The FastAPI application exposes the dashboard and project API/stream routes implemented in `visionguard/web/app.py`. For remote access, put it behind authentication and TLS rather than exposing the development server directly.

### Project structure
```text
visionguard/
  core/          camera ingestion and processing pipeline
  detection/     detector interfaces and YOLO implementation
  tracking/      object tracking
  analytics/     zones and counting
  alerts/        notification and event storage
  web/           FastAPI dashboard/API
config/           YAML configuration
demo/             sample-data helper
tests/            automated tests
```

### Testing
```bash
python -m unittest tests/test_visionguard.py
```
The GitHub Actions workflow also performs automated validation. A local pass is recommended before every contribution.

### Docker
```bash
docker compose up --build
```
Camera/device passthrough and GPU acceleration are host-specific; adjust Compose/runtime settings for your hardware instead of assuming they are automatically available.

### Security & privacy
Video analytics can process sensitive personal information. Use VisionGuard only where you have authorization, minimize retention, protect network streams and credentials, and follow applicable privacy/surveillance law. See [SECURITY.md](SECURITY.md) for deployment guidance. Do not expose the dashboard or camera streams to untrusted networks without access control and TLS.

### Limitations
- Detection and tracking are probabilistic and can miss or misclassify objects.
- This repository does not provide a guarantee of threat detection or safety.
- RTSP/codec behavior depends on the OpenCV/FFmpeg build and camera implementation.
- GPU support is environment-specific.
- Network-facing deployment needs authentication, TLS, monitoring, and hardening supplied by the operator.
- Notification integrations require their respective external service configuration.

### Optional roadmap
Possible future improvements include stronger dashboard authentication, richer integration tests with generated media, configurable retention policies, and documented hardware-specific acceleration profiles.

### Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md). Contributions should include tests where practical and must never include private footage or credentials.

### License
MIT License. See [LICENSE](LICENSE).

### Author
**Radwan Abdulhadi Ahmed**  
**رضوان عبدالهادي أحمد**  
GitHub: **@rad03i2**

---

## العربية

### نظرة عامة
VisionGuard هو مشروع Python محلي لمعالجة مصادر الفيديو والكاميرات عبر OpenCV وربطها بكشف الأجسام باستخدام Ultralytics YOLO، ثم التتبع وتحليل المناطق والتنبيهات وتخزين الأحداث ولوحة مراقبة مبنية بـ FastAPI. الهدف هو توفير أساس عملي لتجارب تحليل الفيديو محليًا من دون اشتراط خدمة ذكاء اصطناعي سحابية.

> المشروع أداة للمطورين وليس نظام أمان ماديًا معتمدًا، ودقة النتائج تتأثر بالنموذج والإضاءة وموقع الكاميرا والعتاد والإعدادات.

### الميزات الرئيسية
- قراءة كاميرات الويب وملفات الفيديو ومصادر الشبكة المتوافقة مع OpenCV.
- كشف الأجسام بنماذج YOLO مع ضبط الثقة والفئات.
- تتبع الأجسام والاحتفاظ بحالة المسار.
- تحليل مناطق متعددة الأضلاع ومدة البقاء داخلها.
- أدوات عدّ اتجاهي للحركة.
- تخزين محلي للأحداث ودعم اللقطات.
- مكونات للتنبيهات حسب الإعدادات المتاحة.
- لوحة/API عبر FastAPI مع دعم بث MJPEG.
- إعداد YAML وواجهة أوامر وDocker واختبارات آلية.

### المتطلبات والتثبيت
يتطلب Python 3.10–3.12 ومصدر فيديو مناسبًا.
```bash
git clone https://github.com/rad03i2/VisionGuard.git
cd VisionGuard
python -m venv .venv
pip install -r requirements.txt
```
ويمكن تثبيت الحزمة للتطوير:
```bash
pip install -e .
visionguard --help
```

### الاستخدام
```bash
python -m visionguard.cli --help
python -m visionguard.cli --source 0 --web
```
ولمصدر شبكة متوافق:
```bash
python -m visionguard.cli --source "rtsp://USER:PASSWORD@camera.example/stream" --web
```
لا تضع رابط كاميرا حقيقيًا يحوي اسم مستخدم أو كلمة مرور داخل GitHub.

### الإعداد
الملف `config/settings.yaml` يحتوي إعدادات المشروع. راجع المصادر وحدود الكشف والفئات والمناطق والتحليلات والتخزين والتنبيهات قبل التشغيل. لا تحفظ الأسرار الحقيقية داخل ملف YAML المرفوع للمستودع.

### المعاينة
عند تشغيل وضع الويب افتح العنوان الذي يطبعه التطبيق، وغالبًا يكون محليًا على المنفذ 8000. عند الوصول من شبكة أخرى استخدم مصادقة وTLS وreverse proxy مناسبًا بدل تعريض خادم التطوير مباشرة.

### بنية المشروع
المجلد `visionguard/` يضم الإدخال والمعالجة والكشف والتتبع والتحليلات والتنبيهات والويب، بينما توجد الإعدادات في `config/` والأمثلة في `demo/` والاختبارات في `tests/`.

### الاختبارات
```bash
python -m unittest tests/test_visionguard.py
```
كما يحتوي المستودع على GitHub Actions للتحقق الآلي.

### Docker
```bash
docker compose up --build
```
تمرير الكاميرات أو GPU يعتمد على نظام التشغيل والعتاد ويحتاج إعدادًا خاصًا بالمضيف.

### الأمان والخصوصية
قد تتضمن معالجة الفيديو بيانات شخصية حساسة. استخدم المشروع فقط مع وجود صلاحية قانونية، وقلل مدة الاحتفاظ، واحمِ بيانات الكاميرات والأسرار والشبكة. راجع [SECURITY.md](SECURITY.md). لا تعرض لوحة التحكم أو البث لشبكة غير موثوقة من دون مصادقة وTLS.

### القيود
- الكشف والتتبع احتماليان وقد تحدث نتائج خاطئة أو حالات فقد للكشف.
- المشروع لا يضمن اكتشاف التهديدات أو منع الحوادث.
- توافق RTSP والترميزات يعتمد على OpenCV/FFmpeg والكاميرا.
- تسريع GPU يعتمد على البيئة.
- النشر على الإنترنت يحتاج طبقة حماية ومراقبة وإدارة أسرار يجهزها المشغّل.

### التطوير الاختياري
يمكن مستقبلًا إضافة مصادقة أقوى للوحة، واختبارات تكامل بوسائط مولدة، وسياسات احتفاظ قابلة للضبط، وتوثيق أوسع لتسريع العتاد.

### المساهمة والترخيص
راجع [CONTRIBUTING.md](CONTRIBUTING.md). المشروع مرخص برخصة MIT الموضحة في [LICENSE](LICENSE).

### المؤلف
**Radwan Abdulhadi Ahmed**  
**رضوان عبدالهادي أحمد**  
GitHub: **@rad03i2**
