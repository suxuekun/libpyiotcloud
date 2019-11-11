# Android app

### Installing APK binary:

Compiled binaries are available. 
Make sure to use the latest compilation.


### Compiling APK binary:

To build Android mobile app using the Ionic web app requires the following:

- Installation of [Java SE Development Kit 8](https://www.oracle.com/technetwork/java/javase/downloads/jdk8-downloads-2133151.html)
- Installation of [Android Studio (with Android SDK)](https://developer.android.com/studio)
- Accepting of <b>Android SDK license</b>

  - cd %LOCALAPPDATA%\Android\sdk\tools\bin
  - sdkmanager.bat --licenses
  
- Build using the following command: 

  - <b> ionic cordova build android </b>
    (This generates an APK file in the following path platforms\android\app\build\outputs\apk\debug\app-debug.apk . A copy of this APK has is made available. Refer to iot-portal-app-debug.apk)
  
  
### Running APK binary on Android emulator:

To run on an <b>Android emulator</b> from <b>Android Studio </b> 

  - <b> ionic cordova emulate android --target=Nexus_5X_API_29_x86 </b> (This generates and runs the APK file on an emulated Android device.)
  - FYI: %LOCALAPPDATA%\Android\sdk\tools\bin\avdmanager list avd


<img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/ui_androidemulator.png" width="1000"/>
