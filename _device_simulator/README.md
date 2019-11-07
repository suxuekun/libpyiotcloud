# How To Guide:

0. Access the IoT portal.
    
    - Via <b>webapp</b> https://richmondu.com
    - Via <b>iOS/Android app simulators</b> https://creator.ionic.io/share/8f86e2005ba5
    - Via <b>Ionic Creator mobile app</b> from Apple App Store or Google Play - Use code: <b>B26EB3</b>


1. Create an account and login.

    <img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/tutorial_signuplogin.png" width="600"/>
    
    Click on No account yet to create an account.

    <img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/tutorial_signuplogin_2.png" width="600"/>
    
    Input the details. Username can be same as email.

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

    - Device simulator (Python) - <b>device_simulator.py.bat</b>
    - Device simulator (NodeJS) - <b>device_simulator.js.bat</b>
    - FT900 device (FT900RevC or IoTModule) - <b>iot_config.h</b>

4. Run the device.

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


7. Test buying credits using Paypal.

    <img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/tutorial_buycredits.png" width="600"/>
    
    Go to Account Page. Click on "Buy credits" button.
    
    
    <img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/tutorial_buycredits_2.png" width="600"/>
    
    Select package. Click on "Pay via Paypal" button.
    
    
    <img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/tutorial_buycredits_3.png" width="600"/>

    A Paypal window appears. Login using the following test account: username-iotportal@bridgetek.com password-BrtIoTPortal
    

    <img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/tutorial_buycredits_4.png" width="600"/>
    
    Click on "Continue" button to approve the payment.
    
    
    <img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/tutorial_buycredits_5.png" width="600"/>
    
    A confirmation page appears indicating that the payment transaction was successful.
    
    
    <img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/tutorial_buycredits_6.png" width="600"/>

    You'll be redirected back to the original window with a popup indicating the new credit balance.



# Device simulator (Python):

### Setup

1. Install the latest Python 3.X.X from https://www.python.org/downloads/

2. Install the required python libraries of the application:

    - pip install -r requirements.py.txt OR
    - python pip install -r requirements.py.txt

### Test

1. Update DEVICE_ID in <b>device_simulator.py.bat</b>

   NOTE: To get a device ID, you must first register a device in the IoT Portal.

    <img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/device_simulator_deviceid_py.png" width="600"/>

2. Run <b>device_simulator.py.bat</b>

    <img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/device_simulator_bootup_py.png" width="600"/>



# Device simulator (NodeJS):

### Setup

1. Install the latest NodeJS from https://nodejs.org/en/download/

2. Go to device_simulator folder and install the required nodejs libraries of the application:

    - cd __device_simulator
    - npm install mqtt
    - npm install fs
    - npm install system-sleep
    - npm install os
    - npm install argparse

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

    <img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/code_ft90Xiotbrtcloud.png" width="600"/>
    
2. Compile code and load the binary.

    <img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/device_bootup.png" width="700"/>

