# ============================================================
# AI GLUE v8.0 — EDUCATION DATA ROUTER
# ============================================================

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from core.database import db, Country, University, City, Campus, Department, Course, IntakeSeat, User
from auth.session import verify_token

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# ---------- Pydantic Models ----------
class CountryCreate(BaseModel):
    name: str
    iso_code: str
    visa_difficulty: Optional[float] = 0.0
    cost_of_living_index: Optional[float] = 0.0

class UniversityCreate(BaseModel):
    country_id: str
    name: str
    website: Optional[str] = None
    ranking_global: Optional[int] = None
    ranking_national: Optional[int] = None
    accreditation: Optional[str] = None
    domain: Optional[str] = None

class CourseCreate(BaseModel):
    department_id: str
    name: str
    level: Optional[str] = None
    duration_months: Optional[int] = None
    tuition_fee: Optional[float] = None
    currency: str = "USD"
    admission_requirements: Optional[dict] = None
    course_url: Optional[str] = None

class IntakeSeatCreate(BaseModel):
    course_id: str
    academic_year: str
    total_seats: int
    filled_seats: int = 0
    waiting_seats: int = 0

# ---------- Helper ----------
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

def require_admin(user: User = Depends(get_current_user)):
    # Simplified: check if user has admin role
    session = db.get_session()
    from core.database import UserRole
    roles = session.query(UserRole.role_code).filter(UserRole.user_id == user.id).all()
    session.close()
    role_codes = [r[0] for r in roles]
    if "ADMIN" not in role_codes:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

# ---------- Country Endpoints ----------
@router.post("/countries", response_model=dict)
def create_country(country_data: CountryCreate, admin: User = Depends(require_admin)):
    session = db.get_session()
    existing = session.query(Country).filter(Country.iso_code == country_data.iso_code).first()
    if existing:
        session.close()
        raise HTTPException(status_code=400, detail="Country with this ISO code already exists")
    
    new_country = Country(
        name=country_data.name,
        iso_code=country_data.iso_code,
        visa_difficulty=country_data.visa_difficulty,
        cost_of_living_index=country_data.cost_of_living_index
    )
    session.add(new_country)
    session.commit()
    session.refresh(new_country)
    country_id = new_country.id
    session.close()
    return {"id": country_id, "name": new_country.name, "message": "Country created"}

@router.get("/countries", response_model=list)
def get_countries():
    session = db.get_session()
    countries = session.query(Country).all()
    session.close()
    return [
        {"id": c.id, "name": c.name, "iso_code": c.iso_code, "visa_difficulty": c.visa_difficulty}
        for c in countries
    ]

@router.get("/countries/{country_id}", response_model=dict)
def get_country(country_id: str):
    session = db.get_session()
    country = session.query(Country).filter(Country.id == country_id).first()
    session.close()
    if not country:
        raise HTTPException(status_code=404, detail="Country not found")
    return {
        "id": country.id,
        "name": country.name,
        "iso_code": country.iso_code,
        "visa_difficulty": country.visa_difficulty,
        "cost_of_living_index": country.cost_of_living_index
    }

# ---------- University Endpoints ----------
@router.post("/universities", response_model=dict)
def create_university(univ_data: UniversityCreate, admin: User = Depends(require_admin)):
    session = db.get_session()
    country = session.query(Country).filter(Country.id == univ_data.country_id).first()
    if not country:
        session.close()
        raise HTTPException(status_code=404, detail="Country not found")
    
    new_univ = University(
        country_id=univ_data.country_id,
        name=univ_data.name,
        website=univ_data.website,
        ranking_global=univ_data.ranking_global,
        ranking_national=univ_data.ranking_national,
        accreditation=univ_data.accreditation,
        domain=univ_data.domain
    )
    session.add(new_univ)
    session.commit()
    session.refresh(new_univ)
    univ_id = new_univ.id
    session.close()
    return {"id": univ_id, "name": new_univ.name, "message": "University created"}

@router.get("/universities", response_model=list)
def get_universities(country_id: Optional[str] = None):
    session = db.get_session()
    query = session.query(University)
    if country_id:
        query = query.filter(University.country_id == country_id)
    universities = query.all()
    session.close()
    return [
        {"id": u.id, "name": u.name, "country_id": u.country_id, "ranking_global": u.ranking_global}
        for u in universities
    ]

@router.get("/universities/{university_id}", response_model=dict)
def get_university(university_id: str):
    session = db.get_session()
    univ = session.query(University).filter(University.id == university_id).first()
    session.close()
    if not univ:
        raise HTTPException(status_code=404, detail="University not found")
    return {
        "id": univ.id,
        "name": univ.name,
        "country_id": univ.country_id,
        "website": univ.website,
        "ranking_global": univ.ranking_global,
        "ranking_national": univ.ranking_national,
        "accreditation": univ.accreditation,
        "domain": univ.domain
    }

# ---------- Course Endpoints ----------
@router.post("/courses", response_model=dict)
def create_course(course_data: CourseCreate, admin: User = Depends(require_admin)):
    session = db.get_session()
    dept = session.query(Department).filter(Department.id == course_data.department_id).first()
    if not dept:
        session.close()
        raise HTTPException(status_code=404, detail="Department not found")
    
    new_course = Course(
        department_id=course_data.department_id,
        name=course_data.name,
        level=course_data.level,
        duration_months=course_data.duration_months,
        tuition_fee=course_data.tuition_fee,
        currency=course_data.currency,
        admission_requirements=course_data.admission_requirements,
        course_url=course_data.course_url
    )
    session.add(new_course)
    session.commit()
    session.refresh(new_course)
    course_id = new_course.id
    session.close()
    return {"id": course_id, "name": new_course.name, "message": "Course created"}

@router.get("/courses", response_model=list)
def get_courses(department_id: Optional[str] = None):
    session = db.get_session()
    query = session.query(Course)
    if department_id:
        query = query.filter(Course.department_id == department_id)
    courses = query.all()
    session.close()
    return [
        {"id": c.id, "name": c.name, "level": c.level, "duration_months": c.duration_months}
        for c in courses
    ]

@router.get("/courses/{course_id}", response_model=dict)
def get_course(course_id: str):
    session = db.get_session()
    course = session.query(Course).filter(Course.id == course_id).first()
    session.close()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return {
        "id": course.id,
        "name": course.name,
        "level": course.level,
        "duration_months": course.duration_months,
        "tuition_fee": course.tuition_fee,
        "currency": course.currency,
        "admission_requirements": course.admission_requirements,
        "course_url": course.course_url,
        "department_id": course.department_id
    }

# ---------- Intake Seats Endpoints ----------
@router.post("/intake-seats", response_model=dict)
def create_intake_seat(seat_data: IntakeSeatCreate, admin: User = Depends(require_admin)):
    session = db.get_session()
    course = session.query(Course).filter(Course.id == seat_data.course_id).first()
    if not course:
        session.close()
        raise HTTPException(status_code=404, detail="Course not found")
    
    existing = session.query(IntakeSeat).filter(
        IntakeSeat.course_id == seat_data.course_id,
        IntakeSeat.academic_year == seat_data.academic_year
    ).first()
    if existing:
        session.close()
        raise HTTPException(status_code=400, detail="Intake seat for this course and year already exists")
    
    new_seat = IntakeSeat(
        course_id=seat_data.course_id,
        academic_year=seat_data.academic_year,
        total_seats=seat_data.total_seats,
        filled_seats=seat_data.filled_seats,
        waiting_seats=seat_data.waiting_seats
    )
    session.add(new_seat)
    session.commit()
    session.refresh(new_seat)
    seat_id = new_seat.id
    session.close()
    return {"id": seat_id, "message": "Intake seat created"}

@router.get("/intake-seats/{course_id}", response_model=list)
def get_intake_seats(course_id: str):
    session = db.get_session()
    seats = session.query(IntakeSeat).filter(IntakeSeat.course_id == course_id).all()
    session.close()
    return [
        {
            "id": s.id,
            "academic_year": s.academic_year,
            "total_seats": s.total_seats,
            "filled_seats": s.filled_seats,
            "waiting_seats": s.waiting_seats,
            "last_updated": s.last_updated
        }
        for s in seats
    ]

# ---------- City, Campus, Department (Additional) ----------
@router.post("/cities", response_model=dict)
def create_city(country_id: str, name: str, state: Optional[str] = None, admin: User = Depends(require_admin)):
    session = db.get_session()
    country = session.query(Country).filter(Country.id == country_id).first()
    if not country:
        session.close()
        raise HTTPException(status_code=404, detail="Country not found")
    
    new_city = City(country_id=country_id, name=name, state=state)
    session.add(new_city)
    session.commit()
    session.refresh(new_city)
    city_id = new_city.id
    session.close()
    return {"id": city_id, "name": name, "message": "City created"}

@router.get("/cities", response_model=list)
def get_cities(country_id: Optional[str] = None):
    session = db.get_session()
    query = session.query(City)
    if country_id:
        query = query.filter(City.country_id == country_id)
    cities = query.all()
    session.close()
    return [{"id": c.id, "name": c.name, "state": c.state, "country_id": c.country_id} for c in cities]

@router.post("/campuses", response_model=dict)
def create_campus(
    university_id: str,
    city_id: str,
    name: Optional[str] = None,
    address: Optional[str] = None,
    established_year: Optional[int] = None,
    admin: User = Depends(require_admin)
):
    session = db.get_session()
    univ = session.query(University).filter(University.id == university_id).first()
    if not univ:
        session.close()
        raise HTTPException(status_code=404, detail="University not found")
    city = session.query(City).filter(City.id == city_id).first()
    if not city:
        session.close()
        raise HTTPException(status_code=404, detail="City not found")
    
    new_campus = Campus(
        university_id=university_id,
        city_id=city_id,
        name=name,
        address=address,
        established_year=established_year
    )
    session.add(new_campus)
    session.commit()
    session.refresh(new_campus)
    campus_id = new_campus.id
    session.close()
    return {"id": campus_id, "message": "Campus created"}

@router.post("/departments", response_model=dict)
def create_department(campus_id: str, name: str, admin: User = Depends(require_admin)):
    session = db.get_session()
    campus = session.query(Campus).filter(Campus.id == campus_id).first()
    if not campus:
        session.close()
        raise HTTPException(status_code=404, detail="Campus not found")
    
    new_dept = Department(campus_id=campus_id, name=name)
    session.add(new_dept)
    session.commit()
    session.refresh(new_dept)
    dept_id = new_dept.id
    session.close()
    return {"id": dept_id, "name": name, "message": "Department created"}