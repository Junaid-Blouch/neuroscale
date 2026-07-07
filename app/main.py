from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from app.api import reports
from app.db.database import engine
from app.db import models

# 🚀 Initialize Database Tables automatically on startup
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="NeuroScale Enterprise AI")

app.include_router(reports.router, prefix="/api/v1/reports", tags=["Reports"])

@app.get("/", response_class=HTMLResponse)
def read_root():
    # Temporary placeholder UI (We will upgrade this to Cyberpunk Dashboard soon)
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>NeuroScale | AI Engine</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0d1117; color: #c9d1d9; text-align: center; padding-top: 100px; }
            h1 { color: #58a6ff; font-weight: 300; letter-spacing: 2px;}
            p { color: #8b949e; margin-bottom: 40px; }
            .status { display: inline-block; padding: 10px 20px; background-color: #238636; color: white; border-radius: 20px; font-weight: bold; }
        </style>
    </head>
    <body>
        <h1>NeuroScale API (System Online)</h1>
        <p>Adaptive Cloud Resource Optimization Backend</p>
        <div class="status">✅ SQLite Database Connected</div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)
