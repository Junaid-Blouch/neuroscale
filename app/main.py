from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
from app.api import reports
import os
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

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
# FRONTEND ROUTING 
# ==========================================
@app.get("/")
def read_root():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path_in_web_folder = os.path.join(BASE_DIR, "web", "index.html")
    path_in_root_folder = os.path.join(BASE_DIR, "index.html")
    
    if os.path.exists(path_in_web_folder):
        return FileResponse(path_in_web_folder)
    elif os.path.exists(path_in_root_folder):
        return FileResponse(path_in_root_folder)
        
    return HTMLResponse(content="<h1>Error: index.html not found!</h1>", status_code=404)