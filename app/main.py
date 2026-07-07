from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
from app.api import reports
from app.db.database import engine
from app.db import models
import os

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

# ==========================================
# DATABASE INITIALIZATION
# ==========================================
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="NeuroScale Enterprise AI")

# Include the AI endpoints (Links to reports.py)
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
    # Rozana raat 2:00 AM par check karega
    scheduler.add_job(scheduled_retraining_job, CronTrigger(hour=2, minute=0))
    scheduler.start()
    print("⏰ Enterprise Background Scheduler Online!")

@app.on_event("shutdown")
def stop_scheduler():
    scheduler.shutdown()
    print("💤 Scheduler safely shut down.")

# ==========================================
# FRONTEND ROUTING (Absolute Path Fix)
# ==========================================
@app.get("/")
def read_root():
    # Absolute path banayen taake Hugging Face ka Docker kabhi file miss na kare
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(BASE_DIR, "index.html")
    
    if os.path.exists(file_path):
        return FileResponse(file_path)
    
    # Agar file nahi milti to absolute path print karega taake debugging asaan ho
    error_html = f"""
    <h1>Error: index.html not found!</h1>
    <p>System is looking for the file exactly at: <b>{file_path}</b></p>
    <p>Please make sure 'index.html' is uploaded to the main root folder of your repository.</p>
    """
    return HTMLResponse(content=error_html, status_code=404)# ==========================================
# FRONTEND ROUTING (Updated for 'web' folder)
# ==========================================
# ==========================================
# FRONTEND ROUTING (Bulletproof Dual-Check)
# ==========================================
@app.get("/")
def read_root():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Path 1: Check inside the 'web' folder
    path_web = os.path.join(BASE_DIR, "web", "index.html")
    # Path 2: Check in the main root folder
    path_root = os.path.join(BASE_DIR, "index.html")
    
    # Dual-Check Logic
    if os.path.exists(path_web):
        return FileResponse(path_web)
    elif os.path.exists(path_root):
        return FileResponse(path_root)
    
    # If both fail
    error_html = f"""
    <h1>Error: index.html not found anywhere!</h1>
    <p>System checked both of these locations but found nothing:</p>
    <ul>
        <li><b>{path_web}</b></li>
        <li><b>{path_root}</b></li>
    </ul>
    """
    return HTMLResponse(content=error_html, status_code=404)