FROM tomerlevi/streamlit-docker

EXPOSE 8501

WORKDIR /app

COPY requirements.txt ./
RUN pip install -U pip
RUN pip install --no-cache-dir -r requirements.txt

