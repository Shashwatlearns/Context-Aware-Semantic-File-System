from fastapi import FastAPI
from api import scan, search, file, context

app = FastAPI(title="Context-Aware Semantic File System")

# Register all API routes
app.include_router(scan.router, prefix="/scan", tags=["Scan"])
app.include_router(search.router, prefix="/search", tags=["Search"])
app.include_router(file.router, prefix="/get_file", tags=["File"])
app.include_router(context.router, prefix="/get_context", tags=["Context"])

@app.get("/")
def root():
    return {"message": "Backend running"}
