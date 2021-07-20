FROM python:3.8-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY ./reader/metrics_reader.py metrics_reader.py

ENTRYPOINT [ "python3", "metrics_reader.py" ]