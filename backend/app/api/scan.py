from fastapi import APIRouter

router = APIRouter()

@router.post("/")
def scan(path: str):
    return {"message": f"Scanning started for {path}"}
