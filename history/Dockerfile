FROM python:3.6.6

RUN mkdir -p /usr/src/app/history_manager
WORKDIR /usr/src/app/history_manager
COPY src/ /usr/src/app/history_manager/
WORKDIR /usr/src/app/history_manager/history_manager
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "-u", "history_manager.py", "--USE_HOST", "172.18.0.2"]
