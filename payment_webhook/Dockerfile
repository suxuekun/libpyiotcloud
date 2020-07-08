FROM python:3.6.6

RUN mkdir -p /usr/src/app/payment_webhook
WORKDIR /usr/src/app/payment_webhook
COPY src/ /usr/src/app/payment_webhook/
RUN pip install --no-cache-dir -r requirements.txt

CMD ["gunicorn", "--workers=5", "--threads=2", "--timeout=120", "--bind=0.0.0.0:8003", "--forwarded-allow-ips='*'", "wsgi:app"]

EXPOSE 8003

