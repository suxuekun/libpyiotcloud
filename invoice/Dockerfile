FROM python:3.6.6

RUN mkdir -p /usr/src/app/invoice_manager
WORKDIR /usr/src/app/invoice_manager
COPY src/ /usr/src/app/invoice_manager/
WORKDIR /usr/src/app/invoice_manager/invoice_manager
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "-u", "invoice_manager.py", "--USE_HOST", "rabbitmq"]
