from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import get_db, Base, engine
from models import CutURL
from schemas import CutRequest, DeleteRequest
from utils import base62_encode, get_client_ip
import os
import time
import pytz
import socket
from datetime import datetime

# 테이블 자동 생성
Base.metadata.create_all(bind=engine)

app = FastAPI()

# 정적 파일 등록
app.mount("/static", StaticFiles(directory="static"), name="static")

# 템플릿 폴더 설정
templates = Jinja2Templates(directory="templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# 서버 시간대 (예: 'Asia/Seoul'로 설정)
local_tz = pytz.timezone("Asia/Seoul")

OWNER_DOMAIN = os.environ.get(OWNER_DOMAIN)
if "://" in OWNER_DOMAIN:
    OWNER_DOMAIN = OWNER_DOMAIN.split("://", 1)[1].split("/", 1)[0]

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    # 1. IP 조회
    owner_ip = socket.gethostbyname(OWNER_DOMAIN)
    # 2. 접속자 IP 추출
    client_ip = get_client_ip(request)

    # 3. 소유자 판별
    is_owner = (client_ip == owner_ip)

    # 4. URL 조
    recent_urls = db.query(CutURL).order_by(CutURL.created_at.desc()).limit(50).all()
    for url in recent_urls:
        url.is_owner = is_owner or (url.ip == client_ip)
        print(url.ip + " ::::: " + client_ip)

    ts = int(datetime.utcnow().timestamp())
    return templates.TemplateResponse("index.html", {
        "request": request,
        "ts": ts,
        "recent_urls": recent_urls
    })

@app.get("/privacy", response_class=HTMLResponse, include_in_schema=False)
async def privacy_policy(request: Request):
    return templates.TemplateResponse("privacy.html", {"request": request})

@app.post("/cut")
async def cut_url(payload: CutRequest, request: Request, db: Session = Depends(get_db)):
    # 전체 개수가 1000개 이상이면 가장 오래된 거 하나 삭제
    total_count = db.query(CutURL).count()
    if total_count >= 1000:
        oldest = db.query(CutURL).order_by(CutURL.created_at.asc()).first()
        if oldest:
            db.delete(oldest)
            db.commit()

    timestamp = int(time.time())
    count = db.query(CutURL).filter(CutURL.timestamp_sec == timestamp).count()
    order = count + 1
    key_num = int(f"{timestamp}{order:04d}")
    url_key = base62_encode(key_num)
    client_ip = get_client_ip(request)
    record = CutURL(
        original_url=payload.url,
        timestamp_sec=timestamp,
        timestamp_order=order,
        url_key=url_key,
        ip=client_ip
    )
    db.add(record)
    db.commit()
    return JSONResponse(content={"detail": "Cut", "value": url_key}, status_code=201)

@app.delete("/delete")
async def delete_url(payload: DeleteRequest, request: Request, db: Session = Depends(get_db)):
    # 1.IP 조회
    owner_ip = socket.gethostbyname(OWNER_DOMAIN)
    # 2. 접속자 IP 추출
    client_ip = get_client_ip(request)

    # 3. 소유자 판별
    is_owner = (client_ip == owner_ip)

    record = db.query(CutURL).filter_by(uid=payload.uid).first()
    if not record:
        return JSONResponse(content={"detail": "Not found"}, status_code=404)

    # 4. 삭제 권한 체크
    if not is_owner and record.ip != client_ip:
        return JSONResponse(content={"detail": "삭제 권한이 없습니다."}, status_code=403)

    db.delete(record)
    db.commit()
    return JSONResponse(content={"detail": "Deleted"}, status_code=200)


@app.get("/{url_key}")
async def redirect_to_url(url_key: str, db: Session = Depends(get_db)):
    record = db.query(CutURL).filter_by(url_key=url_key).first()
    if not record:
        return HTMLResponse("Not found", status_code=404)
    return RedirectResponse(record.original_url)

