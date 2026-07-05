"""
Document APIs (Section 4.15.2):
    POST   /upload             Upload new document
    GET    /documents          Display uploaded documents
    DELETE /documents/{id}     Delete selected document
"""
import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from database.models import get_db, Document, User, SystemLog
from models.schemas import DocumentResponse
from api.deps import get_current_admin
from services.document_service import process_document, get_file_type
from services.search_service import add_document_chunks, delete_document_chunks
from config import settings

router = APIRouter(tags=["Documents"])

ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}
MAX_FILE_SIZE_MB = 20


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    try:
        file_type = get_file_type(file.filename)
    except ValueError:
        raise HTTPException(status_code=400, detail="Only PDF, DOCX, and TXT files are supported.")

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    destination = os.path.join(settings.UPLOAD_DIR, file.filename)

    with open(destination, "wb") as out_file:
        shutil.copyfileobj(file.file, out_file)

    size_mb = os.path.getsize(destination) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        os.remove(destination)
        raise HTTPException(status_code=400, detail=f"File exceeds the {MAX_FILE_SIZE_MB} MB limit.")

    document = Document(
        user_id=current_admin.user_id,
        file_name=file.filename,
        file_type=file_type,
        status="processing",
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    try:
        chunks = process_document(destination, file_type)
        stored = add_document_chunks(document.document_id, file.filename, chunks)
        document.chunk_count = stored
        document.status = "processed"
    except Exception as exc:  # noqa: BLE001
        document.status = "failed"
        db.add(SystemLog(event=f"Document processing failed for '{file.filename}': {exc}"))
    finally:
        db.commit()
        db.refresh(document)

    db.add(SystemLog(event=f"Document '{file.filename}' uploaded by '{current_admin.username}'."))
    db.commit()

    return document


@router.get("/documents", response_model=list[DocumentResponse])
def list_documents(current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    return db.query(Document).order_by(Document.upload_date.desc()).all()


@router.delete("/documents/{document_id}")
def delete_document(
    document_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    document = db.query(Document).filter(Document.document_id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found.")

    delete_document_chunks(document_id)

    file_path = os.path.join(settings.UPLOAD_DIR, document.file_name)
    if os.path.exists(file_path):
        os.remove(file_path)

    db.delete(document)
    db.add(SystemLog(event=f"Document '{document.file_name}' deleted by '{current_admin.username}'."))
    db.commit()

    return {"status": "success", "message": "Document deleted successfully."}
