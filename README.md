# FaceApp Android - Complete Project Structure and Build Guide

## File Structure

Your project should be organized as follows:

```
faceapp-android/
├── .github/
│   └── workflows/
│       └── build.yml                 # GitHub Actions workflow (fixed)
├── main.py                          # Kivy wrapper for Android (NEW)
├── python-app.py                    # Your existing Flask backend (UNCHANGED)
├── buildozer.spec                   # Build configuration (COMPLETE)
├── haarcascade_frontalface_default.xml  # OpenCV classifier
├── known_faces/                     # Created automatically on first run
├── requirements.txt                 # Python dependencies (optional)
└── README.md                        # This file
```

## Fixed Issues

### 1. GitHub Actions Error Fix
**Problem**: `Unexpected input(s) 'log_level'`
**Solution**: Removed invalid `log_level` parameter. Valid inputs for ArtemSBulgakov/buildozer-action@v1 are:
- `command` (default: "buildozer android debug")
- `workdir` (default: ".")
- `buildozer_version` (default: "stable")
- `repository_root` (default: ".")

### 2. Buildozer.spec Error Fix
**Problem**: `One of "version" or "version.regex" must be set`
**Solution**: Added `version = 1.0` to the [app] section in buildozer.spec

### 3. Android Compatibility
**Problem**: Direct Flask app won't work on Android
**Solution**: Created Kivy wrapper (main.py) that:
- Manages Flask server in background thread
- Handles Android permissions automatically
- Creates proper storage directories
- Provides simple UI to start/stop server

## Step-by-Step Build Instructions

### Method 1: GitHub Actions (Recommended)

1. **Create Repository Structure**:
   ```bash
   mkdir faceapp-android
   cd faceapp-android
   
   # Create directories
   mkdir -p .github/workflows
   ```

2. **Add Files**:
   - Copy your `python-app.py` (unchanged)
   - Add `main.py` (Kivy wrapper)
   - Add `buildozer.spec` (complete configuration)
   - Add `.github/workflows/build.yml` (fixed workflow)
   - Download `haarcascade_frontalface_default.xml` from OpenCV

3. **Download Haar Cascade**:
   ```bash
   curl -o haarcascade_frontalface_default.xml \
   https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml
   ```

4. **Push to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial Android build setup"
   git branch -M main
   git remote add origin YOUR_REPO_URL
   git push -u origin main
   ```

5. **Download APK**:
   - Go to Actions tab in your GitHub repository
   - Wait for build to complete (~15-20 minutes)
   - Download APK from Artifacts section

### Method 2: Local Build (Linux/macOS)

1. **Install Dependencies**:
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install -y git zip unzip openjdk-17-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev

   # Install buildozer
   pip3 install --user buildozer
   ```

2. **Build APK**:
   ```bash
   cd faceapp-android
   buildozer android debug
   ```

3. **Install on Device**:
   ```bash
   # Enable USB debugging on your Android device
   adb install bin/faceapp-*.apk
   ```

## Android App Usage

1. **Install APK** on your Android device
2. **Grant Permissions** when prompted:
   - Camera access
   - Storage access
   - Network access
3. **Open FaceApp** and tap "Start Server"
4. **Find Your Phone's IP** (Settings → WiFi → Advanced)
5. **Access Server** via browser: `http://YOUR_PHONE_IP:5000`

## API Endpoints (Same as Desktop)

- `GET /` - Server status
- `POST /process_frame` - Process camera frame for face recognition
- `POST /register_user` - Register new user
- `POST /get_user_email` - Get user email
- `POST /send_otp` - Send OTP for verification
- `POST /verify_otp` - Verify OTP
- `POST /start_update_capture` - Start updating user photos
- `GET /get_last_recognized` - Get last recognized person

## Storage Locations

### Desktop Testing
- `./known_faces/` (project directory)

### Android Device
- `/storage/emulated/0/FaceApp/known_faces/` (accessible via USB)

## Troubleshooting

### Build Errors

1. **"No space left on device"**:
   - Use GitHub Actions instead of local build
   - Clean buildozer cache: `buildozer android clean`

2. **OpenCV crashes**:
   - Ensure OpenCV version is 4.8.1.78 (specified in buildozer.spec)
   - Haar cascade file must be present

3. **Permission denied**:
   - Make sure Android permissions are granted
   - Check storage access in device settings

### Runtime Errors

1. **Camera not working**:
   - Grant camera permission in app settings
   - Restart app after granting permissions

2. **Server won't start**:
   - Check if port 5000 is available
   - Look at app logs via `adb logcat`

3. **Face recognition fails**:
   - Ensure proper lighting
   - Check if `known_faces` folder has training images
   - Verify haar cascade file is present

## Environment Variables (Optional)

For email functionality, set these environment variables in your system or add them to the app:

```bash
export FACEAPP_EMAIL="your_app_email@gmail.com"
export FACEAPP_PASS="your_app_password"  # Use App Password for Gmail
export FACEAPP_ADMIN_EMAIL="admin@example.com"
```

## Testing

### Desktop Testing
```bash
python3 main.py
```

### Android Testing
```bash
# Install and run
adb install bin/faceapp-*.apk
adb shell am start -n com.example.faceapp/org.kivy.android.PythonActivity

# View logs
adb logcat | grep python
```

## Dependencies Included

- **Core**: Python 3, Kivy 2.2.1
- **Backend**: Flask 2.3.3, Flask-CORS 4.0.0
- **Computer Vision**: OpenCV 4.8.1.78, NumPy 1.24.3
- **Android**: android, pyjnius
- **Image Processing**: Pillow
- **HTTP**: requests 2.31.0

## Security Notes

- Server runs on local network only (0.0.0.0:5000)
- No external internet access required for core functionality
- Email notifications require internet connection
- Stored face data remains on device

## Support

If you encounter issues:
1. Check GitHub Actions logs for build errors
2. Use `adb logcat` for runtime debugging
3. Verify all files are in correct locations
4. Ensure Android permissions are granted

## License

Same as your original project.