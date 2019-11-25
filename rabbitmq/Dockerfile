FROM rabbitmq:3.7

RUN rabbitmq-plugins enable --offline rabbitmq_management && rabbitmq-plugins enable --offline rabbitmq_mqtt
COPY src/ /etc/rabbitmq/

ADD init.sh /init.sh
EXPOSE 15672
CMD ["/init.sh"]

EXPOSE 5671
EXPOSE 8883
