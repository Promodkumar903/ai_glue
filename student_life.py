from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

from core.database import db, StudentLife, User
from auth.session import verify_token
from sqlalchemy.orm.attributes import flag_modified

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

class PartTimeJob(BaseModel):
    job_title: str
    company: str
    hours_per_week: int
    pay_rate: float
    currency: str = "USD"
    status: str = "ACTIVE"
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class BookLibrary(BaseModel):
    book_name: str
    author: str
    issue_date: datetime
    return_date: Optional[datetime] = None
    status: str = "ISSUED"

def get_current_user(token: str):
    payload = verify_token(token)
    if "error" in payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    session = db.get_session()
    user = session.query(User).filter(User.id == user_id).first()
    session.close()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def get_or_create_student_life(session, user_id: str):
    student_life = session.query(StudentLife).filter(StudentLife.user_id == user_id).first()
    if not student_life:
        student_life = StudentLife(
            user_id=user_id,
            country="",
            city="",
            university="",
            semester=1,
            preferences={}
        )
        session.add(student_life)
        session.commit()
        session.refresh(student_life)
    return student_life

@router.post("/jobs/add", response_model=dict)
def add_part_time_job(job_data: PartTimeJob, token: str = Depends(oauth2_scheme)):
    user = get_current_user(token)
    session = db.get_session()
    student_life = get_or_create_student_life(session, user.id)
    
    prefs = student_life.preferences or {}
    if "part_time_jobs" not in prefs:
        prefs["part_time_jobs"] = []
    
    job_dict = job_data.dict()
    job_dict["id"] = str(uuid.uuid4())
    # ✅ Convert datetime to ISO string
    if job_dict.get("start_date"):
        job_dict["start_date"] = job_dict["start_date"].isoformat()
    if job_dict.get("end_date"):
        job_dict["end_date"] = job_dict["end_date"].isoformat()
    
    prefs["part_time_jobs"].append(job_dict)
    
    student_life.preferences = prefs
    flag_modified(student_life, "preferences")
    session.commit()
    session.close()
    
    return {"message": "Part-time job added", "job": job_dict}

@router.get("/jobs", response_model=list)
def get_part_time_jobs(token: str = Depends(oauth2_scheme)):
    user = get_current_user(token)
    session = db.get_session()
    student_life = session.query(StudentLife).filter(StudentLife.user_id == user.id).first()
    session.close()
    if not student_life or not student_life.preferences:
        return []
    return student_life.preferences.get("part_time_jobs", [])

@router.post("/books/add", response_model=dict)
def add_book(book_data: BookLibrary, token: str = Depends(oauth2_scheme)):
    user = get_current_user(token)
    session = db.get_session()
    student_life = get_or_create_student_life(session, user.id)
    
    prefs = student_life.preferences or {}
    if "books_library" not in prefs:
        prefs["books_library"] = []
    
    book_dict = book_data.dict()
    book_dict["id"] = str(uuid.uuid4())
    # ✅ Convert datetime to ISO string
    if book_dict.get("issue_date"):
        book_dict["issue_date"] = book_dict["issue_date"].isoformat()
    if book_dict.get("return_date"):
        book_dict["return_date"] = book_dict["return_date"].isoformat()
    
    prefs["books_library"].append(book_dict)
    
    student_life.preferences = prefs
    flag_modified(student_life, "preferences")
    session.commit()
    session.close()
    return {"message": "Book added to library", "book": book_dict}

@router.get("/books", response_model=list)
def get_books(token: str = Depends(oauth2_scheme)):
    user = get_current_user(token)
    session = db.get_session()
    student_life = session.query(StudentLife).filter(StudentLife.user_id == user.id).first()
    session.close()
    if not student_life or not student_life.preferences:
        return []
    return student_life.preferences.get("books_library", [])

@router.put("/books/{book_id}/return", response_model=dict)
def return_book(book_id: str, token: str = Depends(oauth2_scheme)):
    user = get_current_user(token)
    session = db.get_session()
    student_life = get_or_create_student_life(session, user.id)
    prefs = student_life.preferences or {}
    books = prefs.get("books_library", [])
    for book in books:
        if book.get("id") == book_id:
            book["status"] = "RETURNED"
            book["return_date"] = datetime.utcnow().isoformat()
            student_life.preferences = prefs
            flag_modified(student_life, "preferences")
            session.commit()
            session.close()
            return {"message": "Book returned successfully", "book": book}
    session.close()
    raise HTTPException(status_code=404, detail="Book not found")

@router.post("/need", response_model=dict)
def set_current_need(need: str, token: str = Depends(oauth2_scheme)):
    user = get_current_user(token)
    session = db.get_session()
    student_life = get_or_create_student_life(session, user.id)
    student_life.current_need = need
    student_life.need_detected_at = datetime.utcnow()
    session.commit()
    session.close()
    return {"user_id": user.id, "current_need": need, "message": "Need updated"}

@router.get("/me", response_model=dict)
def get_my_student_life(token: str = Depends(oauth2_scheme)):
    user = get_current_user(token)
    session = db.get_session()
    student_life = session.query(StudentLife).filter(StudentLife.user_id == user.id).first()
    session.close()
    if not student_life:
        return {"user_id": user.id, "message": "No student life data found"}
    return {
        "id": student_life.id,
        "user_id": student_life.user_id,
        "country": student_life.country,
        "city": student_life.city,
        "university": student_life.university,
        "semester": student_life.semester,
        "preferences": student_life.preferences,
        "current_need": student_life.current_need
    }