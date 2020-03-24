FROM python:3.6.6

RUN mkdir -p /usr/src/app/registration_manager
WORKDIR /usr/src/app/registration_manager
COPY src/ /usr/src/app/registration_manager/
WORKDIR /usr/src/app/scan_manager/registration_manager
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "-u", "registration_manager.py", "--USE_HOST", "rabbitmq"]
