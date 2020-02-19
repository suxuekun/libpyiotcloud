FROM rabbitmq:3.7

RUN rabbitmq-plugins enable --offline rabbitmq_management && rabbitmq-plugins enable --offline rabbitmq_mqtt

ARG config_use_defaultuser
ARG config_use_defaultpass
RUN rabbitmqctl add_user '$config_use_defaultuser' '$config_use_defaultpass' 
RUN rabbitmqctl set_permissions -p / '$config_use_defaultuser' ".*" ".*" ".*" 
RUN rabbitmqctl set_user_tags '$config_use_defaultuser' administrator 
RUN rabbitmqctl set_topic_permissions -p / '$config_use_defaultuser' amq.topic ".*" ".*"

COPY src/ /etc/rabbitmq/

EXPOSE 15672
EXPOSE 8883
