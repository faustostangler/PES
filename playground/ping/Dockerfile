FROM python:3.11-alpine

WORKDIR /app

RUN pip install --no-cache-dir icmplib speedtest-cli

COPY monitor.py .

VOLUME ["/data"]

ENV TARGET_IP=1.1.1.1
ENV INTERVAL=30
ENV DB_PATH=/data/ping_log.db
ENV CSV_PATH=/data/ping_history.csv

CMD ["python", "-u", "monitor.py"]
