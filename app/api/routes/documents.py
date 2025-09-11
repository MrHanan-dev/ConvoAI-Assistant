"""
Document API routes
"""

from fastapi import APIRouter, UploadFile, File

router = APIRouter()


@router.post("/")
async def upload_document(file: UploadFile = File(...)):
    """Upload document for processing"""
    return {
        "id": "doc_123",
        "filename": file.filename,
        "status": "uploaded"
    }


@router.get("/")
async def list_documents():
    """List documents"""
    return {
        "documents": [
            {"id": "doc_1", "name": "Sales Playbook", "type": "pdf"},
            {"id": "doc_2", "name": "Product Features", "type": "docx"}
        ]
    }
