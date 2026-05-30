"""
init_db.py — Run this once to initialize the database with sample data.
Usage: python init_db.py
"""
from app import app, db, Subject, Prerequisite
from datetime import date, timedelta

def seed():
    with app.app_context():
        db.create_all()
        print("✅ Tables created")

        # Only seed if empty
        if Subject.query.count() > 0:
            print("ℹ️  Database already has data. Skipping seed.")
            return

        today = date.today()
        samples = [
            Subject(name="Data Structures & Algorithms", difficulty=8, subject_type="coding",
                    deadline=(today + timedelta(days=14)).isoformat(), estimated_hours=30, color="#6366f1"),
            Subject(name="Machine Learning Theory", difficulty=7, subject_type="theory",
                    deadline=(today + timedelta(days=21)).isoformat(), estimated_hours=20, color="#0ea5e9"),
            Subject(name="Linear Algebra", difficulty=6, subject_type="math",
                    deadline=(today + timedelta(days=10)).isoformat(), estimated_hours=15, color="#f59e0b"),
            Subject(name="Final Year Project", difficulty=9, subject_type="project",
                    deadline=(today + timedelta(days=30)).isoformat(), estimated_hours=40, color="#10b981"),
            Subject(name="Operating Systems", difficulty=7, subject_type="theory",
                    deadline=(today + timedelta(days=7)).isoformat(), estimated_hours=18, color="#8b5cf6"),
        ]
        for s in samples:
            db.session.add(s)
        db.session.commit()

        # Prerequisites: Linear Algebra → Machine Learning → Final Year Project
        #               DSA → Final Year Project
        subs = {s.name: s.id for s in Subject.query.all()}
        prereqs = [
            (subs["Linear Algebra"], subs["Machine Learning Theory"]),
            (subs["Machine Learning Theory"], subs["Final Year Project"]),
            (subs["Data Structures & Algorithms"], subs["Final Year Project"]),
        ]
        for prereq_id, subject_id in prereqs:
            db.session.add(Prerequisite(subject_id=subject_id, prerequisite_id=prereq_id))
        db.session.commit()

        print("✅ Sample data seeded!")
        print("   Subjects: DSA, ML Theory, Linear Algebra, Final Year Project, OS")
        print("   Graph: Linear Algebra → ML → Project; DSA → Project")

if __name__ == "__main__":
    seed()