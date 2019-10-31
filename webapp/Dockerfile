FROM node:10.6-alpine

RUN npm install -g ionic gulp && mkdir -p /usr/src/app/ionicapp
WORKDIR /usr/src/app/ionicapp
COPY src/ionicapp/ /usr/src/app/ionicapp/

# change default URL 192.168.99.100 to the environment variable $config_use_apiurl
ARG config_use_apiurl
RUN chmod 777 /usr/src/app/ionicapp/www/js/env.js
RUN cat /usr/src/app/ionicapp/www/js/env.js | sed -e 's/'192.168.99.100'/'$config_use_apiurl'/' > /usr/src/app/ionicapp/www/js/env.js

RUN npm install -D -E @ionic/v1-toolkit && npm rebuild node-sass
CMD ["ionic", "serve", "--address=0.0.0.0", "--port=8100", "--no-open", "--no-livereload"]

EXPOSE 8100
