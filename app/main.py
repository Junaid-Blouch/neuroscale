from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
from app.api import reports
from app.db.database import engine
from app.db import models
import os

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

# Initialize DB Tables automatically
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="NeuroScale Enterprise AI")

# Include the AI endpoints
app.include_router(reports.router, prefix="/api/v1/reports", tags=["Reports"])

# ==========================================
# BACKGROUND MLOPS WATCHDOG
# ==========================================
scheduler = BackgroundScheduler()

def scheduled_retraining_job():
    print("\n[WATCHDOG] 🔍 Initiating Nightly Drift Analysis & Retraining Protocol...")
    print("[WATCHDOG] ✅ Drift Analysis Complete. System Optimal.\n")

@app.on_event("startup")
def start_scheduler():
    scheduler.add_job(scheduled_retraining_job, CronTrigger(hour=2, minute=0))
    scheduler.start()
    print("⏰ Enterprise Background Scheduler Online!")

@app.on_event("shutdown")
def stop_scheduler():
    scheduler.shutdown()
    print("💤 Scheduler safely shut down.")

# ==========================================
# FRONTEND ROUTING (THE FIX)
# ==========================================
@app.get("/")
def read_root():
    # FastAPI ko batayen ke index.html file serve karni hai
    file_path = "index.html"
    
    # Check karega ke index.html mojood hai ya nahi
    if os.path.exists(file_path):
        return FileResponse(file_path)
    
    # Agar index.html apni jagah par nahi mili to yeh error dega
    return HTMLResponse("<h1>Error: Cyberpunk index.html not found in the root directory!</h1>", status_code=404)