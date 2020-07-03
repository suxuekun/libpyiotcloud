FROM python:3.6.6

RUN mkdir -p /usr/src/app/download_manager
WORKDIR /usr/src/app/download_manager
COPY src/ /usr/src/app/download_manager/
WORKDIR /usr/src/app/download_manager/download_manager
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "-u", "download_manager.py", "--USE_HOST", "rabbitmq"]
