FROM python:3.11-slim

# 타임존 설정 추가
RUN apt-get update \
    && apt-get install -y tzdata cron curl \
    && ln -snf /usr/share/zoneinfo/Asia/Seoul /etc/localtime \
    && echo "Asia/Seoul" > /etc/timezone


WORKDIR /app

COPY . /app


# CRON 복사
COPY cron /etc/cron.d/cron
RUN chmod 0644 /etc/cron.d/cron && crontab /etc/cron.d/cron

COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install -r requirements.txt

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

#CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]


