from fastapi import APIRouter

router = APIRouter()

@router.get("/test")
def test_reports():
    return {"status": "Reports API is successfully connected!"}
