FROM node:10.6-alpine

RUN npm install -g ionic gulp && mkdir -p /usr/src/app/ionicapp
WORKDIR /usr/src/app/ionicapp

COPY src/ionicapp/ /usr/src/app/ionicapp/
ARG config_use_apiurl
RUN cat /usr/src/app/ionicapp/www/js/env.js | sed -i 's/localhost/'$config_use_apiurl'/' /usr/src/app/ionicapp/www/js/env.js

ARG config_use_jwtkey
RUN cat /usr/src/app/ionicapp/www/js/env.js | sed -i 's/secretkey/'$config_use_jwtkey'/' /usr/src/app/ionicapp/www/js/env.js

ARG config_use_googleapikey
RUN cat /usr/src/app/ionicapp/www/js/env.js | sed -i 's/googleapikey/'$config_use_googleapikey'/' /usr/src/app/ionicapp/www/js/env.js

ARG config_use_awsoauthdomain
RUN cat /usr/src/app/ionicapp/www/js/env.js | sed -i 's/awsoauthdomain/'$config_use_awsoauthdomain'/' /usr/src/app/ionicapp/www/js/env.js

ARG config_use_awsclientid
RUN cat /usr/src/app/ionicapp/www/js/env.js | sed -i 's/awsclientid/'$config_use_awsclientid'/' /usr/src/app/ionicapp/www/js/env.js

RUN npm install -D -E @ionic/v1-toolkit && npm rebuild node-sass
RUN cat /usr/src/app/ionicapp/www/js/env.js
CMD ["ionic", "serve", "--address=0.0.0.0", "--port=8100", "--no-open", "--no-livereload"]

EXPOSE 8100
