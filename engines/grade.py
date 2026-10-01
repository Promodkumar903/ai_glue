"""
AI GLUE — Grade Engine
Week-based rolling performance grading for agents/brokers
Grades: A (Elite), B (Trusted), C (Verified), D (Standard), E (Probation)
"""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from core.database import db, User, AgentGrade, GradeHistory


class GradeEngine:

    # ---------- Weight configuration ----------
    WEIGHTS = {
        "week_completion": 0.40,
        "career_completion": 0.20,
        "response_time": 0.15,
        "rating": 0.15,
        "compliance": 0.10,
    }

    # Grade thresholds
    THRESHOLDS = [
        (90, "A"),
        (75, "B"),
        (60, "C"),
        (40, "D"),
        (0,  "E"),
    ]

    # ---------- Core scoring ----------
    @staticmethod
    def _score_week_completion(assigned: int, completed: int) -> float:
        if assigned == 0:
            return 50.0  # neutral if no work assigned
        return min(100.0, (completed / assigned) * 100.0)

    @staticmethod
    def _score_career_completion(total: int, completed: int) -> float:
        if total == 0:
            return 50.0
        return min(100.0, (completed / total) * 100.0)

    @staticmethod
    def _score_response_time(avg_min: int) -> float:
        # 0 min = 100, 120+ min = 0
        if avg_min <= 0:
            return 100.0
        if avg_min >= 120:
            return 0.0
        return max(0.0, 100.0 - (avg_min / 120.0 * 100.0))

    @staticmethod
    def _score_rating(rating: float) -> float:
        # rating out of 5 → percentage
        return max(0.0, min(100.0, (rating / 5.0) * 100.0))

    @staticmethod
    def _score_compliance(disputes: int) -> float:
        # 0 disputes = 100, 5+ = 0
        return max(0.0, 100.0 - (disputes * 20.0))

    # ---------- Grade calculation ----------
    @classmethod
    def calculate_for_agent(cls, agent_id: str, session: Session = None):
        _auto = session is None
        if session is None:
            session = db.get_session()

        try:
            week_start = datetime.utcnow() - timedelta(days=datetime.utcnow().weekday())
            week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)

            # Fetch or create current week row
            row = session.query(AgentGrade).filter(
                AgentGrade.agent_id == agent_id,
                AgentGrade.week_start == week_start
            ).first()

            if not row:
                row = AgentGrade(agent_id=agent_id, week_start=week_start)
                session.add(row)
                session.flush()

            # Scores
            s_week = cls._score_week_completion(row.demands_assigned, row.demands_completed)
            s_career = cls._score_career_completion(row.career_demands, row.career_completed)
            s_resp = cls._score_response_time(row.avg_response_min or 0)
            s_rating = cls._score_rating(row.rating or 0.0)
            s_comp = cls._score_compliance(row.disputes or 0)

            total = (
                s_week   * cls.WEIGHTS["week_completion"] +
                s_career * cls.WEIGHTS["career_completion"] +
                s_resp   * cls.WEIGHTS["response_time"] +
                s_rating * cls.WEIGHTS["rating"] +
                s_comp   * cls.WEIGHTS["compliance"]
            )

            new_grade = "E"
            for threshold, g in cls.THRESHOLDS:
                if total >= threshold:
                    new_grade = g
                    break

            # Trend
            old_grade = row.grade
            trend = "stable"
            if old_grade:
                order = {"A": 5, "B": 4, "C": 3, "D": 2, "E": 1}
                if order.get(new_grade, 0) > order.get(old_grade, 0):
                    trend = "up"
                elif order.get(new_grade, 0) < order.get(old_grade, 0):
                    trend = "down"

            # Log history
            if old_grade and old_grade != new_grade:
                session.add(GradeHistory(
                    agent_id=agent_id,
                    old_grade=old_grade,
                    new_grade=new_grade,
                    reason=f"Weekly recalc — score {total:.1f}",
                    week_start=week_start
                ))

            row.grade = new_grade
            row.score = round(total, 2)
            row.trend = trend
            row.calculated_at = datetime.utcnow()
            row.valid_until = week_start + timedelta(days=7)

            session.commit()
            return {
                "agent_id": agent_id,
                "grade": new_grade,
                "score": round(total, 2),
                "trend": trend,
                "week_start": str(week_start),
                "factors": {
                    "week_completion": round(s_week, 1),
                    "career_completion": round(s_career, 1),
                    "response_time": round(s_resp, 1),
                    "rating": round(s_rating, 1),
                    "compliance": round(s_comp, 1),
                }
            }
        except Exception as e:
            session.rollback()
            return {"error": str(e), "agent_id": agent_id}
        finally:
            if _auto:
                session.close()

    # ---------- Bulk recalc ----------
    @classmethod
    def recalculate_all(cls, session: Session = None):
        _auto = session is None
        if session is None:
            session = db.get_session()
        try:
            agents = session.query(User).filter(User.status == 'ACTIVE').all()
            results = []
            for a in agents:
                r = cls.calculate_for_agent(a.id, session)
                results.append(r)
            return {"total": len(results), "results": results}
        finally:
            if _auto:
                session.close()

    # ---------- Fetch ----------
    @staticmethod
    def get_grade(agent_id: str, session: Session = None):
        _auto = session is None
        if session is None:
            session = db.get_session()
        try:
            row = session.query(AgentGrade).filter(
                AgentGrade.agent_id == agent_id
            ).order_by(AgentGrade.calculated_at.desc()).first()
            if not row:
                return {"agent_id": agent_id, "grade": None, "message": "No grade yet"}
            return {
                "agent_id": agent_id,
                "grade": row.grade,
                "score": row.score,
                "trend": row.trend,
                "week_start": str(row.week_start),
                "week_completion_rate": row.week_completion_rate,
                "career_completion_rate": row.career_completion_rate,
                "rating": row.rating,
                "disputes": row.disputes,
            }
        finally:
            if _auto:
                session.close()

    @staticmethod
    def leaderboard(session: Session = None, limit: int = 20):
        _auto = session is None
        if session is None:
            session = db.get_session()
        try:
            rows = session.query(AgentGrade).order_by(
                AgentGrade.score.desc()
            ).limit(limit).all()
            return [
                {
                    "agent_id": r.agent_id,
                    "grade": r.grade,
                    "score": r.score,
                    "trend": r.trend,
                }
                for r in rows
            ]
        finally:
            if _auto:
                session.close()


grade_engine = GradeEngine()