# Android app

To build Android mobile app using the Ionic web app requires the following:

- Installation of [Java SE Development Kit 8](https://www.oracle.com/technetwork/java/javase/downloads/jdk8-downloads-2133151.html)
- Installation of [Android Studio (with Android SDK)](https://developer.android.com/studio)
- Accepting of <b>Android SDK license</b>

  - cd %LOCALAPPDATA%\Android\sdk\tools\bin
  - sdkmanager.bat --licenses
  
- Build using 

  - ionic cordova build android
  
- Run on an Android emulator, 

  - ionic cordova emulate android --target=Nexus_5X_API_29_x86
  - FYI: %LOCALAPPDATA%\Android\sdk\tools\bin\avdmanager list avd
  
- Run on an Android device

  - Use iot-portal-app-debug.apk
