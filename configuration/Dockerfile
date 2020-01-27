FROM python:3.6.6

RUN mkdir -p /usr/src/app/configuration_manager
WORKDIR /usr/src/app/configuration_manager
COPY src/ /usr/src/app/configuration_manager/
WORKDIR /usr/src/app/configuration_manager/configuration_manager
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "-u", "configuration_manager.py", "--USE_HOST", "rabbitmq"]
