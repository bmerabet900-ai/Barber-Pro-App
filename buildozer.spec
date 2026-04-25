[app]
title = Barber Pro
package.name = barberpro
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0

# المتطلبات الكاملة (kivy, android, pyjnius ضرورية جداً)
requirements = python3,kivy==2.3.0,android,pyjnius

orientation = portrait
fullscreen = 0

# الصلاحيات بالأسماء الرسمية الكاملة
android.permissions = android.permission.READ_CALL_LOG, android.permission.WRITE_CALL_LOG, android.permission.CALL_PHONE, android.permission.INTERNET

# إعدادات التوافق مع الأندرويد
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
