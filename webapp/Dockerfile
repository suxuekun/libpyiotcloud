FROM python:3.6.6

RUN mkdir -p /usr/src/app/libpyiotcloud
WORKDIR /usr/src/app/libpyiotcloud
COPY src/ /usr/src/app/libpyiotcloud/
RUN pip install --no-cache-dir -r requirements.txt

CMD ["gunicorn", "--workers=1", "--bind=0.0.0.0:8000", "--forwarded-allow-ips='*'", "wsgi:app"]

EXPOSE 8000

