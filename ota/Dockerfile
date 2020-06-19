FROM python:3.6.6

RUN mkdir -p /usr/src/app/ota_manager
WORKDIR /usr/src/app/ota_manager
COPY src/ /usr/src/app/ota_manager/
WORKDIR /usr/src/app/ota_manager/ota_manager
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "-u", "ota_manager.py", "--USE_HOST", "rabbitmq"]
