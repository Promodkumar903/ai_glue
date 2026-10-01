"""
AI GLUE — Matching Engine (Blueprint Section 7.2)
Calculates Eligibility + Match Score between Candidate and Opportunity
"""
from sqlalchemy.orm import Session
from core.database import User, Opportunity, Application

class MatchingEngine:
    @staticmethod
    def check_eligibility(candidate_id: str, opportunity_id: str, session: Session):
        """Hard eligibility check (Blueprint Section 7.2)"""
        user = session.query(User).filter(User.id == candidate_id).first()
        opp = session.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
        
        if not user or not opp:
            return {"eligible": False, "reason": "User or Opportunity not found"}
        
        # For now, simple check: if user has a profile (we'll expand later)
        from core.database import CandidateProfile
        profile = session.query(CandidateProfile).filter(CandidateProfile.user_id == candidate_id).first()
        
        if not profile:
            return {"eligible": False, "reason": "Candidate profile incomplete"}
        
        # Hard requirement: status must be OPEN
        if opp.status != "OPEN":
            return {"eligible": False, "reason": f"Opportunity status is {opp.status}, not OPEN"}
        
        return {"eligible": True, "reason": "All hard requirements passed"}
    
    @staticmethod
    def calculate_match_score(candidate_id: str, opportunity_id: str, session: Session):
        """Calculate match score (0-100) based on profile match"""
        # First check eligibility
        eligibility = MatchingEngine.check_eligibility(candidate_id, opportunity_id, session)
        if not eligibility["eligible"]:
            return {
                "candidate_id": candidate_id,
                "opportunity_id": opportunity_id,
                "score": 0,
                "eligible": False,
                "reason": eligibility["reason"]
            }
        
        # Get profile and opportunity
        from core.database import CandidateProfile
        user = session.query(User).filter(User.id == candidate_id).first()
        opp = session.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
        profile = session.query(CandidateProfile).filter(CandidateProfile.user_id == candidate_id).first()
        
        # Simple scoring: keyword match in title/description vs profile skills
        # For now, we just give a random score between 50-95 as placeholder
        # In real implementation, this will compare skills, education, experience
        import random
        score = random.randint(50, 95)
        
        # Store match score in database
        from core.database import MatchScore
        match = session.query(MatchScore).filter(
            MatchScore.candidate_id == candidate_id,
            MatchScore.opportunity_id == opportunity_id
        ).first()
        if match:
            match.score = score
        else:
            match = MatchScore(
                candidate_id=candidate_id,
                opportunity_id=opportunity_id,
                score=score
            )
            session.add(match)
        session.commit()
        
        return {
            "candidate_id": candidate_id,
            "opportunity_id": opportunity_id,
            "candidate_name": user.full_name,
            "opportunity_title": opp.title,
            "score": score,
            "eligible": True,
            "reason": "Match calculated successfully"
        }

# Singleton
matching = MatchingEngine()