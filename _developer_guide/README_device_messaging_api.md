# MQTTS Device Messaging API Documentation

This is for the firmware developers.

A device can connect to the portal using MQTT protocol over TLS connection.
It establishes connection with the message broker using its UUID and SerialNumber as MQTT username and password respectively.
This is a security measure added in addition to the mutual authentication using SSL X.509 certificates with ECC security.
The ECC certificates are stored in a 3rd-party hardware ATECC chip for hardware-grade secure storage.

	Security measures for device connectivity:

		1. MQTT connectivity over secured TLS connection
		2. ECC-based (Elliptic Curve Cryptography ECC) PKI and X.509 certificates
		3. Enforcement of mutual authentication on both MQTT broker and MQTT client configurations
		4. Unique MQTT credentials (username and password) per device
		5. Strict restrictions for MQTT topic permission (subscribe and publish) per device
		6. [TODO] ECC certificates and UUID stored in 3rd-party ATECC hardware chip 

Upon connection, each device subscribes to its own dedicated MQTT topic using its device identification (DEVICEID/#).
As a result, it will only be receiving subtopics under DEVICEID topic solely for the device.
Each device publishes to its own assigned MQTT topic using its device identification and server (server/DEVICEID/#)
Subscribing or publishing to other MQTT topics will fail as the message broker restricts the permissions of topic for each device.

	MQTT device connection details:

		1.  MQTT host: richmondu.com
		2.  MQTT port: 8883
		3.  MQTT clientid: DEVICEID
		4.  MQTT username: UUID
		5.  MQTT password: jwt.encode({UUID, SERIAL_NUMBER, POE_MAC_ADDRESS}, secret_key=ASK_ME, signing_algo=HMAC_SHA256)
		6.  TLS CA certificate
		7.  TLS client certificates
		8.  TLS client private key
		9.  MQTT subscribe topic: DEVICEID/#
		10. MQTT publish topic: server/DEVICEID/#

Below is a summary and a detailed list of the subtopics the device will receive and publish.


SUMMARY:

	1. STATUS
		A. GET STATUS                       get_status
		B. SET STATUS                       set_status
		C. PUBLISH HEARTBEAT                pub_heartbeat

	2. SETTINGS
		A. GET SETTINGS                     get_settings
		B. SET SETTINGS                     set_settings

	2. UART
		A. SET UART PROPERTIES              set_uart_prop
		B. GET UART PROPERTIES              get_uart_prop        // OBSOLETED
		C. ENABLE/DISABLE UART              enable_uart          // OBSOLETED
		D. GET UARTS                        get_uarts            // OBSOLETED
		E. UART AT Commands

	3. GATEWAY AND LDSBUS
		A. SET GATEWAY DESCRIPTOR           set_descriptor         // auto-register
		B. GET GATEWAY DESCRIPTOR           get_descriptor         // query-based
		C. SET LDSU DESCRIPTORS             set_ldsu_descriptors   // auto-register
		D. GET LDSU DESCRIPTORS             get_ldsu_descriptors   // query-based
		E. IDENTIFY LDSU                    identify_ldsu
		F. ENABLE LDSU DEVICE               enable_ldsu_dev

	4. Configurations
		A. REQUEST CONFIGURATION            req_configuration
		B. RECEIVE CONFIGURATION            rcv_configuration
		C. DELETE CONFIGURATION             del_configuration

	5. Sensor Reading
		A. PUBLISH SENSOR READING           pub_sensor_reading
		B. RECEIVE SENSOR READING           rcv_sensor_reading   // OBSOLETED
		C. REQUEST SENSOR READING           req_sensor_reading   // OBSOLETED

	6. OTA Firmware Update

		A. UPGRADE FIRMWARE                 beg_ota
		B. UPGRADE FIRMWARE COMPLETION      end_ota
		C. REQUEST OTASTATUS                req_otastatus
		D. REQUEST TIME                     req_time
		E. RECEIVE TIME                     rcv_time

	7. Notifications
		A. SEND NOTIFICATION                trigger_notification
		B. STATUS NOTIFICATION              status_notification
		C. RECEIVE NOTIFICATION             recv_notification


	8. GPIO
		A. GET GPIOS                        get_gpios            // OBSOLETED
		B. GET GPIO PROPERTIES              get_gpio_prop        // OBSOLETED
		C. SET GPIO PROPERTIES              set_gpio_prop        // OBSOLETED
		D. ENABLE/DISABLE GPIO              enable_gpio          // OBSOLETED
		E. GET GPIO VOLTAGE                 get_gpio_voltage     // OBSOLETED
		F. SET GPIO VOLTAGE                 set_gpio_voltage     // OBSOLETED

	9. I2C
		A. GET I2C DEVICES                  get_i2c_devs         // OBSOLETED
		B. GET I2C DEVICE PROPERTIES        get_i2c_dev_prop     // OBSOLETED
		C. SET I2C DEVICE PROPERTIES        set_i2c_dev_prop     // OBSOLETED
		D. ENABLE/DISABLE I2C DEVICE        enable_i2c_dev       // OBSOLETED

	10. ADC
		A. GET ADC DEVICES                  get_adc_devs         // OBSOLETED
		B. GET ADC DEVICE PROPERTIES        get_adc_dev_prop     // OBSOLETED
		C. SET ADC DEVICE PROPERTIES        set_adc_dev_prop     // OBSOLETED
		D. ENABLE/DISABLE ADC DEVICE        enable_adc_dev       // OBSOLETED
		E. GET ADC VOLTAGE                  get_adc_voltage      // OBSOLETED
		F. SET ADC VOLTAGE                  set_adc_voltage      // OBSOLETED

	11. 1WIRE
		A. GET 1WIRE DEVICES                get_1wire_devs       // OBSOLETED
		B. GET 1WIRE DEVICE PROPERTIES      get_1wire_dev_prop   // OBSOLETED
		C. SET 1WIRE DEVICE PROPERTIES      set_1wire_dev_prop   // OBSOLETED
		D. ENABLE/DISABLE 1WIRE DEVICE      enable_1wire_dev     // OBSOLETED

	12. TPROBE
		A. GET TPROBE DEVICES               get_tprobe_devs      // OBSOLETED
		B. GET TPROBE DEVICE PROPERTIES     get_tprobe_dev_prop  // OBSOLETED
		C. SET TPROBE DEVICE PROPERTIES     set_tprobe_dev_prop  // OBSOLETED
		D. ENABLE/DISABLE TPROBE DEVICE     enable_tprobe_dev    // OBSOLETED

	13. PERIPHERALS
		A. GET PERIPHERAL DEVICES           get_devs             // OBSOLETED


DETAILED:

	1. STATUS

		A. GET STATUS
		-  Receive:
		   topic: DEVICEID/get_status
		-  Publish:
		   topic: server/DEVICEID/get_status
		   payload: { 'value': {'status': int, 'version': string} }
		   // version is the firmware version in the string format of "major_version.minor_version"
		   // status is an index of the value in the list of statuses
		   //   ["starting", "running", "restart", "restarting", "stop", "stopping", "stopped", "start"]
		   
		B. SET STATUS
		-  Receive:
		   topic: DEVICEID/set_status
		   payload: { 'status': int }
		   // status is an index of the value in the list of statuses
		   //   ["starting", "running", "restart", "restarting", "stop", "stopping", "stopped", "start"]
		-  Publish:
		   topic: server/DEVICEID/set_status
		   payload: { 'value': {'status': int} }
		   
		C. PUBLISH HEARTBEAT
		-  Publish:
		   topic: server/DEVICEID/pub_heartbeat
		   payload: { 'TS': string } // TimeStamp


	2. UART

		A. SET UART PROPERTIES
		-  Receive:
		   topic: DEVICEID/set_uart_prop
		   payload: { 
		       'baudrate': int, 
		       'parity': int, 
		       'flowcontrol': int 
		       'stopbits': int, 
		       'databits': int, 
		   }
		   // sets structure data with correct value mapping
		   // calls uart_close(), uart_soft_reset(), uart_open()
		   // * uart_soft_reset is needed to prevent distorted text when changing databits or parity
		   // * interrupt_attach, uart_enable_interrupt and uart_enable_interrupts_globally needs to be called because uart_soft_reset clears the interrupt
		   //
		   // baudrate is an index of the value in the list of baudrates
		   //   ft900_uart_simple.h: UART_DIVIDER_XXX
		   //   ["110", "150", "300", "1200", "2400", "4800", "9600", "19200", "31250", "38400", "57600", "115200", "230400", "460800", "921600", "1000000"]
		   //      default = 7 (19200)
		   // parity is an index of the value in the list of parities
		   //   ft900_uart_simple.h: uart_parity_t enum
		   //   ["None", "Odd", "Even"]
		   //      default = 0 (None)
		   // flowcontrol is an index of the value in the list of flowcontrols
		   //   ["None", "Rts/Cts", "Xon/Xoff"]
		   //      default = 0 (None)
		   // stopbits is an index of the value in the list of stopbits
		   //   ft900_uart_simple.h: uart_stop_bits_t enum
		   //   ["1", "2"]
		   //      default = 0 (1)
		   // databits is an index of the value in the list of databits
		   //   ft900_uart_simple.h: uart_data_bits_t enum
		   //   ["7", "8"]
		   //      default = 1 (8)
		-  Publish:
		   topic: server/DEVICEID/set_uart_prop
		   payload: {}

		B. GET UART PROPERTIES
		-  Receive:
		   topic: DEVICEID/get_uart_prop
		-  Publish:
		   topic: server/DEVICEID/get_uart_prop
		   payload: { 
		     'value': { 
		       'baudrate': int, 
		       'parity': int, 
		       'flowcontrol': int 
		       'stopbits': int, 
		       'databits': int, 
		     } 
		   }
		   // gets structure data with correct value mapping (due to unexposed values)
		   // baudrate is an index of the value in the list of baudrates
		   //   ft900_uart_simple.h: UART_DIVIDER_XXX
		   //   ["110", "150", "300", "1200", "2400", "4800", "9600", "19200", "31250", "38400", "57600", "115200", "230400", "460800", "921600", "1000000"]
		   //      default = 7 (19200)
		   // parity is an index of the value in the list of parities
		   //   ft900_uart_simple.h: uart_parity_t enum
		   //   ["None", "Odd", "Even"]
		   //      default = 0 (None)
		   // flowcontrol is an index of the value in the list of flowcontrols
		   //   ["None", "Rts/Cts", "Xon/Xoff"]
		   //      default = 0 (None)
		   // stopbits is an index of the value in the list of stopbits
		   //   ft900_uart_simple.h: uart_stop_bits_t enum
		   //   ["1", "2"]
		   //      default = 0 (1)
		   // databits is an index of the value in the list of databits
		   //   ft900_uart_simple.h: uart_data_bits_t enum
		   //   ["7", "8"]
		   //      default = 1 (8)

		C. ENABLE/DISABLE UART
		-  Receive:
		   topic: DEVICEID/enable_uart
		   payload: { 'enable': int }
		   // enable is an int indicating if disabled (0) or enabled (1)
		-  Publish:
		   topic: server/DEVICEID/enable_uart
		   payload: {}
		   // - ENABLE: calls uart_open()
		   //   * interrupt_attach, uart_enable_interrupt and uart_enable_interrupts_globally needs to be called because uart_soft_reset clears the interrupt
		   // - DISABLE: calls uart_close() and uart_soft_reset()
		   //   * uart_soft_reset is needed to prevent distorted text when changing databits or parity

		D. GET UARTS
		-  Receive:
		   topic: DEVICEID/get_uarts
		-  Publish:
		   topic: server/DEVICEID/get_uarts
		   payload: { 
		     'value': { 
		       'uarts': [ 
		           {'enabled': int}, 
		       ]
		     }
		   }
		   // gets enabled status of the UART
		   // enable is an int indicating if disabled (0) or enabled (1)

		E. UART AT Commands
		   - AT+M (Mobile)
		           AT+M
		           AT+M+6512345678
		           AT+M++Hello World
		           AT+M+6512345678+Hello World
		   - AT+E (Email)
		           AT+E
		           AT+E+email@xyz.com
		           AT+E++Hello World
		           AT+E+email@xyz.com+Hello World
		   - AT+N (Notification)
		   - AT+O (mOdem)
		           AT+O
		           AT+O+DEVICEID
		           AT+O++Hello World
		           AT+O+DEVICEID+Hello World
		   - AT+S (Storage)
		   - AT+D (Default)
		           AT+D
		   - Others


	3. GATEWAY and LDSBUS

		A. SET GATEWAY DESCRIPTOR // auto-register
		-  Publish:
		   topic: server/DEVICEID/set_descriptor
		   payload: { 
		     'value': {
		          // RO
		          "UUID": string, // UUID
		          "SNO" : string, // Serial Number
		          "PMAC": string, // PoE MAC ID
		          "WMAC": string, // WiFi MAC ID
		          "MOD" : string, // Model Number
		          "PRV" : string, // Product Version
		          "FWV" : string, // Firmware Version and date
		          "ICAC": string, // Sensor Cache Storage Size
		          "IPRT": string, // Number of LDS Ports
		          "ICFG": string, // Configuration Storage
		          "MLG":  string, // Maximum LDSUs Allowed for Gateway 80
		          "M2M":  string,
		          // RW
		          "WGPS": string, // GPS Location
		          "WASC": string, // Auto-scan
		          "WSCS": string, // Sensor Cache Status
		          "OBJ" : string  // Newly added
		     }
		   }
		
		B. GET GATEWAY DESCRIPTOR // query-based
		-  Receive:
		   topic: DEVICEID/get_descriptor
		-  Publish:
		   topic: server/DEVICEID/get_descriptor
		   payload: { 
		     'value': { 
		          // RO
		          "UUID": string, // UUID
		          "SNO" : string, // Serial Number
		          "PMAC": string, // PoE MAC ID
		          "WMAC": string, // WiFi MAC ID
		          "MOD" : string, // Model Number
		          "PRV" : string, // Product Version
		          "FWV" : string, // Firmware Version and date
		          "ICAC": string, // Sensor Cache Storage Size
		          "IPRT": string, // Number of LDS Ports
		          "ICFG": string, // Configuration Storage
		          "MLG":  string,  // Maximum LDSUs Allowed for Gateway 80
		          "M2M":  string,
		          // RW
		          "WGPS": string, // GPS Location
		          "WASC": string, // Auto-scan
		          "WSCS": string, // Sensor Cache Status
		          "OBJ" : string  // Newly added
		     }
		   }
		
		C. SET LDSU DESCRIPTORS
		-  Publish:
		   topic: server/DEVICEID/set_ldsu_descs
		   payload: { 
		     'value': [
		         {
		           "IID":  "12345",             // LDSU Instance ID. IID is unique within the GW
		           "PORT": "1",                 // Port number
		           "DID":  "1",                 // LDS device ID from eeprom. DID is unique within the Port

		           "PRV":  "1.0",               // Product version
		           "MFG":  "DDMMYYYY",          // Manufacturing date
		           "SNO":  "BRT12345",          // Serial Number
		           "UID":  "BRTXXXXXXXXXXXXX",  // UUID
		           "NAME": "BRT 4-in-1 Sensor", // Name of the Sensor //"BRT 4-in-1 Sensor", "Thermocouple", "Air Quality Sensor"

		           "OBJ":  "32768"              // LDSU Object type   //"32768", "32769", "32770"
		         },
		         {
		           "IID":  string,
		           "PORT": string,
		           "DID":  string,
		           "PRV":  string,
		           "MFG":  string,
		           "SNO":  string,
		           "UID":  string,
		           "NAME": string,
		           "OBJ":  string,
		         },
		         {
		           "IID":  string,
		           "PORT": string,
		           "DID":  string,
		           "PRV":  string,
		           "MFG":  string,
		           "SNO":  string,
		           "UID":  string,
		           "NAME": string,
		           "OBJ":  string,
		         },
		         ...
		       ],
		     ],
		     "chunk": {
		       "TSEQ": string // total num of chunks in the sequence (ex. 16 chunks)
		       "SEQN": string // sequence number (ex. 0-15)
		       "TOT": string  // total num of LDSUs in the sequence (used for verification)
		     }
		   }
		
		D. GET LDSU DESCRIPTORS
		-  Receive:
		   topic: DEVICEID/get_ldsu_descs
		   payload: {'PORT': string}
		   // port can be "1","2","3". If "0", then query is for all ports
		-  Publish:

		   // This api is used is SCAN LDS BUS
		   // To support multiple chunks, the response is composed of 2 parts:
		   // 1. Send the multiple chunks via set_ldsu_descs
		   // 2. Send the empty response to get_ldsu_descs

		   // PART 1. 
		   // Before sending empty response get_ldsu_descs, send the multiple chunks via set_ldsu_descs
		   topic: server/DEVICEID/set_ldsu_descs
		   payload: { 
		     'value': [
		       {
		         "IID":  "12345",             // LDSU Instance ID
		         "PORT": "1",                 // Port number
		         "DID":  "1",                 // LDS device ID from eeprom
		         "PRV":  "1.0",               // Product version
		         "MFG":  "DDMMYYYY",          // Manufacturing date
		         "SNO":  "BRT12345",          // Serial Number
		         "UID":  "BRTXXXXXXXXXXXXX",  // UUID
		         "NAME": "BRT 4-in-1 Sensor", // Name of the Sensor //"BRT 4-in-1 Sensor", "Thermocouple", "Air Quality Sensor"
		         "OBJ":  "32768"              // LDSU Object type   //"32768", "32769", "32770"
		       },
		       {
		         "IID":  string,
		         "PORT": string,
		         "DID":  string,
		         "PRV":  string,
		         "MFG":  string,
		         "SNO":  string,
		         "UID":  string,
		         "NAME": string,
		         "OBJ":  string,
		       },
		       {
		         "IID":  string,
		         "PORT": string,
		         "DID":  string,
		         "PRV":  string,
		         "MFG":  string,
		         "SNO":  string,
		         "UID":  string,
		         "NAME": string,
		         "OBJ":  string,
		       },
		       ...
		     ],
		     "chunk": {
		       "TSEQ": string // total num of chunks in the sequence (ex. 16 chunks)
		       "SEQN": string // sequence number (ex. 0-15)
		       "TOT": string  // total num of LDSUs in the sequence (used for verification)
		     }
		   }
		   // PART 2. 
		   // After sending the multiple chunks via set_ldsu_descs, need to respond with get_ldsu_descs
		   topic: server/DEVICEID/get_ldsu_descs
		   payload: {}

		E. IDENTIFY LDSU
		-  Receive:
		   topic: DEVICEID/identify_ldsu
		   payload: {'UID': string}
		-  Publish:
		   topic: server/DEVICEID/identify_ldsu
		   payload: {}

		F. ENABLE LDSU DEVICE (SENSOR/ACTUATOR)
		-  Receive:
		   topic: DEVICEID/enable_ldsu_dev
		   payload: 
		   {
		     'enable': int,
		     'UID':    string,
		     'SAID':   string,
		     'MODE':   string
		   }
		-  Publish:
		   topic: server/DEVICEID/enable_ldsu_dev
		   payload: {}


	4. Configurations

		A. REQUEST CONFIGURATION     req_configuration
		-  Publish:
		   topic: server/DEVICEID/req_configuration
		   payload: {}

		B. RECEIVE CONFIGURATION     rcv_configuration
		-  Receive:
		   topic: DEVICEID/rcv_configuration
		   payload: 
		   {
		     'ldsu': [
		       {
		         'enabled': int,
		         'UID':    string,
		         'SAID':   string,
		         'MODE':   string
		       },
		       ...
		     ],
		     'uart': [
		       {
		         'enabled': int,
		         'attributes': {
		           'baudrate': int,
		           'parity': int,
		           'flowcontrol': int,
		           'stopbits': int,
		           'databits': int,
		         }
		       }
		     ]
		   }

		C. DELETE CONFIGURATION      del_configuration


	5. Sensor Reading

		C. PUBLISH SENSOR READING    pub_sensor_reading
		-  Publish:
		   topic: DEVICEID/pub_sensor_reading
		   payload:
		   // NEW
		   {
		     "UID": string, // LDSU UUID
		     "TS":  string, // timestamp in epoch
		     "SNS": [string, ...] // if disabled, use "NaN"
		   }
		
		   // OLD
		   {
		     "timestamp": int,
		     "sensors": { 
		       "i2c1":    [{"class": 0, "value": 1, "address": 1}, ...],
		       "i2c2":    [{"class": 1, "value": 2, "address": 2}, ...],
		       "i2c3":    [{"class": 2, "value": 3, "address": 3}, ...],
		       "i2c4":    [{"class": 3, "value": 4, "address": 4}, ...],
		       "adc1":    [{"class": 0, "value": 1}],
		       "adc2":    [{"class": 1, "value": 2}],
		       "1wire1":  [{"class": 2, "value": 3}],
		       "tprobe1": [{"class": 3, "value": 4, subclass: {"class": 4, "value": 5}}],
		     }
		   }
		   // NOTE: multiple sensor data from different peripherals can be sent at the same time
		   // class is the index of the sensor's class in the array
		      ["speaker", "display", "light", "potentiometer", "temperature", "humidity", "anemometer", "battery", "fluid"]
		   // address is optional and it only applies for I2C
		   // timestamp is optional and it refers to epoch in seconds

		B. RECEIVE SENSOR READING    rcv_sensor_reading
		C. REQUEST SENSOR READING    req_sensor_reading


	6. OTA Firmware Update

		A. API_UPGRADE_FIRMWARE
		-  Receive:
		   topic: DEVICEID/beg_ota
		   payload: 
		   {
		     "location": string, // used to download the firmware via HTTPS
		     "size"    : int,    // used to verify if firmware is complete
		     "version" : string, // used to compare with current firmware version
		     "checksum": int,    // used to verify if firmware is not corrupted
		   }
		   // checksum is computed as CRC32 and is used to verify if the downloaded firmware is not corrupted.
		   // This MQTT packet is sent to device when there is an OTA firmware update triggered/scheduled by user.
		   // Once received, device shall proceed to download the firmware via HTTPS using the REST API "DOWNLOAD FIRMWARE"
		   // Refer to DOWNLOAD FIRMWARE API
		   //   HTTP_HOST: check dev or prod URL
		   //   HTTP_TLS_PORT: 443
		   //   GET /firmware/LOCATION (where LOCATION refers to location parameter in API_UPGRADE_FIRMWARE)
		   // Also refer to the DEVICE SIMULATOR function http_get_firmware_binary() in device_simulator.py

		B. API_UPGRADE_FIRMWARE_COMPLETION 
		-  Publish:
		   topic: server/DEVICEID/end_ota
		   payload: 
		   {
		     "value": {"result": boolean},
		   }
		   // The device shall publish this MQTT packet once the device has downloaded and verified the firmware.

		C. API_REQUEST_OTASTATUS
		-  Publish:
		   topic: server/DEVICEID/req_otastatus
		   payload: 
		   {
		     "version": string
		   }
		   // this MQTT packet should ve called every device bootup to check if device is schedule for OTA update
		   // if device is scheduled for OTA update, device shall receive API_UPGRADE_FIRMWARE call

		D. API_REQUEST_TIME
		-  Publish:
		   topic: server/DEVICEID/req_time
		   payload: {}

		E. API_RECEIVE_TIME
		-  Receive:
		   topic: DEVICEID/rcv_time
		   {
		     "time": string
		   }
		   // this topic is for querying the current epoch time in seconds
		   // device should probably add 1 second to accomodate any transmission delay


	7. Notifications

		A. SEND NOTIFICATION         trigger_notification
		-  Receive:
		   topic: DEVICEID/trigger_notification
		   payload: { "recipient": string, "message": string }
		-  Publish:
		   topic: server/DEVICEID/trigger_notification
		   topic: server/DEVICEID/trigger_notification/uart/MENOS
		   topic: server/DEVICEID/trigger_notification/gpioX/MENOS
		   topic: server/DEVICEID/trigger_notification/i2cX/MENOS
		   // MENOS: mobile, email, notification, modem, storage
		   payload: { "recipient": string, "message": string }

		B. STATUS NOTIFICATION       status_notification
		-  Receive:
		   topic: DEVICEID/status_notification
		   payload: { "status": string }
		   // status is result of the trigger_notification

		C. RECV NOTIFICATION         recv_notification
		-  Receive:
		   topic: DEVICEID/recv_notification
		   payload: { "sender": string, "message": string }
		   // sender is the DEVICEID of the sender device/mOdem


	8. GPIO

		A. GET GPIOS
		-  Receive:
		   topic: DEVICEID/get_gpios
		-  Publish:
		   topic: server/DEVICEID/get_gpios
		   payload: { 
		     'value': { 
		       'voltage': int, 
		       'gpios': [ 
		           {'enabled': int, 'direction': int, 'status': int}, 
		           {'enabled': int, 'direction': int, 'status': int}, 
		           {'enabled': int, 'direction': int, 'status': int}, 
		           {'enabled': int, 'direction': int, 'status': int} 
		       ]
		     }
		   }
		   // voltage is an index of the value in the list of voltages
		   //   ["3.3 V", "5 V"]
		   // enable is an int indicating if disabled (0) or enabled (1)
		   // direction is an index of the value in the list of directions
		   //   ["Input", "Output"]
		   // status is an index of the value in the list of directions
		   //   ["Low", "High"]

		B. GET GPIO PROPERTIES
		-  Receive:
		   topic: DEVICEID/get_gpio_prop
		   payload: { 'number': int }
		-  Publish:
		   topic: server/DEVICEID/get_gpio_prop
		   payload: { 
		     'value': {
		       'direction': int, 
		       'mode': int, 
		       'alert': int, 
		       'alertperiod': int, 
		       'polarity': int, 
		       'width': int, 
		       'mark': int, 
		       'space': int
		       'count': int
		     } 
		   }
		   // direction is an index of the value in the list of directions
		   //     ft900_gpio.h: pad_dir_t
		   //     ["Input", "Output"]
		   // mode is an index of the value in the list of modes
		   //     ft900_gpio.h
		   //     direction == "Input"
		   //       ["High Level", "Low Level", "High Edge", "Low Edge"]
		   //     direction == "Output"
		   //       ["Level", "Clock", "Pulse"]
		   // alert is an index of the value in the list of alerts
		   //     ["Once", "Continuously"]
		   // alert is an optional and is valid only when direction points to Input
		   // alertperiod is optional and is valid only if alert points to Continuously
		   // polarity is an index of the value in the list of polarities
		   //     ft900_gpio.h
		   //     direction == "Output"
		   //       ["Negative", "Positive"]
		   // polarity is optional and is valid only when direction points to Output
		   // width is optional and is valid only when direction points to Output and mode points to Pulse (width (ms) should be > 0)
		   // mark is optional and is valid only when direction points to Output and mode points to Clock (mark (ms) should be > 0)
		   // space is optional and is valid only when direction points to Output and mode points to Clock (space (ms) should be > 0)
		   // count is optional and is valid only when direction points to Output and mode points to Clock (count should be > 0)

		C. SET GPIO PROPERTIES
		-  Receive:
		   topic: DEVICEID/set_gpio_prop
		   payload: {
		       'direction': int, 
		       'mode': int, 
		       'alert': int, 
		       'alertperiod': int, 
		       'polarity': int, 
		       'width': int, 
		       'mark': int, 
		       'space': int,
		       'count': int,
		       'number': int
		   }
		   // direction is an index of the value in the list of directions
		   //     ft900_gpio.h: pad_dir_t
		   //     ["Input", "Output"]
		   // mode is an index of the value in the list of modes
		   //     ft900_gpio.h
		   //     direction == "Input"
		   //       ["High Level", "Low Level", "High Edge", "Low Edge"]
		   //     direction == "Output"
		   //       ["Level", "Clock", "Pulse"]
		   // alert is an index of the value in the list of alerts
		   //     ["Once", "Continuously"]
		   // alert is an optional and is valid only when direction points to Input
		   // alertperiod is optional and is valid only if alert points to Continuously
		   // polarity is an index of the value in the list of polarities
		   //     ft900_gpio.h
		   //     direction == "Output"
		   //       ["Negative", "Positive"]
		   // polarity is optional and is valid only when direction points to Output
		   // width is optional and is valid only when direction points to Output and mode points to Pulse (width (ms) should be > 0)
		   // mark is optional and is valid only when direction points to Output and mode points to Clock (mark (ms) should be > 0)
		   // space is optional and is valid only when direction points to Output and mode points to Clock (space (ms) should be > 0)
		   // count is optional and is valid only when direction points to Output and mode points to Clock (count should be > 0)
		-  Publish:
		   topic: server/DEVICEID/set_gpio_prop
		   payload: {}

		D. ENABLE/DISABLE GPIO
		-  Receive:
		   topic: DEVICEID/enable_gpio
		   payload: { 'enable': int, 'number': int }
		   // enable is an int indicating if disabled (0) or enabled (1)
		-  Publish:
		   topic: server/DEVICEID/enable_gpio
		   payload: {}

		E. GET GPIO VOLTAGE
		-  Receive:
		   topic: DEVICEID/get_gpio_voltage
		-  Publish:
		   topic: server/DEVICEID/get_gpio_voltage
		   payload: { 'value': { 'voltage': int } }
		   // voltage is an index of the value in the list of voltages
		   //   ["3.3 V", "5 V"]

		F. SET GPIO VOLTAGE
		-  Receive:
		   topic: DEVICEID/set_gpio_voltage
		   payload: { 'voltage': int }
		   // voltage is an index of the value in the list of voltages
		   //   ["3.3 V", "5 V"]
		-  Publish:
		   topic: server/DEVICEID/set_gpio_voltage
		   payload: {}


	9. I2C

		A. GET I2CS
		-  Receive:
		   topic: DEVICEID/get_i2cs
		-  Publish:
		   topic: server/DEVICEID/get_i2cs
		   payload: { 
		     'value': { 
		       'i2cs': [ 
		           {'enabled': int}, 
		           {'enabled': int}, 
		           {'enabled': int}, 
		           {'enabled': int} 
		       ]
		     }
		   }
		   // enable is an int indicating if disabled (0) or enabled (1)

		B. GET I2C DEVICES
		-  Receive:
		   topic: DEVICEID/get_i2c_devs
		-  Publish:
		   topic: server/DEVICEID/get_i2c_devs
		   payload: { 
		     'value': { 
		       'i2cs': [ 
		           {
		              address: { 'enabled': 0, 'class': 0, 'attributes': {} },
		           },
		           {
		              address: { 'enabled': 0, 'class': 0, 'attributes': {} },
		           },
		           {
		              address: { 'enabled': 0, 'class': 0, 'attributes': {} },
		           },
		           {
		              address: { 'enabled': 0, 'class': 0, 'attributes': {} },
		           },
		       ]
		     }
		   }
		   // enable is an int indicating if disabled (0) or enabled (1)

		C. GET I2C DEVICE PROPERTIES
		-  Receive:
		   topic: DEVICEID/get_i2c_dev_prop
		   payload: { 'number': int, 'address': int }
		-  Publish:
		   topic: server/DEVICEID/get_i2c_dev_prop
		   payload: { 
		     'value': { TODO:Refer to GET I2C DEVICE PROPERTIES API } 
		   }

		D. SET I2C DEVICE PROPERTIES
		-  Receive:
		   topic: DEVICEID/set_i2c_dev_prop
		   payload: { 
		       'number': int, 
		       'address': int, 
		       'class': string, 
		       ...  TODO:Refer to SET I2C DEVICE PROPERTIES API ...
		   }
		-  Publish:
		   topic: server/DEVICEID/set_i2c_dev_prop
		   payload: {}

		E. ENABLE/DISABLE I2C DEVICE
		-  Receive:
		   topic: DEVICEID/enable_i2c_dev
		   payload: { 'enable': int, 'number': int, 'address': int }
		   // enable is an int indicating if disabled (0) or enabled (1)
		-  Publish:
		   topic: server/DEVICEID/enable_i2c
		   payload: {}

		F. ENABLE/DISABLE I2C
		-  Receive:
		   topic: DEVICEID/enable_i2c
		   payload: { 'enable': int, 'number': int }
		   // enable is an int indicating if disabled (0) or enabled (1)
		-  Publish:
		   topic: server/DEVICEID/enable_i2c
		   payload: {}


	10. ADC

		A. GET ADC DEVICE PROPERTIES
		-  Receive:
		   topic: DEVICEID/get_adc_dev_prop
		   payload: { 'number': int, 'address': int }
		-  Publish:
		   topic: server/DEVICEID/get_adc_dev_prop
		   payload: { 
		     'value': { TODO:Refer to GET ADC DEVICE PROPERTIES API } 
		   }

		B. SET ADC DEVICE PROPERTIES
		-  Receive:
		   topic: DEVICEID/set_adc_dev_prop
		   payload: { 
		       'number': int, 
		       'address': int, 
		       'class': string, 
		       ...  TODO:Refer to SET ADC DEVICE PROPERTIES API ...
		   }
		-  Publish:
		   topic: server/DEVICEID/set_adc_dev_prop
		   payload: {}

		C. ENABLE/DISABLE ADC DEVICE
		-  Receive:
		   topic: DEVICEID/enable_adc_dev
		   payload: { 'enable': int, 'number': int, 'address': int }
		   // enable is an int indicating if disabled (0) or enabled (1)
		-  Publish:
		   topic: server/DEVICEID/enable_adc_dev
		   payload: {}


	11. 1WIRE

		A. GET 1WIRE DEVICE PROPERTIES
		-  Receive:
		   topic: DEVICEID/get_1wire_dev_prop
		   payload: { 'number': int, 'address': int }
		-  Publish:
		   topic: server/DEVICEID/get_1wire_dev_prop
		   payload: { 
		     'value': { TODO:Refer to GET 1WIRE DEVICE PROPERTIES API } 
		   }

		B. SET 1WIRE DEVICE PROPERTIES
		-  Receive:
		   topic: DEVICEID/set_1wire_dev_prop
		   payload: { 
		       'number': int, 
		       'address': int, 
		       'class': string, 
		       ...  TODO:Refer to SET 1WIRE DEVICE PROPERTIES API ...
		   }
		-  Publish:
		   topic: server/DEVICEID/set_1wire_dev_prop
		   payload: {}

		C. ENABLE/DISABLE 1WIRE DEVICE
		-  Receive:
		   topic: DEVICEID/enable_1wire_dev
		   payload: { 'enable': int, 'number': int, 'address': int }
		   // enable is an int indicating if disabled (0) or enabled (1)
		-  Publish:
		   topic: server/DEVICEID/enable_1wire_dev
		   payload: {}


	12. TPROBE

		A. GET TPROBE DEVICE PROPERTIES
		-  Receive:
		   topic: DEVICEID/get_tprobe_dev_prop
		   payload: { 'number': int, 'address': int }
		-  Publish:
		   topic: server/DEVICEID/get_tprobe_dev_prop
		   payload: { 
		     'value': { TODO:Refer to GET TPROBE DEVICE PROPERTIES API } 
		   }

		B. SET TPROBE DEVICE PROPERTIES
		-  Receive:
		   topic: DEVICEID/set_tprobe_dev_prop
		   payload: { 
		       'number': int, 
		       'address': int, 
		       'class': string, 
		       ...  TODO:Refer to SET TPROBE DEVICE PROPERTIES API ...
		   }
		-  Publish:
		   topic: server/DEVICEID/set_tprobe_dev_prop
		   payload: {}

		C. ENABLE/DISABLE TPROBE DEVICE
		-  Receive:
		   topic: DEVICEID/enable_tprobe_dev
		   payload: { 'enable': int, 'number': int, 'address': int }
		   // enable is an int indicating if disabled (0) or enabled (1)
		-  Publish:
		   topic: server/DEVICEID/enable_tprobe_dev
		   payload: {}


	13. Peripherals

		A. GET PERIPHERAL DEVICES    get_devs





