FROM python:3.12

RUN apt-get update && apt-get install -y vim curl

WORKDIR /app

# Create proper directory structure
RUN mkdir -p /app/backend/common
RUN mkdir -p /app/backend/data_source
RUN mkdir -p /app/backend/data_sink
RUN mkdir -p /app/backend/logs
RUN mkdir -p /app/data/My\ Files
RUN mkdir -p /app/data/Received\ Files

# Copy application files
COPY ./common/* /app/backend/common/
COPY ./data_source/* /app/backend/data_source/
COPY ./data_sink/* /app/backend/data_sink/
COPY ./requirements.txt /app/requirements.txt
COPY ./run_backend.py /app/backend/run_backend.py

# Ensure logs directory and files exist
RUN touch /app/backend/logs/data_sink.log
RUN touch /app/backend/logs/data_source.log

# Install dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Set environment variables
ENV PYTHONPATH=/app

EXPOSE 8002
EXPOSE 8003

# Run both services
CMD ["python", "backend/run_backend.py", "--service", "all", "--log-level", "debug", "--detailed-logs"]