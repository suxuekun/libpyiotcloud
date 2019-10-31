FROM nginx:latest

RUN rm /etc/nginx/conf.d/default.conf

ARG config_use_certs
COPY $config_use_certs /etc/nginx/conf.d/

EXPOSE 443

