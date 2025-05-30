#!/bin/bash

# 1. cron 데몬 시작 (백그라운드)
/usr/sbin/cron

# 2. FastAPI(Uvicorn) 서버 실행 (포그라운드)
uvicorn main:app --host 0.0.0.0 --port 80

