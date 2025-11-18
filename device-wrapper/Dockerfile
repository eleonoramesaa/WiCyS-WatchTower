# device-wrapper/Dockerfile

FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir paho-mqtt

# We’ll use the built-in http.server, so no extra web frameworks are needed

# Copy the wrapper script
COPY server.py .

CMD ["python", "server.py"]
