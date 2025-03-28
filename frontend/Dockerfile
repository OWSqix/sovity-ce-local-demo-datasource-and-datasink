FROM node:18.19.1

RUN apt-get update && apt-get install -y vim curl

WORKDIR /app

RUN npm install -g @angular/cli@19.2.4

COPY package*.json ./
RUN npm install
COPY . .

EXPOSE 4200

CMD ["ng", "serve", "--host", "0.0.0.0", "--disable-host-check"]
