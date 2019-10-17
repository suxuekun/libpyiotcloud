FROM python:3.6.6

RUN mkdir -p /usr/src/app/notification_manager
WORKDIR /usr/src/app/notification_manager
COPY src/ /usr/src/app/notification_manager/
WORKDIR /usr/src/app/notification_manager/notification_manager
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "-u", "notification_manager.py", "--USE_HOST", "rabbitmq"]
