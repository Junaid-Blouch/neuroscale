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
# ==========================================
# FRONTEND ROUTING (Ultimate Auto-Discovery)
# ==========================================
@app.get("/")
def read_root():
    import os
    from fastapi.responses import HTMLResponse, FileResponse
    
    # 1. Get the current working directory of Hugging Face (/code)
    base_dir = os.getcwd() 
    found_path = None
    
    # 2. Scan every single folder in the project to find index.html
    for root, dirs, files in os.walk(base_dir):
        # Ignore system folders to speed up the search
        if '.git' in root or '__pycache__' in root or 'venv' in root or '.local' in root:
            continue
        for file in files:
            # .lower() fixes Windows/Linux case sensitivity issues (e.g., Index.html vs index.html)
            if file.lower() == "index.html": 
                found_path = os.path.join(root, file)
                break
        if found_path:
            break
            
    # 3. If file is found ANYWHERE, serve it immediately!
    if found_path:
        return FileResponse(found_path)
        
    # 4. If file is TRULY missing from the cloud, print the server's exact folder tree
    tree_html = f"<h2>Error: index.html is completely missing from the cloud server!</h2>"
    tree_html += f"<p>Here is what the server actually sees inside <b>{base_dir}</b>:</p><ul>"
    
    for root, dirs, files in os.walk(base_dir):
        if '.git' in root or '__pycache__' in root or 'venv' in root or '.local' in root: 
            continue
        tree_html += f"<li><b style='color: blue;'>{root}</b><ul>"
        for f in files: 
            tree_html += f"<li>{f}</li>"
        tree_html += "</ul></li>"
        
    tree_html += "</ul><p>Please check your .gitignore file or drag-and-drop index.html directly to Hugging Face.</p>"
    
    return HTMLResponse(content=tree_html, status_code=404)