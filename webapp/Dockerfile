FROM node:10.6-alpine

RUN npm install -g ionic gulp
RUN node -v
RUN npm -v
RUN ionic -v
RUN npm install --save @ionic/v1-toolkit --no-confirm

RUN mkdir -p /usr/src/app/ionicapp
WORKDIR /usr/src/app/ionicapp
COPY src/ionicapp/ /usr/src/app/ionicapp/
RUN npm rebuild node-sass

CMD ["ionic", "serve", "--address=172.18.0.5", "--port=8100", "--no-open", "--no-livereload", "--consolelogs", "--no-proxy"]

EXPOSE 8100
