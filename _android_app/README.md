# Android app

To build Android mobile app using the Ionic web app requires the following:

- Installation of [Java SE Development Kit 8](https://www.oracle.com/technetwork/java/javase/downloads/jdk8-downloads-2133151.html)
- Installation of [Android Studio (with Android SDK)](https://developer.android.com/studio)
- Accepting of <b>Android SDK license</b>

  - cd %LOCALAPPDATA%\Android\sdk\tools\bin
  - sdkmanager.bat --licenses
  
- Build using the following command: 

  - ionic cordova build android
    (This generates an APK file in the following path platforms\android\app\build\outputs\apk\debug\app-debug.apk . A copy of this APK has is made available. Refer to iot-portal-app-debug.apk)
  
- Run on an <b>Android emulator</b> from <b>Android Studio</b>, 

  - ionic cordova emulate android --target=Nexus_5X_API_29_x86
  - FYI: %LOCALAPPDATA%\Android\sdk\tools\bin\avdmanager list avd
  
