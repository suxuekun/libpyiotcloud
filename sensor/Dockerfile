FROM python:3.6.6

RUN mkdir -p /usr/src/app/sensor_manager
WORKDIR /usr/src/app/sensor_manager
COPY src/ /usr/src/app/sensor_manager/
WORKDIR /usr/src/app/sensor_manager/sensor_manager
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "-u", "sensor_manager.py", "--USE_HOST", "rabbitmq"]
