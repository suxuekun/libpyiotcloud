var mqtt = require('mqtt');
var fs = require('fs');
var sleep = require('system-sleep');
const os = require('os');
var ArgumentParser = require('argparse');



// UART notification configuration
var CONFIG_NOTIFICATION_UART_KEYWORD = "Hello World"
var CONFIG_NOTIFICATION_RECIPIENT   = "richmond.umagat@brtchip.com"
var CONFIG_NOTIFICATION_MESSAGE    = "Hi, How are you today?"

// default configurations
var CONFIG_DEVICE_ID     = ""
var CONFIG_USERNAME      = null
var CONFIG_PASSWORD      = null
var CONFIG_TLS_CA        = "../cert/rootca.pem"
var CONFIG_TLS_CERT      = "../cert/ft900device1_cert.pem"
var CONFIG_TLS_PKEY      = "../cert/ft900device1_pkey.pem"
var CONFIG_HOST          = "localhost"
var CONFIG_MQTT_TLS_PORT = 8883
var CONFIG_PREPEND_REPLY_TOPIC  = "server/"



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
    console.log(CONFIG_DEVICE_ID);
}
if (args.USE_DEVICE_CA != null) {
    CONFIG_TLS_CA = args.USE_DEVICE_CA;
    console.log(CONFIG_TLS_CA);
}
if (args.USE_DEVICE_CERT != null) {
    CONFIG_TLS_CERT = args.USE_DEVICE_CERT;
    console.log(CONFIG_TLS_CERT);
}
if (args.USE_DEVICE_PKEY != null) {
    CONFIG_TLS_PKEY = args.USE_DEVICE_PKEY;
    console.log(CONFIG_TLS_PKEY);
}
if (args.USE_HOST != null) {
    CONFIG_HOST = args.USE_HOST;
    console.log(CONFIG_HOST);
}
if (args.USE_PORT != null) {
    CONFIG_MQTT_TLS_PORT = parseInt(args.USE_PORT);
    console.log(CONFIG_MQTT_TLS_PORT);
}
if (args.USE_USERNAME != null) {
    CONFIG_USERNAME = args.USE_USERNAME;
    console.log(CONFIG_USERNAME);
}
if (args.USE_PASSWORD != null) {
    CONFIG_PASSWORD = args.USE_PASSWORD;
    console.log(CONFIG_PASSWORD);
}


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
        if (subscribed == false) {
            var topic = subtopic + "#";
            console.log("subscribing " + topic);
            result = client.subscribe(topic, {qos:1} );
			//console.log(result);
            subscribed = true;
        }
    }
    else {
        console.log("connected  "+ client.connected);
    }
});

// handle API call
function handle_api(api, topic, payload) {
	console.log("\r\n" + topic);

    if (api == "get_status") {		
        pubtopic = CONFIG_PREPEND_REPLY_TOPIC + topic;
        var obj = {
            "value": "running"
        };
        client.publish(pubtopic, JSON.stringify(obj));

		console.log(pubtopic);
		console.log(JSON.stringify(obj));
    }
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
    else if (api == "set_status") {
        pubtopic = CONFIG_PREPEND_REPLY_TOPIC + topic;
        var obj = JSON.parse(payload);
        var value = obj.value;
        console.log(value);
        var obj = {
            "value": "restarting"
        };
        client.publish(pubtopic, JSON.stringify(obj));
		
		console.log(pubtopic);
		console.log(JSON.stringify(obj));		
    }
    else {
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

while (true)
{
    sleep(1000);
}

console.log("end")