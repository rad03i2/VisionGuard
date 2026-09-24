# Contributing / المساهمة

## English

Contributions that improve reliability, privacy, portability, documentation, tests, or maintainability are welcome.

1. Fork the repository and create a focused branch.
2. Install dependencies with `pip install -r requirements.txt`.
3. Keep changes scoped and avoid committing camera credentials, tokens, model weights, private footage, generated databases, or snapshots.
4. Add or update tests for behavioral changes.
5. Run `python -m unittest tests/test_visionguard.py` before submitting a pull request.
6. Update the README when behavior, configuration, or commands change.

Please describe what changed, why it changed, and how it was validated. Do not submit surveillance footage or personally identifying imagery as test fixtures.

## العربية

نرحب بالمساهمات التي تحسن الاعتمادية والخصوصية والتوافق والتوثيق والاختبارات وسهولة الصيانة.

1. أنشئ Fork ثم فرعًا مخصصًا للتغيير.
2. ثبّت الاعتماديات عبر `pip install -r requirements.txt`.
3. اجعل التغيير محددًا، ولا ترفع بيانات الكاميرات أو الرموز السرية أو أوزان النماذج أو الفيديوهات الخاصة أو قواعد البيانات واللقطات المولدة.
4. أضف أو حدّث الاختبارات عند تغيير السلوك.
5. شغّل `python -m unittest tests/test_visionguard.py` قبل إرسال Pull Request.
6. حدّث README إذا تغير السلوك أو الإعداد أو أوامر التشغيل.

اذكر في طلب الدمج ما الذي تغير وسبب التغيير وطريقة التحقق منه، ولا تستخدم صورًا أو فيديوهات تكشف هوية أشخاص كبيانات اختبار.

**Author / المؤلف:** Radwan Abdulhadi Ahmed — رضوان عبدالهادي أحمد — @rad03i2
