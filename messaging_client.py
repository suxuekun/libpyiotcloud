import ssl
import json
import time
import threading
import pika as amqp
import paho.mqtt.client as mqtt



###################################################################################
# MQTT and AMQP configurations
###################################################################################

CONFIG_AMQP_SEPARATOR       = '.'
CONFIG_PREPEND_REPLY_TOPIC  = "server"
CONFIG_QOS                  = 1



###################################################################################
# messaging_client
# abstracts MQTT and AMPQ implementation
# used by both webserver and device_simulator
###################################################################################
class messaging_client:

    def __init__(self, use_amqp, on_message_callback, device_name=None):
        self.use_amqp = use_amqp
        self.client = None
        self.mqtt_connected = False
        self.on_message_callback = on_message_callback
        self.consume_continuously = False
        self.device_name = device_name

    def set_server(self, host, port):
        self.host = host
        self.port = port

    def set_user_pass(self, username, password):
        self.username = username
        self.password = password

    def set_tls(self, ca, cert, pkey):
        self.ca = ca
        self.cert = cert
        self.pkey = pkey

    def initialize(self):
        if self.use_amqp:
            self.client = self.initialize_ampq()
        else:
            self.client = self.initialize_mqtt()

    def publish(self, topic, payload):
        if self.use_amqp:
            self.publish_ampq(self.client, topic, payload)
        else:
            self.publish_mqtt(self.client, topic, payload)

    def subscribe(self, topic, subscribe=True, declare=False, consume_continuously=False):
        self.consume_continuously = consume_continuously
        if self.use_amqp:
            self.subscribe_ampq(self.client, topic, subscribe=subscribe, declare=declare)
        else:
            self.subscribe_mqtt(self.client, topic, subscribe=subscribe)

    def initialize_ampq(self):
        use_tls = True
        # Set TLS certificates and access credentials
        credentials = amqp.PlainCredentials(self.username, self.password)
        ssl_options = None
        if use_tls:
            context = ssl._create_unverified_context()
            #context = ssl.create_default_context(cafile=CONFIG_AMQP_TLS_CA)
            #context.load_cert_chain(CONFIG_AMQP_TLS_CERT, CONFIG_AMQP_TLS_PKEY)
            ssl_options = amqp.SSLOptions(context) 
            parameters = amqp.ConnectionParameters(
                self.host, 
                self.port, 
                credentials=credentials, 
                ssl_options=ssl_options)
        else:
            parameters = amqp.ConnectionParameters(
                self.host, 
                self.port, 
                credentials=credentials, 
                ssl_options=ssl_options)
        # Connect to AMPQ server
        connection = amqp.BlockingConnection(parameters)
        client = connection.channel()
        return client

    def initialize_mqtt(self):
        if self.device_name:
            client = mqtt.Client(client_id=self.device_name)
        else:
            client = mqtt.Client()
        client.on_connect = self.on_mqtt_connect
        client.on_message = self.on_mqtt_message
        # Set MQTT credentials
        client.username_pw_set(self.username, self.password)
        # Set TLS certificates
        client.tls_set(ca_certs = self.ca,
            certfile    = self.cert,
            keyfile     = self.pkey,
            cert_reqs   = ssl.CERT_REQUIRED,
            tls_version = ssl.PROTOCOL_TLSv1_2,
            ciphers=None)
        # handle issue: 
        #   hostname doesn't match xxxx
        client.tls_insecure_set(True)
        # handle issues: 
        #   MQTT server is down OR 
        #   invalid MQTT crendentials OR 
        #   invalid TLS certificates
        try:
            client.connect(self.host, self.port)
            client.loop_start()
        except:
            client = None

        while True:
            #print(self.mqtt_connected)
            if self.mqtt_connected:
                break
            time.sleep(1)

        return client

    def publish_ampq(self, client, topic, payload):
        print("PUB: topic={} payload={}".format(topic, payload))
        if client:
            client.basic_publish(exchange='amq.topic', routing_key=topic, body=payload.encode("utf-8"))

    def publish_mqtt(self, client, topic, payload):
        print("PUB: topic={} payload={}".format(topic, payload))
        if client:
            client.publish(topic, payload, qos=CONFIG_QOS)

    def subscribe_ampq(self, client, topic, subscribe=True, declare=False):
        print("SUB: topic={}".format(topic))
        if client:
            if subscribe:
                if CONFIG_PREPEND_REPLY_TOPIC == '':
                    index = 0
                else:
                    index = len(CONFIG_PREPEND_REPLY_TOPIC)+1
                index += topic[index:].index(CONFIG_AMQP_SEPARATOR)
                index2 = index + 1 + topic[index+1:].index(CONFIG_AMQP_SEPARATOR)
                device_name = topic[index+1:index2]
                myqueue = 'mqtt-subscription-{}qos{}'.format(device_name, CONFIG_QOS)

                if declare:
                    client.exchange_declare(exchange='amq.topic', exchange_type='topic', durable=True, auto_delete=False)
                    result = client.queue_declare(queue=myqueue, auto_delete=True)
                client.queue_bind(queue=myqueue, exchange='amq.topic', routing_key=topic)

                client.basic_consume(queue=myqueue, on_message_callback=self.on_amqp_message)
                x = threading.Thread(target=self.subscribe_amqp_thread, args=(client,))
                x.start()

    def subscribe_amqp_thread(self, client):
        while True:
            try:
                client.start_consuming()
                break
            except amqp.exceptions.ConnectionClosedByBroker:
                print("ConnectionClosedByBroker")
                time.sleep(1)
                continue
            except amqp.exceptions.AMQPChannelError:
                print("AMQPChannelError")
                time.sleep(1)
                continue
            except amqp.exceptions.AMQPConnectionError:
                print("AMQPConnectionError")
                time.sleep(1)
                continue

    def subscribe_mqtt(self, client, topic, subscribe=True):
        print("SUB: topic={}".format(topic))
        if client:
            if subscribe:
                client.subscribe(topic, qos=CONFIG_QOS)
            else:
                client.unsubscribe(topic)

    def on_mqtt_connect(self, client, userdata, flags, rc):
        print("MQTT Connected with result code " + str(rc))
        self.mqtt_connected = True

    def on_mqtt_message(self, client, userdata, msg):
        self.on_message_callback(client, userdata, msg)

    def on_amqp_message(self, ch, method, properties, body):
        self.on_message_callback(ch, method, properties, body)
        if not self.consume_continuously:
            self.client.stop_consuming()

