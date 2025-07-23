#!/usr/bin/env python3
"""
FaceApp Android - Kivy wrapper for Flask face recognition backend
This file combines Kivy UI with Flask backend for Android deployment
"""

import os
import sys
import threading
import time
from pathlib import Path

# Kivy imports
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.logger import Logger

# Android-specific imports
try:
    from android.permissions import request_permissions, Permission
    from android.storage import primary_external_storage_path
    from android import activity
    ANDROID = True
    Logger.info("FaceApp: Running on Android")
except ImportError:
    ANDROID = False
    Logger.info("FaceApp: Running on desktop")

# Import your existing Flask app
try:
    # Import the existing Flask backend
    import importlib.util
    
    # Load the python-app.py as a module
    spec = importlib.util.spec_from_file_location("flask_backend", "python-app.py")
    flask_backend = importlib.util.module_from_spec(spec)
    sys.modules["flask_backend"] = flask_backend
    spec.loader.exec_module(flask_backend)
    
    flask_app = flask_backend.app
    face_app_backend = flask_backend.face_app_backend
    Logger.info("FaceApp: Flask backend loaded successfully")
except Exception as e:
    Logger.error(f"FaceApp: Failed to load Flask backend: {e}")
    flask_app = None
    face_app_backend = None

class FaceAppRoot(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', spacing=10, padding=20, **kwargs)
        
        # Server state
        self.server_thread = None
        self.server_running = False
        
        # Setup UI
        self.setup_ui()
        
        # Setup Android-specific configurations
        if ANDROID:
            self.setup_android()
    
    def setup_ui(self):
        """Setup the user interface"""
        # Title
        title = Label(
            text='FaceApp - Face Recognition Server',
            size_hint_y=None,
            height=50,
            font_size=20
        )
        self.add_widget(title)
        
        # Status label
        self.status_label = Label(
            text='Server Status: Stopped',
            size_hint_y=None,
            height=40,
            color=(1, 0, 0, 1)  # Red color
        )
        self.add_widget(self.status_label)
        
        # Server control buttons
        button_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=60)
        
        self.start_button = Button(
            text='Start Server',
            size_hint_x=0.5,
            background_color=(0, 0.7, 0, 1)  # Green
        )
        self.start_button.bind(on_press=self.start_server)
        
        self.stop_button = Button(
            text='Stop Server',
            size_hint_x=0.5,
            disabled=True,
            background_color=(0.7, 0, 0, 1)  # Red
        )
        self.stop_button.bind(on_press=self.stop_server)
        
        button_layout.add_widget(self.start_button)
        button_layout.add_widget(self.stop_button)
        self.add_widget(button_layout)
        
        # Info label
        info_text = """
Instructions:
1. Tap 'Start Server' to begin face recognition service
2. Server will run on your phone's local IP address
3. Access via: http://YOUR_PHONE_IP:5000
4. Use the endpoints for face recognition features
5. Tap 'Stop Server' when done

Features:
• Face recognition and registration
• Attendance tracking with email notifications
• Google Forms integration
• Automatic known_faces folder creation
        """.strip()
        
        info_label = Label(
            text=info_text,
            text_size=(None, None),
            halign='left',
            valign='top'
        )
        self.add_widget(info_label)
    
    def setup_android(self):
        """Setup Android-specific configurations"""
        try:
            # Request necessary permissions
            permissions = [
                Permission.CAMERA,
                Permission.INTERNET,
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.READ_EXTERNAL_STORAGE,
                Permission.ACCESS_NETWORK_STATE,
                Permission.WAKE_LOCK
            ]
            request_permissions(permissions)
            Logger.info("FaceApp: Android permissions requested")
            
            # Setup storage directories
            self.setup_storage_directories()
            
        except Exception as e:
            Logger.error(f"FaceApp: Android setup failed: {e}")
    
    def setup_storage_directories(self):
        """Setup Android storage directories"""
        try:
            if ANDROID:
                # Use Android external storage
                base_path = primary_external_storage_path()
                app_dir = os.path.join(base_path, "FaceApp")
            else:
                # Use current directory for desktop testing
                app_dir = "."
            
            known_faces_dir = os.path.join(app_dir, "known_faces")
            
            # Create directories
            os.makedirs(known_faces_dir, exist_ok=True)
            Logger.info(f"FaceApp: Created directories at {app_dir}")
            
            # Update backend path if available
            if face_app_backend:
                face_app_backend.known_faces_dir = known_faces_dir
                Logger.info(f"FaceApp: Updated backend storage path to {known_faces_dir}")
                
        except Exception as e:
            Logger.error(f"FaceApp: Storage setup failed: {e}")
    
    def start_server(self, instance):
        """Start the Flask server"""
        if self.server_running or not flask_app:
            return
        
        try:
            # Start server in a separate thread
            self.server_thread = threading.Thread(
                target=self.run_flask_server,
                daemon=True,
                name="FlaskServerThread"
            )
            self.server_thread.start()
            
            # Update UI
            self.server_running = True
            self.start_button.disabled = True
            self.stop_button.disabled = False
            self.status_label.text = 'Server Status: Starting...'
            self.status_label.color = (1, 1, 0, 1)  # Yellow
            
            # Schedule status check
            Clock.schedule_once(self.check_server_status, 2)
            
            Logger.info("FaceApp: Server start initiated")
            
        except Exception as e:
            Logger.error(f"FaceApp: Failed to start server: {e}")
            self.status_label.text = f'Server Error: {str(e)}'
            self.status_label.color = (1, 0, 0, 1)  # Red
    
    def run_flask_server(self):
        """Run the Flask server"""
        try:
            # Run Flask server
            flask_app.run(
                host='0.0.0.0',
                port=5000,
                debug=False,
                threaded=True,
                use_reloader=False
            )
        except Exception as e:
            Logger.error(f"FaceApp: Flask server error: {e}")
            Clock.schedule_once(lambda dt: self.server_error(str(e)), 0)
    
    def check_server_status(self, dt):
        """Check if server is running and update status"""
        if self.server_running and self.server_thread and self.server_thread.is_alive():
            self.status_label.text = 'Server Status: Running on port 5000'
            self.status_label.color = (0, 1, 0, 1)  # Green
        else:
            self.server_error("Server failed to start")
    
    def server_error(self, error_msg):
        """Handle server errors"""
        self.server_running = False
        self.start_button.disabled = False
        self.stop_button.disabled = True
        self.status_label.text = f'Server Error: {error_msg}'
        self.status_label.color = (1, 0, 0, 1)  # Red
    
    def stop_server(self, instance):
        """Stop the Flask server"""
        try:
            self.server_running = False
            
            # Note: Flask's development server doesn't have a clean shutdown method
            # In a production app, you'd want to implement proper shutdown
            if self.server_thread:
                # The thread will continue running until the Flask server stops
                # For a proper shutdown, you'd need to implement a shutdown endpoint
                pass
            
            # Update UI
            self.start_button.disabled = False
            self.stop_button.disabled = True
            self.status_label.text = 'Server Status: Stopped'
            self.status_label.color = (1, 0, 0, 1)  # Red
            
            Logger.info("FaceApp: Server stop initiated")
            
        except Exception as e:
            Logger.error(f"FaceApp: Failed to stop server: {e}")

class FaceAppAndroid(App):
    def build(self):
        """Build the Kivy app"""
        self.title = 'FaceApp - Face Recognition'
        return FaceAppRoot()
    
    def on_start(self):
        """Called when the app starts"""
        Logger.info("FaceApp: Application started")
        
        # Android-specific initialization
        if ANDROID:
            try:
                # Keep screen on while app is running
                from jnius import autoclass
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                WindowManager = autoclass('android.view.WindowManager$LayoutParams')
                activity = PythonActivity.mActivity
                activity.getWindow().addFlags(WindowManager.FLAG_KEEP_SCREEN_ON)
                Logger.info("FaceApp: Screen keep-on enabled")
            except Exception as e:
                Logger.warning(f"FaceApp: Could not enable screen keep-on: {e}")
    
    def on_pause(self):
        """Called when the app is paused"""
        Logger.info("FaceApp: Application paused")
        return True
    
    def on_resume(self):
        """Called when the app is resumed"""
        Logger.info("FaceApp: Application resumed")

def main():
    """Main function"""
    # Ensure haarcascade file exists
    haar_file = "haarcascade_frontalface_default.xml"
    if not os.path.exists(haar_file):
        Logger.warning(f"FaceApp: {haar_file} not found. Face detection may not work.")
    
    # Start the Kivy app
    FaceAppAndroid().run()

if __name__ == '__main__':
    main()