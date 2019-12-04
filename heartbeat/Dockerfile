FROM python:3.6.6

RUN mkdir -p /usr/src/app/heartbeat_manager
WORKDIR /usr/src/app/heartbeat_manager
COPY src/ /usr/src/app/heartbeat_manager/
WORKDIR /usr/src/app/heartbeat_manager/heartbeat_manager
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "-u", "heartbeat_manager.py", "--USE_HOST", "rabbitmq"]
