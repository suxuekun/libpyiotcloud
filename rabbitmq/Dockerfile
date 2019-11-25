FROM rabbitmq:3.7

RUN rabbitmq-plugins enable --offline rabbitmq_management && rabbitmq-plugins enable --offline rabbitmq_mqtt

RUN rabbitmqctl add_user admin admin && rabbitmqctl set_user_tags admin administrator && rabbitmqctl set_permissions -p / admin ".*" ".*" ".*" && rabbitmqctl set_topic_permissions -p / admin amq.topic "^$" "^$"

COPY src/ /etc/rabbitmq/

EXPOSE 15672
EXPOSE 5671
EXPOSE 8883
