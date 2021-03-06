import ssl
import json
import time
import threading
import pika as amqp
import paho.mqtt.client as mqtt
import random 



###################################################################################
# MQTT and AMQP configurations
###################################################################################

CONFIG_AMQP_SEPARATOR       = '.'
CONFIG_PREPEND_REPLY_TOPIC  = "server"
CONFIG_QOS                  = 1



###################################################################################
# messaging_client
# abstracts MQTT and AMQP implementation
# used by both webserver and device_simulator
###################################################################################
class messaging_client:

    def __init__(self, use_amqp, on_message_callback, device_id=None):
        self.use_amqp = use_amqp
        self.client = None
        self.mqtt_connected = False
        self.amqp_connected = False
        self.on_message_callback = on_message_callback
        self.consume_continuously = False
        self.device_id = device_id
        self.tag = ''.join(["%s" % random.randint(0, 9) for num in range(16)])
        self.host = None
        self.port = None
        self.username = None
        self.password = None
        self.ca = None
        self.cert = None
        self.pkey = None

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

    def initialize(self, timeout=0):
        if self.use_amqp:
            self.client = self.initialize_ampq()
        else:
            self.client = self.initialize_mqtt(timeout)
        return False if self.client is None else True

    def release(self):
        if self.use_amqp:
            self.release_amqp(self.client)
        else:
            self.release_mqtt(self.client)

    def publish(self, topic, payload):
        if self.use_amqp:
            self.publish_ampq(self.client, topic, payload)
        else:
            self.publish_mqtt(self.client, topic, payload)

    def subscribe(self, topic, subscribe=True, declare=False, consume_continuously=False, deviceid=None):
        self.consume_continuously = consume_continuously
        if self.use_amqp:
            return self.subscribe_ampq(self.client, topic, subscribe=subscribe, declare=declare, deviceid=deviceid)
        else:
            return self.subscribe_mqtt(self.client, topic, subscribe=subscribe)

    def is_connected(self):
        if self.use_amqp:
            return self.amqp_connected
        else:
            return self.mqtt_connected

    def initialize_ampq(self):
        use_tls = True
        # Set TLS certificates and access credentials
        if self.username and self.password:
            credentials = amqp.PlainCredentials(self.username, self.password)
        else:
            credentials = None
        ssl_options = None
        if use_tls:
            context = ssl._create_unverified_context()
            #context = ssl.create_default_context(cafile=CONFIG_AMQP_TLS_CA)
            #context.load_cert_chain(CONFIG_AMQP_TLS_CERT, CONFIG_AMQP_TLS_PKEY)
            ssl_options = amqp.SSLOptions(context)
            if credentials:
                parameters = amqp.ConnectionParameters(
                    self.host, 
                    self.port, 
                    credentials=credentials, 
                    ssl_options=ssl_options)
            else:
                parameters = amqp.ConnectionParameters(
                    self.host, 
                    self.port, 
                    ssl_options=ssl_options)
        else:
            if credentials:
                parameters = amqp.ConnectionParameters(
                    self.host, 
                    self.port, 
                    credentials=credentials, 
                    ssl_options=ssl_options)
            else:
                parameters = amqp.ConnectionParameters(
                    self.host, 
                    self.port, 
                    ssl_options=ssl_options)
        # Connect to AMPQ server
        try:
            connection = amqp.BlockingConnection(parameters)
        except:
            self.amqp_connected = False
            return None
        client = connection.channel()
        self.amqp_connected = True
        return client

    def release_amqp(self, client):
        try:
            self.amqp_connected = False
            client.close()
        except:
            pass

    def initialize_mqtt(self, timeout):
        if self.device_id:
            client = mqtt.Client(client_id=self.device_id)
        else:
            client = mqtt.Client()
        client.on_connect = self.on_mqtt_connect
        client.on_disconnect = self.on_mqtt_disconnect
        client.on_message = self.on_mqtt_message
        # Set MQTT credentials
        if self.username and self.password:
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
        except Exception as e:
            print(e)
            client = None

        trial = 0
        while True:
            #print(self.mqtt_connected)
            if self.mqtt_connected:
                break
            time.sleep(1)
            trial += 1
            if timeout > 0 and timeout == trial:
                #print("timeout")
                try:
                    client.disconnect()
                except:
                    pass
                client = None
                break

        return client

    def release_mqtt(self, client):
        try:
            self.mqtt_connected = False
            client.disconnect()
        except:
            pass

    def publish_ampq(self, client, topic, payload):
        print("PUB: topic={} payload={}".format(topic, payload))
        if client:
            client.basic_publish(exchange='amq.topic', routing_key=topic, body=payload.encode("utf-8"))

    def publish_mqtt(self, client, topic, payload):
        print("PUB: topic={} payload={}".format(topic, payload))
        if client:
            client.publish(topic, payload, qos=CONFIG_QOS)

    def subscribe_ampq(self, client, topic, subscribe=True, declare=False, deviceid=None):
        print("SUB: topic={}".format(topic))
        if client:
            if subscribe:
                if deviceid is not None:
                    myqueue = 'mqtt-subscription-{}qos{}'.format(deviceid, CONFIG_QOS)
                    self.device_id = deviceid
                else:
                    myqueue = 'mqtt-subscription-{}qos{}'.format(self.device_id, CONFIG_QOS)

                if declare:
                    client.exchange_declare(exchange='amq.topic', exchange_type='topic', durable=True, auto_delete=False)
                    result = client.queue_declare(queue=myqueue, auto_delete=True)

                try:
                    print("SUB: queue_bind")
                    client.queue_bind(queue=myqueue, exchange='amq.topic', routing_key=topic)
                    print("SUB: basic_consume")
                    client.basic_consume(queue=myqueue, on_message_callback=self.on_amqp_message, consumer_tag=self.tag)
                    x = threading.Thread(target=self.subscribe_amqp_thread, args=(client,))
                    x.start()
                except:
                    print("SUB: exception! Please check if device is connected with correct deviceid=\r\n{}".format(deviceid))
                    return False
        return True

    def subscribe_amqp_thread(self, client):
        print("SUB: thread")
        while True:
            try:
                client.start_consuming()
                break
            except amqp.exceptions.ConnectionClosedByBroker:
                print("ConnectionClosedByBroker")
                time.sleep(1)
                break
            except amqp.exceptions.AMQPChannelError:
                print("AMQPChannelError")
                time.sleep(1)
                break
            except amqp.exceptions.AMQPConnectionError:
                print("AMQPConnectionError")
                time.sleep(1)
                break
        if self.consume_continuously:
            try:
                client.close()
            except:
                pass
            self.amqp_connected = False

    def subscribe_mqtt(self, client, topic, subscribe=True):
        print("SUB: topic={}\n\n".format(topic))
        if client:
            if subscribe:
                try:
                    client.subscribe(topic, qos=CONFIG_QOS)
                except:
                    return False
            else:
                try:
                    client.unsubscribe(topic)
                except:
                    return False
        return True

    def on_mqtt_connect(self, client, userdata, flags, rc):
        print("MQTT Connected with result code " + str(rc))
        self.mqtt_connected = True

    def on_mqtt_disconnect(self, client, userdata, rc):
        print("MQTT Disconnected with result code " + str(rc))
        self.mqtt_connected = False

    def on_mqtt_message(self, client, userdata, msg):
        self.on_message_callback(client, userdata, msg)

    def on_amqp_message(self, ch, method, properties, body):
        self.on_message_callback(ch, method, properties, body)
        if not self.consume_continuously:
            self.client.stop_consuming(consumer_tag=self.tag)
            myqueue = 'mqtt-subscription-{}qos{}'.format(self.device_id, CONFIG_QOS)
            self.client.queue_unbind(queue=myqueue, exchange='amq.topic', routing_key=method.routing_key)
            self.client.basic_cancel(self.tag)


