#!/bin/sh

( sleep 5 && \
rabbitmq-server start && \
rabbitmqctl add_user admin admin && \
rabbitmqctl set_user_tags admin administrator  && \
rabbitmqctl set_permissions -p / admin ".*" ".*" ".*"  && \
rabbitmqctl set_topic_permissions -p / admin amq.topic "^$" "^$" )

