FROM python:3.10-slim

WORKDIR /code

ENV PYTHONDONTWRITEBYTECODE 1 \
    PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y ffmpeg libavcodec-extra

COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r /code/requirements.txt

COPY . .

RUN chmod a+x docker/app.sh