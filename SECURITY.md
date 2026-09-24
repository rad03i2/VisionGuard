# Security Policy / سياسة الأمان

## English

VisionGuard processes camera/video sources and may store incident metadata or snapshots. Treat camera URLs, credentials, alert tokens, and recorded imagery as sensitive data.

- Never commit RTSP credentials, bot tokens, webhook URLs, SMTP passwords, or private footage.
- Keep secrets in environment variables or a secret manager; do not place real credentials in `config/settings.yaml`.
- Bind the dashboard to a trusted interface or protect it behind an authenticated reverse proxy before network exposure.
- Use TLS for remote access and restrict camera/network access with firewall rules.
- Review retention requirements before storing snapshots or incident records, and comply with applicable privacy and surveillance laws.
- Keep Python dependencies and model packages updated from trusted sources.

For a suspected vulnerability, open a GitHub issue only when the report contains no secrets, private camera addresses, personal data, or exploit material that would put users at immediate risk. For sensitive reports, use GitHub's private vulnerability reporting feature when available.

## العربية

يعالج VisionGuard مصادر كاميرات وفيديو وقد يخزن بيانات الحوادث أو لقطاتها، لذلك يجب اعتبار روابط الكاميرات وبيانات الدخول ورموز التنبيه والصور المسجلة معلومات حساسة.

- لا ترفع بيانات RTSP أو رموز البوت أو Webhook أو كلمات مرور البريد أو فيديوهات خاصة إلى المستودع.
- خزّن الأسرار في متغيرات البيئة أو مدير أسرار، ولا تضع بيانات حقيقية في `config/settings.yaml`.
- لا تعرض لوحة التحكم للإنترنت مباشرة؛ استخدم شبكة موثوقة أو reverse proxy محمي بالمصادقة.
- استخدم TLS عند الوصول البعيد وحدد الوصول للشبكة والكاميرات بجدار ناري.
- راجع سياسة الاحتفاظ بالصور والسجلات والتزم بقوانين الخصوصية والمراقبة المعمول بها.
- حدّث الاعتماديات والنماذج من مصادر موثوقة.

المؤلف: Radwan Abdulhadi Ahmed — رضوان عبدالهادي أحمد — @rad03i2
