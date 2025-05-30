from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime
import pytz

# Base 클래스 정의 (필수)
Base = declarative_base()

# Asia/Seoul 타임존 설정
seoul_tz = pytz.timezone("Asia/Seoul")

class CutURL(Base):
    __tablename__ = 'cut_urls'

    uid = Column(Integer, primary_key=True, index=True)
    original_url = Column(String, index=True)
    timestamp_sec = Column(Integer)
    timestamp_order = Column(Integer)
    ip = Column(String)
    url_key = Column(String, unique=True, index=True)

    # 명확히 타임존 포함해서 현재시간 저장
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(seoul_tz))

