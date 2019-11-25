FROM rabbitmq:3.7

RUN rabbitmq-plugins enable --offline rabbitmq_management && rabbitmq-plugins enable --offline rabbitmq_mqtt

COPY src/ /etc/rabbitmq/

EXPOSE 15672
EXPOSE 5671
EXPOSE 8883

RUN rabbitmq-server start
RUN rabbitmqctl add_user admin admin 
RUN rabbitmqctl set_user_tags admin administrator 
RUN rabbitmqctl set_permissions -p / admin ".*" ".*" ".*" 
RUN rabbitmqctl set_topic_permissions -p / admin amq.topic "^$" "^$"
