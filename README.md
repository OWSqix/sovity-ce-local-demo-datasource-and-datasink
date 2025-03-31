# Sample data source and data sink for Sovity EDC CE

This repository provides you a sample data sink and data source for Sovity CE local deployment.

## Getting started

First, you need to clone and set up with [Sovity CE guide](https://github.com/sovity/edc-ce).

After you finish it, then clone this repository
```angular2html
git clone https://github.com/OWSqix/sovity-ce-local-demo-datasource-and-datasink.git
```

Copy backend and frontend to sovity-edc-ce/docs/deployment-guide/goals/local-demo-ce/
```angular2html
cp ./frontend {path_to_sovity-edc-ce}/docs/deployment-guide/goals/local-demo-ce/
cp ./backend {path_to_sovity-edc-ce}/docs/deployment-guide/goals/local-demo-ce/
```
Fix docker-compose.yaml
```angular2html
in "provider-connector"
-> change: sovity.edc.fqdn.internal from 'localhost' to 'provider-connector'
-> add environment: edc.control.endpoint: 'http://provider-connector:11004/api/control'

in "consumer-connector"
-> change: sovity.edc.fqdn.internal from 'localhost' to 'consumer-connector'
-> add environment: edc.control.endpoint: 'http://consumer-connector:11004/api/control'
```
Add those lines after services in docker-compose.yaml
```angular2html
  provider-backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    image: 'sovity-ce-local-demo-datasource-and-datasink-backend:latest'
    restart: always
    ports:
      - "8000:8002"  # Data Sink API
      - "8001:8003"  # Data Source API
    volumes:
      - ./provider/data:/app/data
      - ./provider/backend/logs:/app/backend/logs
    environment:
      - LOG_LEVEL=debug
      - HOST=0.0.0.0

  provider-frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      args:
        - DATA_SINK_API_URL=http://localhost:8000
        - DATA_SOURCE_API_URL=http://localhost:8001
    image: 'sovity-ce-local-demo-datasource-and-datasink-provider-frontend:latest'
    ports:
      - "4200:4200"
    environment:
      - DATA_SINK_API_URL=http://localhost:8000
      - DATA_SOURCE_API_URL=http://localhost:8001
    depends_on:
      - provider-backend

  consumer-backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    image: 'sovity-ce-local-demo-datasource-and-datasink-backend:latest'
    restart: always
    ports:
      - "8002:8002"  # Data Sink API
      - "8003:8003"  # Data Source API
    volumes:
      - ./consumer/data:/app/data
      - ./consumer/backend/logs:/app/backend/logs
    environment:
      - LOG_LEVEL=debug
      - HOST=0.0.0.0

  consumer-frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      args:
        - DATA_SINK_API_URL=http://localhost:8002
        - DATA_SOURCE_API_URL=http://localhost:8003
    image: 'sovity-ce-local-demo-datasource-and-datasink-consumer-frontend:latest'
    ports:
      - "4201:4200"
    environment:
      - DATA_SINK_API_URL=http://localhost:8002
      - DATA_SOURCE_API_URL=http://localhost:8003
    depends_on:
      - consumer-backend
```

Build docker compose and enjoy sharing
```
docker compose up -d --build
```