FROM python:3.9.5-slim-buster

EXPOSE 8501

WORKDIR /app

COPY requirements.txt .
RUN pip install -U pip
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src /examples
ENTRYPOINT ["streamlit", "run"]
CMD ["/examples/intro.py"]