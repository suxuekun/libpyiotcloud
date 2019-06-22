import ssl
import json
import time
import threading



CONFIG_USE_AMPQ = True
if CONFIG_USE_AMPQ:
    import pika as amqp
else:
    import paho.mqtt.client as mqtt



###################################################################################
# global variables
###################################################################################

g_messaging_client = None
g_mqtt_connect = False


###################################################################################
# MQTT and AMPQ configurations
###################################################################################

CONFIG_CUSTOMER_ID          = "richmond_umagat@brtchip_com"
CONFIG_DEVICE_NAME          = "ft900device1"

CONFIG_MQTT_USERNAME        = "guest"
CONFIG_MQTT_PASSWORD        = "guest"
CONFIG_MQTT_TLS_CA          = "cert/rootca.pem"
CONFIG_MQTT_TLS_CERT        = "cert/ft900device1_cert.pem"
CONFIG_MQTT_TLS_PKEY        = "cert/ft900device1_pkey.pem"
CONFIG_MQTT_HOST            = "localhost"
CONFIG_MQTT_TLS_PORT        = 8883

CONFIG_AMPQ_TLS_CA          = "cert/rootca.pem"
CONFIG_AMPQ_TLS_CERT        = "cert/ft900device1_cert.pem"
CONFIG_AMPQ_TLS_PKEY        = "cert/ft900device1_pkey.pem"
CONFIG_AMPQ_HOST            = "localhost"
CONFIG_AMPQ_TLS_PORT        = 5671
CONFIG_AMPQ_PORT            = 5672

CONFIG_PREPEND_REPLY_TOPIC  = ""
CONFIG_QOS                  = 1



###################################################################################
# Messaging client functions and callback handlers
###################################################################################

def on_mqtt_connect(client, userdata, flags, rc):
    global g_mqtt_connect
    print("MQTT Connected with result code " + str(rc))
    g_mqtt_connect = True

def on_mqtt_message(client, userdata, msg):
    print("MQTT Recv {}".format(userdata))
    print("MQTT Recv {}".format(msg.topic))
    print("MQTT Recv {}".format(msg.payload))

    expected_topic = "{}/{}/".format(CONFIG_CUSTOMER_ID, CONFIG_DEVICE_NAME)
    expected_topic_len = len(expected_topic)
    topic = msg.topic
    if topic[:expected_topic_len] != expected_topic:
        return

    api = topic[expected_topic_len:]
    print(api)

    if api == "get_status":
        topic = "server/" + topic
        payload = {}
        payload["status"] = "running"
        payload = json.dumps(payload)
        publish_mqtt_packet(topic, payload)


def publish_mqtt_packet(topic, payload):
    print("PUB: topic={} payload={}".format(topic, payload))
    if g_messaging_client:
        g_messaging_client.publish(topic, payload, qos=CONFIG_QOS)

def subscribe_mqtt_topic(topic, subscribe=True):
    print("SUB: topic={}".format(topic))
    if g_messaging_client:
        if subscribe:
            g_messaging_client.subscribe(topic, qos=CONFIG_QOS)
        else:
            g_messaging_client.unsubscribe(topic)

def on_ampq_message(ch, method, properties, body):
    print("RCV: {} {}".format(method.routing_key, body))

    expected_topic = "{}.{}.".format(CONFIG_CUSTOMER_ID, CONFIG_DEVICE_NAME)
    expected_topic_len = len(expected_topic)
    topic = method.routing_key
    if topic[:expected_topic_len] != expected_topic:
        print("exit")
        return

    api = topic[expected_topic_len:]
    print(api)

    if api == "get_status":
        topic = "server." + topic
        payload = {}
        payload["status"] = "running"
        payload = json.dumps(payload)
        publish_ampq_packet(topic, payload)

    #print("RCV: {} {}".format(method.routing_key, body))
    #g_queue_dict[method.routing_key] = body
    #print("RCV: {}".format(g_queue_dict))
    #g_messaging_client.stop_consuming()

def publish_ampq_packet(topic, payload):
    print("PUB: topic={} payload={}".format(topic, payload))
    if g_messaging_client:
        g_messaging_client.basic_publish(exchange='amq.topic', routing_key=topic, body=payload.encode("utf-8"))

def subscribe_ampq_thread(client):
    while True:
        try:
            #print("start consuming")
            client.start_consuming()
            #print("end consuming")
            break
        # Don't recover if connection was closed by broker
        except amqp.exceptions.ConnectionClosedByBroker:
            print("ConnectionClosedByBroker")
            time.sleep(1)
            continue
        # Don't recover on client errors
        except amqp.exceptions.AMQPChannelError:
            print("AMQPChannelError")
            time.sleep(1)
            continue
        # Recover on all other connection errors
        except amqp.exceptions.AMQPConnectionError:
            print("AMQPConnectionError")
            time.sleep(1)
            continue

def subscribe_ampq_topic(topic, subscribe=True):
    print("SUB: topic={}".format(topic))
    if g_messaging_client:
        if subscribe:
            if CONFIG_PREPEND_REPLY_TOPIC == '':
                index = 0
            else:
                index = len(CONFIG_PREPEND_REPLY_TOPIC)+1

            index += topic[index:].index('.')
            index2 = index + 1 + topic[index+1:].index('.')
            device_name = topic[index+1:index2]
            myqueue = 'mqtt-subscription-{}qos{}'.format(device_name, CONFIG_QOS)

            if True:
                g_messaging_client.exchange_declare(exchange='amq.topic', exchange_type='topic', durable=True)
                result = g_messaging_client.queue_declare(queue=myqueue)

            g_messaging_client.queue_bind(queue=myqueue, exchange='amq.topic', routing_key=topic)
            #print("SUB: queue={}".format(myqueue))
            #print("SUB: topic={}".format(topic))

            g_messaging_client.basic_consume(queue=myqueue, on_message_callback=on_ampq_message)
            x = threading.Thread(target=subscribe_ampq_thread, args=(g_messaging_client,))
            x.start()

def publish_messaging_packet(topic, payload):
    if CONFIG_USE_AMPQ:
       publish_ampq_packet(topic, payload)
    else:
       publish_mqtt_packet(topic, payload)

def subscribe_messaging_topic(topic, subscribe=True):
    if CONFIG_USE_AMPQ:
       subscribe_ampq_topic(topic, subscribe=subscribe)
    else:
       subscribe_mqtt_topic(topic, subscribe=subscribe)

def receive_messaging_topic(topic):
    time.sleep(1)
    i = 0
    while True:
        try:
            data = g_queue_dict[topic].decode("utf-8")
            g_queue_dict.pop(topic)
            print("API: response={}\r\n".format(data))
            return data
        except:
            #print("x")
            #time.sleep(1)
            i += 1
        if i > 5:
            break
    return None



###################################################################################
# Messaging client initialization
###################################################################################

def init_mqtt_client():
    global g_mqtt_connect

    client = mqtt.Client(client_id=CONFIG_DEVICE_NAME)
    client.on_connect = on_mqtt_connect
    client.on_message = on_mqtt_message

    # Set MQTT credentials
    client.username_pw_set(CONFIG_MQTT_USERNAME, CONFIG_MQTT_PASSWORD)

    # Set TLS certificates
    client.tls_set(ca_certs = CONFIG_MQTT_TLS_CA,
        certfile    = CONFIG_MQTT_TLS_CERT,
        keyfile     = CONFIG_MQTT_TLS_PKEY,
        cert_reqs   = ssl.CERT_REQUIRED,
        tls_version = ssl.PROTOCOL_TLSv1_2)

    # handle issue: 
    #   hostname doesn't match xxxx
    client.tls_insecure_set(True)

    # handle issues: 
    #   MQTT server is down OR 
    #   invalid MQTT crendentials OR 
    #   invalid TLS certificates
    try:
        client.connect(CONFIG_MQTT_HOST, CONFIG_MQTT_TLS_PORT)
        client.loop_start()
    except:
        client = None

    while True:
        print(g_mqtt_connect)
        if g_mqtt_connect:
            break
        time.sleep(1)

    return client

def init_ampq_client():

    use_tls = True

    # Set TLS certificates and access credentials
    credentials = amqp.PlainCredentials('guest', 'guest')
    ssl_options = None
    if use_tls:
        context = ssl._create_unverified_context()
        #context = ssl.create_default_context(cafile=CONFIG_AMPQ_TLS_CA)
        #context.load_cert_chain(CONFIG_AMPQ_TLS_CERT, CONFIG_AMPQ_TLS_PKEY)
        ssl_options = amqp.SSLOptions(context) 
        parameters = amqp.ConnectionParameters(
            CONFIG_AMPQ_HOST, 
            CONFIG_AMPQ_TLS_PORT, 
            credentials=credentials, 
            ssl_options=ssl_options)
    else:
        parameters = amqp.ConnectionParameters(
            CONFIG_AMPQ_HOST, 
            CONFIG_AMPQ_PORT, 
            credentials=credentials, 
            ssl_options=ssl_options)

    # Connect to AMPQ server
    connection = amqp.BlockingConnection(parameters)
    client = connection.channel()

    return client

def init_messaging_client():
    if CONFIG_USE_AMPQ:
       client = init_ampq_client()
       print("Using AMPQ for webserver-messagebroker communication!")
    else:
       client = init_mqtt_client()
       print("Using MQTT for webserver-messagebroker communication!")
    return client



###################################################################################
# Main entry point
###################################################################################

if __name__ == '__main__':

    # Initialize MQTT/AMPQ client
    g_messaging_client = init_messaging_client()
    if g_messaging_client is None:
        print("Error: {} server is down!!!".format("AMPQ" if CONFIG_USE_AMPQ else "MQTT"))



    time.sleep(1)
    if CONFIG_USE_AMPQ:
        subtopic = "{}.{}.#".format(CONFIG_CUSTOMER_ID, CONFIG_DEVICE_NAME)
    else:
        subtopic = "{}/{}/#".format(CONFIG_CUSTOMER_ID, CONFIG_DEVICE_NAME)
    print(subtopic)
    subscribe_messaging_topic(subtopic)

    while True:
        pass

