FROM python:3.6.6

RUN mkdir -p /usr/src/app/notification_manager
WORKDIR /usr/src/app/notification_manager
COPY libpyiotcloud/ /usr/src/app/notification_manager/
WORKDIR /usr/src/app/notification_manager/notification_manager
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "-u", "notification_manager.py", "--USE_HOST", "172.18.0.2"]
