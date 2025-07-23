import threading, sys, os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from android.permissions import request_permissions, Permission
from android.storage import primary_external_storage_path
from face_backend.app import app as flask_app  # unchanged backend

# 1️⃣  runtime permissions
request_permissions([Permission.CAMERA,
                     Permission.WRITE_EXTERNAL_STORAGE,
                     Permission.READ_EXTERNAL_STORAGE])

# 2️⃣  ensure storage folders exist
BASE_DIR = os.path.join(primary_external_storage_path(), "FaceApp")
KNOWN_DIR = os.path.join(BASE_DIR, "known_faces")
os.makedirs(KNOWN_DIR, exist_ok=True)

# 3️⃣  background Flask server
def run_server():
    flask_app.run(host="0.0.0.0", port=5000, threaded=True)

class Root(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", **kwargs)
        self.server_thread = None
        self.start_btn = Button(text="Start server")
        self.stop_btn  = Button(text="Stop server", disabled=True)
        self.start_btn.bind(on_press=self.start_server)
        self.stop_btn.bind(on_press=self.stop_server)
        self.add_widget(self.start_btn)
        self.add_widget(self.stop_btn)

    def start_server(self, *_):
        if not self.server_thread:
            self.server_thread = threading.Thread(target=run_server, daemon=True)
            self.server_thread.start()
            self.start_btn.disabled, self.stop_btn.disabled = True, False

    def stop_server(self, *_):
        # graceful shutdown via Werkzeug
        flask_app.shutdown()
        self.server_thread.join()
        self.server_thread = None
        self.start_btn.disabled, self.stop_btn.disabled = False, True

class FaceAppUI(App):
    def build(self):
        return Root()

if __name__ == "__main__":
    FaceAppUI().run()
