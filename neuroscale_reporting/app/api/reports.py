from fastapi import APIRouter
from app.schemas.report_schema import NeuroScaleReportData
from app.services.generator import generate_word_report
from fastapi.responses import FileResponse
import os

router = APIRouter()

@router.post("/generate/{format}")
async def generate_report(format: str, data: NeuroScaleReportData):
    if format.lower() == "word":
        file_path = generate_word_report(data)
        
        # File directly user ko download karwa dega
        return FileResponse(
            path=file_path, 
            filename="NeuroScale_Report.docx", 
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        
    return {"error": "Format currently unsupported. Use 'word'."}
