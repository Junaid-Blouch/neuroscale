from sqlalchemy import Column, Integer, String, Float, DateTime
from app.db.database import Base
import datetime

class ReportLog(Base):
    __tablename__ = "report_logs"

    id = Column(Integer, primary_key=True, index=True)
    report_title = Column(String, index=True)
    start_date = Column(String)
    end_date = Column(String)
    total_cost_saved = Column(Float)
    drift_status = Column(String)
    generated_at = Column(DateTime, default=datetime.datetime.utcnow)
    file_path = Column(String) # Word/PDF file kahan save hui hai
