[app]
title = FaceApp
package.name = faceapp
package.domain = com.example
source.dir = app
# Include *everything* in app/, but keep repo thin
requirements = python3,kivy==2.2.1,flask,werkzeug==2.3.8,\
               numpy,opencv-python==4.5.2.60,android,requests
orientation = portrait
fullscreen = 0
log_level = 2
presplash.filename = %(source.dir)s/assets/presplash.png
icon.filename = %(source.dir)s/assets/icon.png
android.permissions = CAMERA,INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.allow_backup = True
# Avoid OpenCV config crash
android.ndk_api = 21
# copy_libs is safer for cv2.so bundling
android.copy_libs = 1

[buildozer]
warn_on_root = 0
