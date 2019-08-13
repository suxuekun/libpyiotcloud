# Android app

To build Android mobile app using the Ionic web app requires the following:

- Installation of [Java SE Development Kit 8](https://www.oracle.com/technetwork/java/javase/downloads/jdk8-downloads-2133151.html)
- Installation of [Android Studio (with Android SDK)](https://developer.android.com/studio)
- Accepting of Android SDK license
  cd %LOCALAPPDATA%\Android\sdk\tools\bin
  sdkmanager.bat --licenses
- Build using 
  'ionic cordova build android'
- Run on an Android emulator, 
  'ionic cordova emulate android --target=Nexus_5X_API_29_x86'
  target can be checked using %LOCALAPPDATA%\Android\sdk\tools\bin\avdmanager list avd
- Run on an Android device
  Copy platforms\android\app\build\outputs\apk\debug\app-debug.apk
  Rename to iot-portal-app-debug.apk
