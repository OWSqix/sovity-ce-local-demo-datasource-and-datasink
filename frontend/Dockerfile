FROM node:18.19.1

RUN apt-get update && apt-get install -y vim curl

WORKDIR /app

ARG DATA_SOURCE_API_URL
ARG DATA_SINK_API_URL
ENV DATA_SOURCE_API_URL=$DATA_SOURCE_API_URL
ENV DATA_SINK_API_URL=$DATA_SINK_API_URL

RUN npm install -g @angular/cli@19.2.4

COPY package*.json ./
RUN npm install

COPY . .

RUN node set-env.js

EXPOSE 4200

CMD ["ng", "serve", "--host", "0.0.0.0", "--disable-host-check"]
