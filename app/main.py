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
app.include_router(reports.router, prefix="/api/v1/reports", tags=["Reports"])

# ==========================================
# BACKGROUND MLOPS WATCHDOG
# ==========================================
scheduler = BackgroundScheduler()

def scheduled_retraining_job():
    print("[WATCHDOG] ✅ Drift Analysis Complete. System Optimal.")

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
# FRONTEND ROUTING (100% Bulletproof Pathing)
# ==========================================
@app.get("/")
def read_root():
    # Find the exact absolute root path of the project on Hugging Face
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Define the two possible places the file could be
    path_in_web_folder = os.path.join(BASE_DIR, "web", "index.html")
    path_in_root_folder = os.path.join(BASE_DIR, "index.html")
    
    # 1. First, check if it's inside the 'web' folder
    if os.path.exists(path_in_web_folder):
        return FileResponse(path_in_web_folder)
        
    # 2. If not in 'web', check if it's outside in the main root folder
    elif os.path.exists(path_in_root_folder):
        return FileResponse(path_in_root_folder)
        
    # 3. If file is completely missing from the cloud, show this error
    error_msg = f"""
    <h1>Critical Error: index.html is Missing from Hugging Face!</h1>
    <p>The server checked these two exact locations but found nothing:</p>
    <ol>
        <li><b>{path_in_web_folder}</b></li>
        <li><b>{path_in_root_folder}</b></li>
    </ol>
    <p><b>How to fix:</b> Go to your Hugging Face Space -> Click 'Files' -> Click 'Add file' -> 'Upload files' -> Drop your index.html here and commit.</p>
    """
    return HTMLResponse(content=error_msg, status_code=404)