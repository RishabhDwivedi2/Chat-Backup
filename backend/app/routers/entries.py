from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.app.schemas import entry as schemas
from backend.app.database import get_db
from backend.app.services import entry_service

router = APIRouter()

@router.post("/", response_model=schemas.Entry, operation_id="create_entry")
def create_entry(entry: schemas.EntryCreate, db: Session = Depends(get_db)):
    return entry_service.create_entry(db, entry)

@router.get("/", response_model=List[schemas.Entry], operation_id="read_entries")
def read_entries(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return entry_service.get_entries(db, skip=skip, limit=limit)

@router.get("/{entry_id}", response_model=schemas.Entry, operation_id="read_entry")
def read_entry(entry_id: int, db: Session = Depends(get_db)):
    entry = entry_service.get_entry(db, entry_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Entry not found")
    return entry

@router.put("/{entry_id}", response_model=schemas.Entry, operation_id="update_entry")
def update_entry(entry_id: int, entry: schemas.EntryUpdate, db: Session = Depends(get_db)):
    updated_entry = entry_service.update_entry(db, entry_id, entry)
    if updated_entry is None:
        raise HTTPException(status_code=404, detail="Entry not found")
    return updated_entry

@router.delete("/{entry_id}", response_model=schemas.EntryDelete, operation_id="delete_entry")
def delete_entry(entry_id: int, db: Session = Depends(get_db)):
    deleted_entry = entry_service.delete_entry(db, entry_id)
    if deleted_entry is None:
        raise HTTPException(status_code=404, detail="Entry not found")
    return schemas.EntryDelete(id=deleted_entry.id)