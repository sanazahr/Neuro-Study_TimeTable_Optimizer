"""
Database Models for AI Study Planner
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
import math

db = SQLAlchemy()

class Subject(db.Model):
    __tablename__ = 'subjects'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    difficulty = db.Column(db.Float, default=5.0)  # 1-10
    subject_type = db.Column(db.String(50), default='theory')  # coding, theory, math, project
    deadline = db.Column(db.String(20), nullable=True)
    estimated_hours = db.Column(db.Float, default=10.0)
    completed_hours = db.Column(db.Float, default=0.0)
    color = db.Column(db.String(20), default='#6366f1')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Student preferences
    preferred_time_start = db.Column(db.String(10), default='09:00')  # 9 AM
    preferred_time_end = db.Column(db.String(10), default='17:00')   # 5 PM
    is_weak_subject = db.Column(db.Boolean, default=False)
    priority = db.Column(db.Integer, default=1)  # 1=normal, 2=high, 3=exam
    
    def days_left(self):
        if not self.deadline:
            return 999
        try:
            dl = datetime.strptime(self.deadline, "%Y-%m-%d").date()
            return max(0, (dl - date.today()).days)
        except:
            return 999
    
    def urgency_score(self):
        """Urgency = difficulty² / max(days_left, 1)"""
        days = max(self.days_left(), 1)
        return (self.difficulty ** 2) / days
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "difficulty": self.difficulty,
            "type": self.subject_type,
            "deadline": self.deadline,
            "estimated_hours": self.estimated_hours,
            "completed_hours": self.completed_hours,
            "color": self.color,
            "days_left": self.days_left(),
            "urgency_score": round(self.urgency_score(), 2),
            "progress": round((self.completed_hours / self.estimated_hours) * 100, 1) if self.estimated_hours > 0 else 0,
            "preferred_time_start": self.preferred_time_start,
            "preferred_time_end": self.preferred_time_end,
            "is_weak_subject": self.is_weak_subject,
            "priority": self.priority
        }


class StudySession(db.Model):
    __tablename__ = 'study_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'))
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=True)
    actual_hours = db.Column(db.Float, default=0.0)
    notes = db.Column(db.Text, nullable=True)
    cognitive_load = db.Column(db.Float, default=0.0)
    date_studied = db.Column(db.String(20), nullable=True)
    
    def to_dict(self):
        return {
            "id": self.id,
            "subject_id": self.subject_id,
            "actual_hours": self.actual_hours,
            "cognitive_load": self.cognitive_load,
            "date_studied": self.date_studied,
            "notes": self.notes
        }


class TimePreference(db.Model):
    __tablename__ = 'time_preferences'
    
    id = db.Column(db.Integer, primary_key=True)
    day_of_week = db.Column(db.Integer)  # 0=Monday, 6=Sunday
    start_time = db.Column(db.String(10), default='09:00')
    end_time = db.Column(db.String(10), default='17:00')
    is_available = db.Column(db.Boolean, default=True)