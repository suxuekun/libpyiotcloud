FROM rabbitmq:3.7

RUN rabbitmq-plugins enable --offline rabbitmq_management && rabbitmq-plugins enable --offline rabbitmq_mqtt

COPY src/ /etc/rabbitmq/

EXPOSE 15672
EXPOSE 8883
