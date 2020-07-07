FROM python:3.6.6

RUN mkdir -p /usr/src/app/email_manager
WORKDIR /usr/src/app/email_manager
COPY src/ /usr/src/app/email_manager/
WORKDIR /usr/src/app/email_manager/email_manager
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "-u", "email_manager.py", "--USE_HOST", "rabbitmq"]
