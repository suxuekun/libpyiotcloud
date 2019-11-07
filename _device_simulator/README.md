# User Guide:

This page contains a step-by-step tutorial on how to use the IoT Portal including how to use the device simulators or FT900 device module. If you have questions, comments and suggestions, please contact me at Skype. My ID is <b>ftdi.richmond.umagat</b>. 

### Summary

    A. Detailed step-by-step guide with screenshots
        0. Access the IoT portal.
           a. Via web app https://richmondu.com
           b. Via Android mobile app - Install APK: https://github.com/richmondu/libpyiotcloud/tree/master/_android_app
           c. Via Ionic Creator mobile app simulators https://creator.ionic.io/share/8f86e2005ba5
           d. Via Ionic Creator mobile app from Apple App Store or Google Play - Use code: <b>B26EB3</b>
        1. Create an account and login.
        2. Register a device (Registering a device will return a unique DEVICE_ID).
        3. Set the DEVICE_ID on the device.
        4. Run the device.
        5. Access and control the device via the IoT portal. (GPIO, RTC, UART, IP/MAC, etc)
        6. Check device history.
        7. Test buying credits using Paypal.
        8. Test username and password recovery.
        9. Test deleting a device.
    B. Device simulator (Python)
    C. Device simulator (NodeJS)
    D. FT900 device (FT900RevC or IoTModule)


# Detailed step-by-step guide with screenshots:

0. Access the IoT portal.
    
    The IoT portal can be accessed in 4 ways:
    
    - Via <b>webapp</b> https://richmondu.com
    
        <img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/iotportal_website.png" width="600"/>
    
    - Via <b>Android mobile app</b> - Install the latest APK: https://github.com/richmondu/libpyiotcloud/tree/master/_android_app
    
        <img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/ui_androidemulator.png" width="600"/>
        
    - Via <b>Ionic Creator mobile app simulators</b> https://creator.ionic.io/share/8f86e2005ba5
    
        <img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/iotportal_mobilesimulators.png" width="600"/>
    
    - Via <b>Ionic Creator mobile app</b> from Apple App Store or Google Play - Use code: <b>B26EB3</b>

        <img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/iotportal_ioniccreatorapp.png" width="600"/>

    
    

1. Create an account and login.

    <img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/tutorial_signuplogin.png" width="600"/>
    
    Click on "No account yet? Get started for free" link to create an account.


    <img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/tutorial_signuplogin_2.png" width="600"/>
    
    Input the details. Username can be same as email. Note that a confirmation code will be sent to your email.


    <img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/tutorial_signuplogin_3.png" width="600"/>
    
    Input the 6-digit code sent to your email.


    <img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/tutorial_signuplogin_4.png" width="600"/>
    
    You can now login using your specified username and password.


2. Register a device (Registering a device will return a unique DEVICE_ID).

    <img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/tutorial_adddevice.png" width="600"/>
    
    To add a device, click on the "+" button on the top right of the window.


    <img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/tutorial_adddevice_2.png" width="600"/>

    Type a name for the device. Ex. "Smart Device 1"


    <img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/tutorial_adddevice_3.png" width="600"/>
    
    Wait for the device to be registered. A popup up window will appear that the device has been registered.


    <img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/tutorial_adddevice_4.png" width="600"/>

    Copy the DEVICE ID by double clicking on it and typing Ctrl+C.
    

3. Set the DEVICE_ID on the device.

    <b>Refer to corresponding sections below for setup instructions for the device simulators and FT900 device.</b>
    
    - Device simulator (Python) - <b>device_simulator.py.bat</b>
    
        <img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/device_simulator_deviceid_py.png" width="600"/>
    
    - Device simulator (NodeJS) - <b>device_simulator.js.bat</b>
    
        <img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/device_simulator_deviceid_js.png" width="600"/>
        
    - FT900 device (FT900RevC or IoTModule) - <b>iot_config.h</b>

        <img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/code_ft90Xiotbrtcloud.png" width="600"/>


4. Run the device.

    <b>Refer to corresponding sections below for more details with screenshots.</b>


5. Access and control the device via the IoT portal. (GPIO, RTC, UART, IP/MAC, etc)

    <img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/tutorial_testdevice.png" width="600"/>

    Click on the top right button to check if device is RUNNING or NOT RUNNING. Make sure device is RUNNING before proceeding.


    <img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/tutorial_testdevice_2.png" width="600"/>
    
    Select <b>Ethernet</b>. Click on Get to retrieve the network-related information of the device.


    <img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/tutorial_testdevice_3.png" width="600"/>
    
    Select <b>UART</b>. Type "hello world" on the message box then click "Submit" button to be displayed on the device.


    <img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/tutorial_testdevice_4.png" width="600"/>

    Select <b>GPIO</b>. Type "10" on GPIO Number then click "Get" button to get the value of the GPIO.


    <img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/tutorial_testdevice_5.png" width="600"/>

    Select <b>Notifications</b>. Select Email. Type your email address and the message then click "Submit" button. You should receive the email. 
    
    Note that your email must first be registered in AWS Notifications. Contact me to registered your email address. This a limitation of AWS Pinpoint in Sandbox mode.
    

    <img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/tutorial_testdevice_6.png" width="600"/>

    Select <b>Notifications</b>. Select SMS. Choose country, input phone number and the message. Then click Submit. You should receive the SMS. 
    
    Note AWS Pinpoint in Sandbox mode has limit in the number of SMS messages that can be sent. So test wisely. You can also select the source of SMS - AWS Pinpoint, Twilio or Nexmo.


6. Check device history.

    <img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/tutorial_checkhistory.png" width="600"/>

    Go to History Page. This will display the transaction received and sent by each of the devices in descending order.


    <img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/tutorial_checkhistory_2.png" width="600"/>

    Select a device from the list to filter transactions for that specific device.


7. Test buying credits using Paypal.

    <img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/tutorial_buycredits.png" width="600"/>
    
    Go to Account Page. Click on "Buy credits" button.
    
    
    <img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/tutorial_buycredits_2.png" width="600"/>
    
    Select package. Click on "Pay via Paypal" button. This will open up a Paypal window.
    
    
    <img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/tutorial_buycredits_3.png" width="600"/>

    A Paypal window appears. Login using the following test account - username: <b>iotportal@bridgetek.com</b> password: <b>BrtIoTPortal</b>
    

    <img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/tutorial_buycredits_4.png" width="600"/>
    
    Click on "Continue" button to approve the payment.
    
    
    <img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/tutorial_buycredits_5.png" width="600"/>
    
    A confirmation page appears indicating that the payment transaction was successful.
    
    
    <img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/tutorial_buycredits_6.png" width="600"/>

    You'll be redirected back to the original window with a popup indicating the new credit balance.


8. Test username and password recovery.

    <img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/tutorial_forgotpassword.png" width="600"/>
    
    Click on "Forgot username or password?" link.
    
    
    <img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/tutorial_forgotpassword_2.png" width="600"/>
    
    Input your email address then click on "Submit" button. Note that a confirmation code will be sent to your email.
    
    
    <img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/tutorial_forgotpassword_3.png" width="600"/>
    
    Input the confirmation code including your new password. Then click on "Submit" button.
    

    <img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/tutorial_forgotpassword_4.png" width="600"/>

    You can now login with your username and new password.


9. Test deleting a device.

    <img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/tutorial_deletedevice.png" width="600"/>
    
    Swipe the device to the right. The View and Delete buttons will appear. Click on the "Delete" button.
    
    
    <img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/tutorial_deletedevice_2.png" width="600"/>
    
    A confirmation popup will appear to delete the device.
    
    
    <img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/tutorial_deletedevice_3.png" width="600"/>

    The list of devices will automatically be updated to remove the deleted device.
    


# Device simulator (Python):

### Setup

1. Install the latest Python 3.X.X from https://www.python.org/downloads/

    <img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/device_simulator_py.png" width="600"/>

    After installation, open a command prompt and type "Python". You should see the version of the "Python" installed.
    

2. Install the required python libraries of the application:

    - pip install -r requirements.py.txt OR
    - python pip install -r requirements.py.txt

    <img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/device_simulator_requirements_py.png" width="600"/>


### Test

1. Update DEVICE_ID in <b>device_simulator.py.bat</b>

   NOTE: To get a device ID, you must first register a device in the IoT Portal.

    <img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/device_simulator_deviceid_py.png" width="600"/>

2. Run <b>device_simulator.py.bat</b>

    <img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/device_simulator_bootup_py.png" width="600"/>



# Device simulator (NodeJS):

### Setup

1. Install the latest NodeJS from https://nodejs.org/en/download/

    <img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/device_simulator_js.png" width="600"/>

    After installation, open a command prompt and type "npm". You should see the version of the "npm" installed.


2. Install the required nodejs libraries of the application:

    - npm install -g mqtt
    - npm install -g fs
    - npm install -g system-sleep
    - npm install -g os
    - npm install -g argparse

    <img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/device_simulator_requirements_js.png" width="600"/>

### Test

1. Update DEVICE_ID in <b>device_simulator.js.bat</b>

   NOTE: To get a device ID, you must first register a device in the IoT Portal.
   
    <img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/device_simulator_deviceid_js.png" width="600"/>
    
2. Run <b>device_simulator.js.bat</b>

    <img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/device_simulator_bootup_js.png" width="600"/>


# FT900 device (FT900RevC or IoTModule)

### Setup

1. Get the FT900 code [here](https://github.com/richmondu/FT900/tree/master/IoT/ft90x_iot_brtcloud).

### Test

1. Update DEVICE_ID in <b>iot_config.h</b>

    NOTE: To get a device ID, you must first register a device in the IoT Portal.

    <img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/code_ft90Xiotbrtcloud.png" width="600"/>
    
2. Compile code and load the binary.

    <img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/device_bootup.png" width="700"/>

