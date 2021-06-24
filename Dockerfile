FROM python:3.9.5-slim-buster

EXPOSE 8501

WORKDIR /app

COPY requirements.txt .
RUN pip install -U pip
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install nano

COPY ./src /examples

CMD streamlit run /examples/app.py -- "bolt://3.231.58.8:7687" "neo4j" "band-thermometer-sash"