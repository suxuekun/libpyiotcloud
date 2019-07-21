FROM rabbitmq:3.7

RUN rabbitmq-plugins enable --offline rabbitmq_management
RUN rabbitmq-plugins enable --offline rabbitmq_mqtt

COPY src/ /etc/rabbitmq/

EXPOSE 15672
EXPOSE 5671
EXPOSE 8883
