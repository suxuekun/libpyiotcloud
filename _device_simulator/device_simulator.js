var mqtt = require('mqtt');
var fs = require('fs');
var sleep = require('system-sleep');
const os = require('os');
var ArgumentParser = require('argparse');





var g_device_status = "running";

var g_firmware_version_MAJOR = 0;
var g_firmware_version_MINOR = 1;
var g_firmware_version = (g_firmware_version_MAJOR*100 + g_firmware_version_MINOR);
var g_firmware_version_STR = g_firmware_version_MAJOR.toString() + "." + g_firmware_version_MINOR.toString();

var g_uart_properties = { 'baudrate': 7, 'parity': 0, 'databits': 3, 'stopbits': 0, 'flowcontrol': 0 };
var g_uart_enabled = 1;

var g_gpio_properties = [
    { 'direction': 0, 'mode': 0, 'alert': 0, 'alertperiod':   0, 'polarity': 0, 'width': 0, 'mark': 0, 'space': 0 },
    { 'direction': 0, 'mode': 3, 'alert': 1, 'alertperiod':  60, 'polarity': 0, 'width': 0, 'mark': 0, 'space': 0 },
    { 'direction': 1, 'mode': 0, 'alert': 0, 'alertperiod':   0, 'polarity': 0, 'width': 0, 'mark': 0, 'space': 0 },
    { 'direction': 1, 'mode': 2, 'alert': 1, 'alertperiod': 120, 'polarity': 1, 'width': 0, 'mark': 1, 'space': 2 } ];
var g_gpio_voltage = 1;
var g_gpio_enabled = [1, 1, 1, 1];
var g_gpio_status = [0, 1, 0, 1];

var g_i2c_properties = [
    {
        '0': { 'class': 0, 'attributes': {} },
    },
    {
        '0': { 'class': 0, 'attributes': {} },
    },
    {
        '0': { 'class': 0, 'attributes': {} },
    },
    {
        '0': { 'class': 0, 'attributes': {} },
    }
];
var g_i2c_enabled = [1, 1, 1, 1];




// UART notification configuration
var CONFIG_NOTIFICATION_UART_KEYWORD = "Hello World";
var CONFIG_NOTIFICATION_RECIPIENT   = "richmond.umagat@brtchip.com";
var CONFIG_NOTIFICATION_MESSAGE    = "Hi, How are you today?";

// default configurations
var CONFIG_DEVICE_ID     = "";
var CONFIG_USERNAME      = null;
var CONFIG_PASSWORD      = null;
var CONFIG_TLS_CA        = "../cert/rootca.pem";
var CONFIG_TLS_CERT      = "../cert/ft900device1_cert.pem";
var CONFIG_TLS_PKEY      = "../cert/ft900device1_pkey.pem";
var CONFIG_HOST          = "localhost";
var CONFIG_MQTT_TLS_PORT = 8883;
var CONFIG_PREPEND_REPLY_TOPIC  = "server/";



console.log("\n\n");
console.log("Copyright (C) Bridgetek Pte Ltd");
console.log("-------------------------------------------------------");
console.log("Welcome to IoT Device Controller example...\n");
console.log("Demonstrate remote access of FT900 via Bridgetek IoT Cloud");
console.log("-------------------------------------------------------");

// parse arguments
var parser = new ArgumentParser.ArgumentParser({addHelp:true});
parser.addArgument(['--USE_DEVICE_ID'],   {help: 'Device ID to use'});
parser.addArgument(['--USE_DEVICE_CA'],   {help: 'Device CA certificate to use'});
parser.addArgument(['--USE_DEVICE_CERT'], {help: 'Device certificate to use'});
parser.addArgument(['--USE_DEVICE_PKEY'], {help: 'Device private key to use'});
parser.addArgument(['--USE_HOST'],        {help: 'Host server to connect to'});
parser.addArgument(['--USE_PORT'],        {help: 'Host port to connect to'});
parser.addArgument(['--USE_USERNAME'],    {help: 'Username to use in connection'});
parser.addArgument(['--USE_PASSWORD'],    {help: 'Password to use in connection'});

var args = parser.parseArgs();
if (args.USE_DEVICE_ID != null) {
    CONFIG_DEVICE_ID = args.USE_DEVICE_ID;
}
if (args.USE_DEVICE_CA != null) {
    CONFIG_TLS_CA = args.USE_DEVICE_CA;
}
if (args.USE_DEVICE_CERT != null) {
    CONFIG_TLS_CERT = args.USE_DEVICE_CERT;
}
if (args.USE_DEVICE_PKEY != null) {
    CONFIG_TLS_PKEY = args.USE_DEVICE_PKEY;
}
if (args.USE_HOST != null) {
    CONFIG_HOST = args.USE_HOST;
}
if (args.USE_PORT != null) {
    CONFIG_MQTT_TLS_PORT = parseInt(args.USE_PORT);
}
if (args.USE_USERNAME != null && args.USE_USERNAME.length > 0) {
    CONFIG_USERNAME = args.USE_USERNAME;
}
if (args.USE_PASSWORD != null && args.USE_PASSWORD.length > 0) {
    CONFIG_PASSWORD = args.USE_PASSWORD;
}


console.log("\nFIRMWARE VERSION = " + g_firmware_version_STR + " (" + g_firmware_version.toString() + ")");

console.log("\nTLS CERTIFICATES");
console.log("ca:   " + CONFIG_TLS_CA);
console.log("cert: " + CONFIG_TLS_CERT);
console.log("pkey: " + CONFIG_TLS_PKEY);

console.log("\nMQTT CREDENTIALS");
console.log("host: " + CONFIG_HOST + ":" + CONFIG_MQTT_TLS_PORT);
console.log("id:   " + CONFIG_DEVICE_ID);
console.log("user: " + CONFIG_USERNAME);
console.log("pass: " + CONFIG_PASSWORD);


// connect to server
var options = 
{
    host:               CONFIG_HOST,
    port:               CONFIG_MQTT_TLS_PORT,
    protocol:           'mqtts',
    protocolId:         'MQIsdp',
    ca:                 fs.readFileSync(CONFIG_TLS_CA),
    cert:               fs.readFileSync(CONFIG_TLS_CERT),
    key:                fs.readFileSync(CONFIG_TLS_PKEY),
    secureProtocol:     'TLSv1_2_method',
    protocolVersion:    3,
    rejectUnauthorized: false,
    username:           CONFIG_USERNAME,
    password:           CONFIG_PASSWORD,
    clientId:           CONFIG_DEVICE_ID
};
var client  = mqtt.connect(options);

// subscribe to topic
var subscribed = false
var subtopic = CONFIG_DEVICE_ID + "/"

// handle connection
client.on("connect", function()
{
    if (client.connected == true) {
        console.log("\nMQTT CONNECTED");

        if (subscribed == false) {
            var topic = subtopic + "#";
            console.log("\nSUB: " + topic);
            result = client.subscribe(topic, {qos:1} );
            //console.log(result);
            subscribed = true;
            console.log("\nDevice is now ready! Control this device from IoT Portal https://" + CONFIG_HOST);
        }
    }
    else {
        console.log("connected  "+ client.connected);
    }
});

function setClassAttributes(device_class, class_attributes) 
{
    var attributes = null;
    if (class_attributes.number != null) {
        delete class_attributes["number"];
    }
    if (class_attributes.class != null) {
        delete class_attributes["class"];
    }
    if (class_attributes.address != null) {
        delete class_attributes["address"];
    }
    attributes = class_attributes
    return attributes
}

// handle API call
function handle_api(api, topic, payload) 
{
    console.log("\r\n" + topic + "\r\n" + payload);


    ////////////////////////////////////////////////////
    // GET/SET STATUS
    ////////////////////////////////////////////////////
    if (api == "get_status") {
        pubtopic = CONFIG_PREPEND_REPLY_TOPIC + topic;
        var obj = {
            "value": { "status": g_device_status, "version": g_firmware_version_STR }
        };
        client.publish(pubtopic, JSON.stringify(obj));
    }
    else if (api == "set_status") {
        pubtopic = CONFIG_PREPEND_REPLY_TOPIC + topic;
        var obj = JSON.parse(payload);

        var value = obj.value;
        if (value == "restart") {
            g_device_status = "restarting";
        }
        else if (value == "stop") {
            g_device_status = "stopping";
        }
        else if (value == "start") {
            g_device_status = "starting";
        }

        var obj = {
            "value": g_device_status
        };
        client.publish(pubtopic, JSON.stringify(obj));
    }


    ////////////////////////////////////////////////////
    // UART
    ////////////////////////////////////////////////////
    else if (api == "get_uart_properties") {
        pubtopic = CONFIG_PREPEND_REPLY_TOPIC + topic;
        var obj = JSON.parse(payload);

        var response = { "value": g_uart_properties };
        client.publish(pubtopic, JSON.stringify(response));

        console.log(pubtopic);
        console.log(JSON.stringify(response));
    }
    else if (api == "set_uart_properties") {
        pubtopic = CONFIG_PREPEND_REPLY_TOPIC + topic;
        var obj = JSON.parse(payload);

        g_uart_properties = {
            "baudrate"    : Number(obj.baudrate), 
            "parity"      : Number(obj.parity),
            "databits"    : Number(obj.databits),
            "stopbits"    : Number(obj.stopbits),
            "flowcontrol" : Number(obj.flowcontrol)
        };
        var response = {};
        client.publish(pubtopic, JSON.stringify(response));

        console.log(pubtopic);
        console.log(JSON.stringify(response));
    }
    else if (api == "enable_uart") {
        pubtopic = CONFIG_PREPEND_REPLY_TOPIC + topic;
        var obj = JSON.parse(payload);

        g_uart_enabled = obj.enable

        var response = {};
        client.publish(pubtopic, JSON.stringify(response));
        console.log(g_uart_enabled);

        console.log(pubtopic);
        console.log(JSON.stringify(response));
    }
    else if (api == "get_uarts") {
        pubtopic = CONFIG_PREPEND_REPLY_TOPIC + topic;
        var response = {
            'value': {
                'uarts': [
                    {'enabled': g_uart_enabled },
                ]
            }
        }
        client.publish(pubtopic, JSON.stringify(response));

        console.log(pubtopic);
        console.log(JSON.stringify(response));
    }


    ////////////////////////////////////////////////////
    // GPIO
    ////////////////////////////////////////////////////
    else if (api == "get_gpio_properties") {
        pubtopic = CONFIG_PREPEND_REPLY_TOPIC + topic;
        var obj = JSON.parse(payload);
        var number = Number(obj.number)-1;

        console.log(number);
        var response = { "value": g_gpio_properties[number] };
        client.publish(pubtopic, JSON.stringify(response));

        console.log(pubtopic);
        console.log(JSON.stringify(response));
    }
    else if (api == "set_gpio_properties") {
        pubtopic = CONFIG_PREPEND_REPLY_TOPIC + topic;
        var obj = JSON.parse(payload);
        var number = Number(obj.number)-1;
        console.log(number);

        g_gpio_properties[number] = {
            "direction"  : Number(obj.direction),
            "mode"       : Number(obj.mode),
            "alert"      : Number(obj.alert),
            "alertperiod": Number(obj.alertperiod),
            "polarity"   : Number(obj.polarity),
            "width"      : Number(obj.width),
            "mark"       : Number(obj.mark),
            "space"      : Number(obj.space)
        };
        var response = {};
        client.publish(pubtopic, JSON.stringify(response));

        console.log(pubtopic);
        console.log(JSON.stringify(response));
    }
    else if (api == "get_gpio_voltage") {
        pubtopic = CONFIG_PREPEND_REPLY_TOPIC + topic;
        var response = { "value": { "voltage": g_gpio_voltage } };
        client.publish(pubtopic, JSON.stringify(response));

        console.log(pubtopic);
        console.log(JSON.stringify(response));
    }
    else if (api == "set_gpio_voltage") {
        pubtopic = CONFIG_PREPEND_REPLY_TOPIC + topic;
        var obj = JSON.parse(payload);
        g_gpio_voltage = Number(obj.voltage);
        console.log(g_gpio_voltage);

        var response = {};
        client.publish(pubtopic, JSON.stringify(response));

        console.log(pubtopic);
        console.log(JSON.stringify(response));
    }
    else if (api == "enable_gpio") {
        pubtopic = CONFIG_PREPEND_REPLY_TOPIC + topic;
        var obj = JSON.parse(payload);

        g_gpio_enabled[Number(obj.number)-1] = obj.enable

        var response = {};
        client.publish(pubtopic, JSON.stringify(response));
        console.log(g_gpio_enabled);

        console.log(pubtopic);
        console.log(JSON.stringify(response));
    }
    else if (api == "get_gpios") {
        pubtopic = CONFIG_PREPEND_REPLY_TOPIC + topic;
        var response = {
            'value': {
                'voltage': g_gpio_voltage,
                'gpios': [
                    {'direction': g_gpio_properties[0]['direction'], 'status': g_gpio_status[0], 'enabled': g_gpio_enabled[0] },
                    {'direction': g_gpio_properties[1]['direction'], 'status': g_gpio_status[1], 'enabled': g_gpio_enabled[1] },
                    {'direction': g_gpio_properties[2]['direction'], 'status': g_gpio_status[2], 'enabled': g_gpio_enabled[2] },
                    {'direction': g_gpio_properties[3]['direction'], 'status': g_gpio_status[3], 'enabled': g_gpio_enabled[3] }
                ]
            }
        }
        client.publish(pubtopic, JSON.stringify(response));

        console.log(pubtopic);
        console.log(JSON.stringify(response));
    }

    ////////////////////////////////////////////////////
    // I2C
    ////////////////////////////////////////////////////
    else if (api == "get_i2c_device_properties") {
        pubtopic = CONFIG_PREPEND_REPLY_TOPIC + topic;
        var obj = JSON.parse(payload);
        var number = Number(obj.number)-1;
        var address = Number(obj.address).toString();
        var value = null;
        console.log(number);

        if (g_i2c_properties[number][address] != null) {
            value = g_i2c_properties[number][address]["attributes"];
            console.log("");
            console.log(value);
            console.log("");
        }

        var response = {};
        if (value != null) {
            response["value"] = value;
        }
        client.publish(pubtopic, JSON.stringify(response));
        console.log(pubtopic);
        console.log(JSON.stringify(response));
    }
    else if (api == "set_i2c_device_properties") {
        pubtopic = CONFIG_PREPEND_REPLY_TOPIC + topic;
        var obj = JSON.parse(payload);
        var number = Number(obj.number)-1;
        var address = Number(obj.address).toString();
        var device_class = obj.class;
        console.log(number);

        g_i2c_properties[number][address] = {
            "class"      : device_class,
            "attributes" : setClassAttributes(device_class, obj)
        };
        console.log("");
        console.log(g_i2c_properties[number]);
        console.log("");

        var response = {};
        client.publish(pubtopic, JSON.stringify(response));
        console.log(pubtopic);
        console.log(JSON.stringify(response));
    }
    else if (api == "enable_i2c") {
        pubtopic = CONFIG_PREPEND_REPLY_TOPIC + topic;
        var obj = JSON.parse(payload);

        g_i2c_enabled[Number(obj.number)-1] = obj.enable

        var response = {};
        client.publish(pubtopic, JSON.stringify(response));
        console.log(g_i2c_enabled);

        console.log(pubtopic);
        console.log(JSON.stringify(response));
    }
    else if (api == "get_i2cs") {
        pubtopic = CONFIG_PREPEND_REPLY_TOPIC + topic;
        var response = {
            'value': {
                'i2cs': [
                    {'enabled': g_i2c_enabled[0] },
                    {'enabled': g_i2c_enabled[1] },
                    {'enabled': g_i2c_enabled[2] },
                    {'enabled': g_i2c_enabled[3] }
                ]
            }
        }
        client.publish(pubtopic, JSON.stringify(response));

        console.log(pubtopic);
        console.log(JSON.stringify(response));
    }

    ////////////////////////////////////////////////////
    // OTHERS
    ////////////////////////////////////////////////////
    else if (api == "write_uart") {
        pubtopic = CONFIG_PREPEND_REPLY_TOPIC + topic;
        var obj = JSON.parse(payload);
        console.log(obj.value);

        // Trigger an Email/SMS notification when the UART message received contains a specific phrase!
        if (obj.value.includes(CONFIG_NOTIFICATION_UART_KEYWORD)) {
            console.log("Keyword detected on message!");
            var deviceid = (topic.split("/", 1))[0];
            var topicX = CONFIG_PREPEND_REPLY_TOPIC + deviceid + "/" + "trigger_notification";
            var payloadX = {
                "recipient": CONFIG_NOTIFICATION_RECIPIENT,
                "message": CONFIG_NOTIFICATION_MESSAGE
            }
            client.publish(topicX, JSON.stringify(payloadX));
            console.log("Notification triggered to email/SMS recipient!");
        }
        client.publish(pubtopic, JSON.stringify(obj));
    }
    else if (api == "trigger_notification"){
        pubtopic = CONFIG_PREPEND_REPLY_TOPIC + topic;
        client.publish(pubtopic, payload);
        console.log("Notification triggered to email/SMS recipient!");
    }
    else if (api == "get_gpio") {
        pubtopic = CONFIG_PREPEND_REPLY_TOPIC + topic;
        var obj = JSON.parse(payload);
        var number = Number(obj.number);
        var obj = {
            "number": number,
            "value": Number(0)
        };
        client.publish(pubtopic, JSON.stringify(obj));
        
        console.log(pubtopic);
        console.log(JSON.stringify(obj));
    }
    else if (api == "set_gpio") {
        pubtopic = CONFIG_PREPEND_REPLY_TOPIC + topic;
        var obj = JSON.parse(payload);
        var number = Number(obj.number);
        var value = Number(obj.value);
        var obj = {
            "number": number,
            "value": value
        };
        client.publish(pubtopic, JSON.stringify(obj));
        
        console.log(pubtopic);
        console.log(JSON.stringify(obj));
    }
    else if (api == "get_rtc") {
        pubtopic = CONFIG_PREPEND_REPLY_TOPIC + topic;
        var epoch = Math.trunc((new Date).getTime()/1000);
        console.log(epoch);
        var obj = {
            "value": epoch
        };
        client.publish(pubtopic, JSON.stringify(obj));
        
        console.log(pubtopic);
        console.log(JSON.stringify(obj));
    }
    else if (api == "set_rtc") {
        pubtopic = CONFIG_PREPEND_REPLY_TOPIC + topic;
        var obj = JSON.parse(payload);
        var value = Number(obj.value);
        console.log(value);
        var obj = {
            "value": value
        };
        client.publish(pubtopic, JSON.stringify(obj));
        
        console.log(pubtopic);
        console.log(JSON.stringify(obj));
    }
    else if (api == "get_mac") {
        pubtopic = CONFIG_PREPEND_REPLY_TOPIC + topic;

        value = ""
        interfaces = os.networkInterfaces()
        var found = false
        for (var devName in interfaces) {
            if (devName.includes("Loopback") == true) {
                continue;
            }
            else if (devName.includes("VirtualBox") == true) {
                continue;
            }
            else if (devName.includes("VMWare") == true || devName.includes("VMware") == true) {
                continue;
            }
            var iface = interfaces[devName];
            for (var i = 0; i < iface.length; i++) {
                var alias = iface[i];
                if (alias.family === 'IPv4') {
                    value = alias.mac
                    found = true;
                    break;
                }
            }
            if (found == true) {
                break;
            }
        }
        console.log(value);
        var obj = {
            "value": value
        };

        client.publish(pubtopic, JSON.stringify(obj));
        
        console.log(pubtopic);
        console.log(JSON.stringify(obj));
    }
    else if (api == "get_ip") {
        pubtopic = CONFIG_PREPEND_REPLY_TOPIC + topic;

        value = ""
        interfaces = os.networkInterfaces()
        var found = false
        for (var devName in interfaces) {
            if (devName.includes("Loopback") == true) {
                continue;
            }
            else if (devName.includes("VirtualBox") == true) {
                continue;
            }
            else if (devName.includes("VMWare") == true || devName.includes("VMware") == true) {
                continue;
            }
            var iface = interfaces[devName];
            for (var i = 0; i < iface.length; i++) {
                var alias = iface[i];
                if (alias.family === 'IPv4') {
                    value = alias.address
                    found = true;
                    break;
                }
            }
            if (found == true) {
                break;
            }
        }
        console.log(value);
        var obj = {
            "value": value
        };

        client.publish(pubtopic, JSON.stringify(obj));
        
        console.log(pubtopic);
        console.log(JSON.stringify(obj));
    }
    else if (api == "get_subnet") {
        pubtopic = CONFIG_PREPEND_REPLY_TOPIC + topic;

        value = ""
        interfaces = os.networkInterfaces()
        var found = false
        for (var devName in interfaces) {
            if (devName.includes("Loopback") == true) {
                continue;
            }
            else if (devName.includes("VirtualBox") == true) {
                continue;
            }
            else if (devName.includes("VMWare") == true || devName.includes("VMware") == true) {
                continue;
            }
            var iface = interfaces[devName];
            for (var i = 0; i < iface.length; i++) {
                var alias = iface[i];
                if (alias.family === 'IPv4') {
                    value = alias.netmask
                    found = true;
                    break;
                }
            }
            if (found == true) {
                break;
            }
        }
        console.log(value);
        var obj = {
            "value": value
        };

        client.publish(pubtopic, JSON.stringify(obj));
        
        console.log(pubtopic);
        console.log(JSON.stringify(obj));
    }
    else if (api == "get_gateway") {
        pubtopic = CONFIG_PREPEND_REPLY_TOPIC + topic;

        value = ""
        interfaces = os.networkInterfaces()
        var found = false
        for (var devName in interfaces) {
            if (devName.includes("Loopback") == true) {
                continue;
            }
            else if (devName.includes("VirtualBox") == true) {
                continue;
            }
            else if (devName.includes("VMWare") == true || devName.includes("VMware") == true) {
                continue;
            }
            var iface = interfaces[devName];
            for (var i = 0; i < iface.length; i++) {
                var alias = iface[i];
                if (alias.family === 'IPv4') {
                    index = alias.cidr.indexOf("/");
                    value = alias.cidr.substring(0, index)
                    found = true;
                    break;
                }
            }
            if (found == true) {
                break;
            }
        }
        console.log(value);
        var obj = {
            "value": value
        };

        client.publish(pubtopic, JSON.stringify(obj));
        
        console.log(pubtopic);
        console.log(JSON.stringify(obj));
    }
    else {
        console.log("UNSUPPORTED");
    }
} 

// handle incoming messages
client.on('message', function(topic, message, packet) 
{
    var expected_topic = subtopic;

    if (expected_topic == topic.substring(0, expected_topic.length)) {
        api = topic.substring(expected_topic.length, topic.length);
        //console.log(api);
        
        handle_api(api, topic, message)
    }
});

// handle errors
client.on("error", function(error)
{
    console.log("Can't connect" + error);
    process.exit(1)
});

function process_restart() {
    if (g_device_status === "restarting") {
        console.log("\nDevice will be stopped in 3 seconds");
        for (var i = 0; i < 3; i++) {
            sleep(1000);
            console.log(".");
        }
        sleep(1000);
        g_device_status = "running"
        console.log("Device restarted successfully!\n");
    }
}

function process_stop() {
    if (g_device_status === "stopping") {
        console.log("\nDevice will be stopped in 3 seconds");
        for (var i = 0; i < 3; i++) {
            sleep(1000);
            console.log(".");
        }
        sleep(1000);
        g_device_status = "stopped"
        console.log("Device stopped successfully!\n");
    }
}

function process_start() {
    if (g_device_status === "starting") {
        console.log("\nDevice will be started in 3 seconds");
        for (var i = 0; i < 3; i++) {
            sleep(1000);
            console.log(".");
        }
        sleep(1000);
        g_device_status = "running"
        console.log("Device started successfully!\n");
    }
}

while (true)
{
    sleep(1000);
    if (g_device_status === "restarting") {
        process_restart()
    }
    else if (g_device_status === "stopping") {
        process_stop()
    }
    else if (g_device_status === "starting") {
        process_start()
    }
}

console.log("end")