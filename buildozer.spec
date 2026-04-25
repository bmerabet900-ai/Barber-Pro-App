[app]
title = Barber Pro
package.name = barberpro
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3,kivy==2.3.0,android,pyjnius

orientation = portrait
fullscreen = 0
android.permissions = android.permission.READ_CALL_LOG, android.permission.WRITE_CALL_LOG, android.permission.CALL_PHONE, android.permission.INTERNET
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 1
