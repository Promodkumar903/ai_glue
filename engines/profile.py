"""
AI GLUE — Profile Engine (Blueprint Section 5.2)
"""
from sqlalchemy.orm import Session
from core.database import db, CandidateProfile, User
from datetime import datetime
from core.audit import log_audit

class ProfileEngine:
    @staticmethod
    def create_profile(user_id: str, education: list = None, experience: list = None, skills: list = None, languages: list = None, session: Session = None):
        if session is None:
            session = db.get_session()
        
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            return {"error": "User not found"}
        
        existing = session.query(CandidateProfile).filter(CandidateProfile.user_id == user_id).first()
        if existing:
            return {"error": "Profile already exists", "profile_id": existing.id}
        
        profile = CandidateProfile(
            user_id=user_id,
            education=education or [],
            experience=experience or [],
            skills=skills or [],
            languages=languages or [],
            completeness_pct=25
        )
        session.add(profile)
        session.commit()
        session.refresh(profile)
        
        # Update completeness
        completeness = 0
        if profile.education and len(profile.education) > 0:
            completeness += 25
        if profile.experience and len(profile.experience) > 0:
            completeness += 25
        if profile.skills and len(profile.skills) > 0:
            completeness += 25
        if profile.languages and len(profile.languages) > 0:
            completeness += 25
        profile.completeness_pct = completeness
        session.commit()
        
        log_audit(
            actor_id=user_id,
            action="PROFILE_CREATE",
            target_type="PROFILE",
            target_id=str(profile.id),
            after={"completeness": completeness},
            reason="Profile created"
        )
        
        return {
            "profile_id": str(profile.id),
            "user_id": str(profile.user_id),
            "completeness_pct": profile.completeness_pct,
            "message": "Profile created successfully"
        }

    @staticmethod
    def update_profile(user_id: str, education: list = None, experience: list = None, skills: list = None, languages: list = None, session: Session = None):
        if session is None:
            session = db.get_session()
        
        profile = session.query(CandidateProfile).filter(CandidateProfile.user_id == user_id).first()
        if not profile:
            return {"error": "Profile not found"}
        
        if education is not None:
            profile.education = education
        if experience is not None:
            profile.experience = experience
        if skills is not None:
            profile.skills = skills
        if languages is not None:
            profile.languages = languages
        
        completeness = 0
        if profile.education and len(profile.education) > 0:
            completeness += 25
        if profile.experience and len(profile.experience) > 0:
            completeness += 25
        if profile.skills and len(profile.skills) > 0:
            completeness += 25
        if profile.languages and len(profile.languages) > 0:
            completeness += 25
        profile.completeness_pct = completeness
        profile.updated_at = datetime.utcnow()
        session.commit()
        
        log_audit(
            actor_id=user_id,
            action="PROFILE_UPDATE",
            target_type="PROFILE",
            target_id=str(profile.id),
            before={"completeness": None},
            after={"completeness": completeness},
            reason="Profile updated"
        )
        
        return {
            "profile_id": str(profile.id),
            "user_id": str(profile.user_id),
            "completeness_pct": profile.completeness_pct,
            "message": "Profile updated successfully"
        }

    @staticmethod
    def get_profile(user_id: str, session: Session = None):
        if session is None:
            session = db.get_session()
        
        profile = session.query(CandidateProfile).filter(CandidateProfile.user_id == user_id).first()
        if not profile:
            return {"error": "Profile not found"}
        
        return {
            "profile_id": str(profile.id),
            "user_id": str(profile.user_id),
            "education": profile.education,
            "experience": profile.experience,
            "skills": profile.skills,
            "languages": profile.languages,
            "completeness_pct": profile.completeness_pct
        }

profile = ProfileEngine()