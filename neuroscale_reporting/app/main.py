from fastapi import FastAPI
from app.api import reports

app = FastAPI(title="NeuroScale Enterprise Reporting API")

app.include_router(reports.router, prefix="/api/v1/reports", tags=["Reports"])

@app.get("/")
def read_root():
    return {"status": "NeuroScale Reporting Backend is Live"}
