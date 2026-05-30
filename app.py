"""
NeuroStudy: AI-Powered Study Planner & Intelligent Timetable Optimizer
"""

import heapq
import json
import math
import os
import random
from collections import defaultdict
from datetime import datetime, timedelta, date

from flask import Flask, jsonify, render_template, request, send_file
from flask_sqlalchemy import SQLAlchemy

from ai_models.exam_predictor import ExamScorePredictor
from ai_models.time_optimizer import TimeOptimizer
from ai_models.quiz_generator import QuizGenerator
from ai_models.burnout_predictor import BurnoutPredictor


app = Flask(__name__)
app.secret_key = "neurostudy_secret_2024"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///study_planner.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ============================================================
# Database Models
# ============================================================
class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    difficulty = db.Column(db.Float, default=5.0)
    subject_type = db.Column(db.String(50), default="theory")
    deadline = db.Column(db.String(20), nullable=True)
    estimated_hours = db.Column(db.Float, default=10.0)
    completed_hours = db.Column(db.Float, default=0.0)
    color = db.Column(db.String(20), default="#4f46e5")
    is_weak = db.Column(db.Boolean, default=False)
    schedule_slots = db.Column(db.Text, default="[]")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def days_left(self):
        if not self.deadline:
            return 999
        try:
            dl = datetime.strptime(self.deadline, "%Y-%m-%d").date()
            return max(0, (dl - date.today()).days)
        except:
            return 999

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
            "progress": round((self.completed_hours / max(self.estimated_hours, 1)) * 100, 1),
            "is_weak": self.is_weak,
            "schedule_slots": json.loads(self.schedule_slots) if self.schedule_slots else [],
        }


class StudySession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey("subject.id"))
    start_time = db.Column(db.DateTime, default=datetime.utcnow)  # FIXED: Added missing column
    end_time = db.Column(db.DateTime, nullable=True)  # FIXED: Added for completeness
    actual_hours = db.Column(db.Float, default=0.0)
    notes = db.Column(db.Text, nullable=True)
    cognitive_load = db.Column(db.Float, default=0.0)
    date_studied = db.Column(db.String(20))


# ============================================================
# Helper Functions
# ============================================================
def classify_subject_type(name: str) -> str:
    name_lower = name.lower()
    if any(w in name_lower for w in ["python", "java", "code", "algorithm", "dsa", "programming"]):
        return "coding"
    if any(w in name_lower for w in ["math", "calculus", "algebra", "statistics"]):
        return "math"
    if any(w in name_lower for w in ["project", "thesis", "research", "build"]):
        return "project"
    return "theory"


def predict_completion_probability(subject):
    """
    Calculate REAL completion probability based on actual progress.
    - 0% if no hours completed
    - 100% if completed_hours >= estimated_hours
    - Otherwise percentage based on completed_hours / estimated_hours
    """
    if subject.estimated_hours <= 0:
        return 1.0
    
    if subject.completed_hours <= 0:
        return 0.0
    
    if subject.completed_hours >= subject.estimated_hours:
        return 1.0
    
    progress_ratio = subject.completed_hours / subject.estimated_hours
    
    days_left = subject.days_left()
    if days_left < 999 and days_left > 0:
        remaining = max(0, subject.estimated_hours - subject.completed_hours)
        hours_per_day_needed = remaining / days_left
        if hours_per_day_needed > 4:
            progress_ratio *= 0.7
    
    return round(min(0.99, progress_ratio), 2)


def get_burnout_status():
    """Calculate real burnout based on actual study sessions"""
    seven_days_ago = (date.today() - timedelta(days=7)).isoformat()
    sessions = StudySession.query.filter(
        StudySession.date_studied >= seven_days_ago
    ).all()
    
    if not sessions:
        return {"level": "healthy", "avg_load": 0.0, "suggestion": "Start studying to see burnout status!"}
    
    total_hours = sum(s.actual_hours for s in sessions)
    avg_load = total_hours / max(len(sessions), 1)
    
    if total_hours > 35:
        return {"level": "critical", "avg_load": round(avg_load, 2), "total_hours": round(total_hours, 1), "suggestion": "⚠️ Critical burnout risk! Take a full rest day."}
    elif total_hours > 25:
        return {"level": "warning", "avg_load": round(avg_load, 2), "total_hours": round(total_hours, 1), "suggestion": "⚠️ Warning: You're studying a lot. Take breaks!"}
    else:
        return {"level": "healthy", "avg_load": round(avg_load, 2), "total_hours": round(total_hours, 1), "suggestion": "✅ You're doing great! Keep it up."}


# ============================================================
# API Routes
# ============================================================
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/subjects", methods=["GET"])
def get_subjects():
    subjects = Subject.query.all()
    result = []
    for s in subjects:
        d = s.to_dict()
        d["completion_probability"] = predict_completion_probability(s)
        result.append(d)
    return jsonify(result)


@app.route("/api/subjects", methods=["POST"])
def add_subject():
    try:
        data = request.json
        name = data.get("name", "").strip()
        if not name:
            return jsonify({"error": "Name required"}), 400

        subject_type = data.get("type") or classify_subject_type(name)
        color_map = {"coding": "#4f46e5", "theory": "#0ea5e9", "math": "#f59e0b", "project": "#10b981"}
        
        schedule_slots = json.dumps(data.get("schedule_slots", []))
        
        subject = Subject(
            name=name,
            difficulty=float(data.get("difficulty", 5)),
            subject_type=subject_type,
            deadline=data.get("deadline"),
            estimated_hours=float(data.get("estimated_hours", 10)),
            color=data.get("color", color_map.get(subject_type, "#4f46e5")),
            schedule_slots=schedule_slots,
        )
        db.session.add(subject)
        db.session.commit()
        
        return jsonify({"message": "Subject added", "subject": subject.to_dict()}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/subjects/<int:sid>", methods=["DELETE"])
def delete_subject(sid):
    subj = Subject.query.get_or_404(sid)
    StudySession.query.filter_by(subject_id=sid).delete()
    db.session.delete(subj)
    db.session.commit()
    return jsonify({"message": "Deleted"})


@app.route("/api/subjects/<int:sid>", methods=["PUT"])
def update_subject(sid):
    subj = Subject.query.get_or_404(sid)
    data = request.json
    if "completed_hours" in data:
        subj.completed_hours = float(data["completed_hours"])
    if "difficulty" in data:
        subj.difficulty = float(data["difficulty"])
    if "estimated_hours" in data:
        subj.estimated_hours = float(data["estimated_hours"])
    if "is_weak" in data:
        subj.is_weak = data["is_weak"]
    if "name" in data:
        subj.name = data["name"]
    if "subject_type" in data:
        subj.subject_type = data["subject_type"]
    if "deadline" in data:
        subj.deadline = data["deadline"]
    if "color" in data:
        subj.color = data["color"]
    if "schedule_slots" in data:
        subj.schedule_slots = json.dumps(data["schedule_slots"])
    db.session.commit()
    return jsonify(subj.to_dict())


@app.route("/api/subjects/<int:sid>/weak", methods=["PUT"])
def toggle_weak(sid):
    subj = Subject.query.get_or_404(sid)
    subj.is_weak = not subj.is_weak
    db.session.commit()
    return jsonify({"is_weak": subj.is_weak})


@app.route("/api/subjects/<int:sid>/color", methods=["PUT"])
def update_color(sid):
    subj = Subject.query.get_or_404(sid)
    data = request.json
    subj.color = data.get("color", "#4f46e5")
    db.session.commit()
    return jsonify({"color": subj.color})


@app.route("/api/sessions", methods=["POST"])
def log_session():
    try:
        data = request.json
        subj = Subject.query.get_or_404(data.get("subject_id"))
        hours = float(data.get("actual_hours", 0))
        
        subj.completed_hours = min(subj.estimated_hours, subj.completed_hours + hours)
        
        cognitive_load = (hours / max(subj.estimated_hours, 1)) * subj.difficulty
        
        session = StudySession(
            subject_id=subj.id,
            actual_hours=hours,
            notes=data.get("notes", ""),
            cognitive_load=cognitive_load,
            date_studied=date.today().isoformat(),
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow() + timedelta(hours=hours)
        )
        db.session.add(session)
        db.session.commit()
        
        return jsonify({
            "message": "Session logged", 
            "cognitive_load": round(cognitive_load, 2),
            "new_progress": round((subj.completed_hours / subj.estimated_hours) * 100, 1) if subj.estimated_hours > 0 else 0
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/sessions", methods=["GET"])
def get_sessions():
    sessions = StudySession.query.order_by(StudySession.date_studied.desc()).limit(50).all()
    return jsonify([{
        "id": s.id,
        "subject_id": s.subject_id,
        "actual_hours": s.actual_hours,
        "date_studied": s.date_studied,
        "notes": s.notes,
        "start_time": s.start_time.isoformat() if s.start_time else None
    } for s in sessions])


@app.route("/api/ai-schedule", methods=["POST"])
def generate_schedule():
    data = request.json
    subjects = [s.to_dict() for s in Subject.query.all()]
    
    events = []
    today = date.today()
    
    for subj in subjects:
        slots = subj.get("schedule_slots", [])
        if slots:
            for slot in slots:
                for day in slot.get("days", []):
                    day_map = {"monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3, "friday": 4, "saturday": 5, "sunday": 6}
                    day_idx = day_map.get(day, 0)
                    event_date = today + timedelta(days=(day_idx - today.weekday() + 7) % 7)
                    start_dt = datetime.combine(event_date, datetime.strptime(slot["startTime"], "%H:%M").time())
                    end_dt = datetime.combine(event_date, datetime.strptime(slot["endTime"], "%H:%M").time())
                    events.append({
                        "id": f"{subj['id']}_{day}",
                        "title": subj['name'],
                        "start": start_dt.isoformat(),
                        "end": end_dt.isoformat(),
                        "color": subj.get("color", "#4f46e5"),
                    })
    
    if not events:
        for i, subj in enumerate(subjects[:4]):
            start_dt = datetime.now().replace(hour=9+i*2, minute=0, second=0, microsecond=0)
            end_dt = start_dt + timedelta(hours=2)
            events.append({
                "id": f"demo_{i}",
                "title": subj['name'],
                "start": start_dt.isoformat(),
                "end": end_dt.isoformat(),
                "color": subj.get("color", "#4f46e5"),
            })
    
    return jsonify({"schedule": events, "duration_type": data.get("duration_type", "weekly")})


@app.route("/api/analytics", methods=["GET"])
def get_analytics():
    subjects = Subject.query.all()
    sessions = StudySession.query.all()
    
    heatmap_dict = {}
    for s in sessions:
        if s.date_studied:
            if s.date_studied in heatmap_dict:
                heatmap_dict[s.date_studied] += s.actual_hours
            else:
                heatmap_dict[s.date_studied] = s.actual_hours
    
    heatmap = [{"date": k, "hours": round(v, 1)} for k, v in heatmap_dict.items()]
    
    total_hours = round(sum(s.actual_hours for s in sessions), 1)
    total_sessions = len(sessions)
    
    subject_analytics = []
    for s in subjects:
        progress_pct = round((s.completed_hours / max(s.estimated_hours, 1)) * 100, 1)
        subject_analytics.append({
            "id": s.id,
            "name": s.name,
            "completion_probability": predict_completion_probability(s),
            "progress": s.completed_hours / max(s.estimated_hours, 1),
            "progress_percent": progress_pct,
            "completed_hours": s.completed_hours,
            "estimated_hours": s.estimated_hours,
            "difficulty": s.difficulty,
            "type": s.subject_type,
            "days_left": s.days_left(),
        })
    
    burnout = get_burnout_status()
    
    return jsonify({
        "heatmap": heatmap,
        "subjects": subject_analytics,
        "burnout": burnout,
        "total_subjects": len(subjects),
        "total_sessions": total_sessions,
        "total_hours": total_hours,
    })


@app.route("/api/export/json", methods=["GET"])
def export_json():
    data = {
        "subjects": [s.to_dict() for s in Subject.query.all()],
        "sessions": [{
            "id": s.id,
            "subject_id": s.subject_id,
            "actual_hours": s.actual_hours,
            "date_studied": s.date_studied,
            "notes": s.notes
        } for s in StudySession.query.all()],
        "export_date": date.today().isoformat(),
        "total_study_hours": round(sum(s.actual_hours for s in StudySession.query.all()), 1),
        "total_sessions": StudySession.query.count()
    }
    return jsonify(data)


@app.route("/api/leetcode", methods=["GET"])
def get_leetcode():
    topic = request.args.get("topic", "").lower()
    problems = {
        "easy": [
            {"title": "Two Sum", "url": "https://leetcode.com/problems/two-sum/"},
            {"title": "Valid Parentheses", "url": "https://leetcode.com/problems/valid-parentheses/"},
            {"title": "Merge Two Sorted Lists", "url": "https://leetcode.com/problems/merge-two-sorted-lists/"},
            {"title": "Maximum Subarray", "url": "https://leetcode.com/problems/maximum-subarray/"},
            {"title": "Contains Duplicate", "url": "https://leetcode.com/problems/contains-duplicate/"}
        ],
        "medium": [
            {"title": "Add Two Numbers", "url": "https://leetcode.com/problems/add-two-numbers/"},
            {"title": "Longest Substring", "url": "https://leetcode.com/problems/longest-substring-without-repeating-characters/"},
            {"title": "3Sum", "url": "https://leetcode.com/problems/3sum/"},
            {"title": "Group Anagrams", "url": "https://leetcode.com/problems/group-anagrams/"},
            {"title": "Container With Most Water", "url": "https://leetcode.com/problems/container-with-most-water/"}
        ],
        "hard": [
            {"title": "Median of Two Arrays", "url": "https://leetcode.com/problems/median-of-two-sorted-arrays/"},
            {"title": "Merge k Sorted Lists", "url": "https://leetcode.com/problems/merge-k-sorted-lists/"},
            {"title": "Trapping Rain Water", "url": "https://leetcode.com/problems/trapping-rain-water/"},
            {"title": "Serialize Binary Tree", "url": "https://leetcode.com/problems/serialize-and-deserialize-binary-tree/"}
        ]
    }
    
    if topic and topic != "default":
        filtered = {"easy": [], "medium": [], "hard": []}
        for level in ["easy", "medium", "hard"]:
            filtered[level] = [p for p in problems[level] if topic in p["title"].lower()]
        if any(filtered[level] for level in ["easy", "medium", "hard"]):
            return jsonify(filtered)
    
    return jsonify(problems)


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    query = data.get("query", "").lower()
    
    responses = {
        "array": "📊 **Array**: A collection of elements stored at contiguous memory locations. Access: O(1), Search: O(n). Example: `int[] arr = {1,2,3,4,5}`",
        "linked list": "🔗 **Linked List**: Linear data structure where elements (nodes) point to the next node. Types: Singly, Doubly, Circular. Insertion O(1) at head.",
        "stack": "📚 **Stack**: LIFO (Last In First Out) data structure. Operations: Push, Pop, Peek. Used in recursion, undo operations. Time O(1).",
        "queue": "⏳ **Queue**: FIFO (First In First Out) data structure. Operations: Enqueue, Dequeue. Used in BFS, task scheduling. Time O(1).",
        "tree": "🌳 **Binary Tree**: Hierarchical structure with at most 2 children per node. BST has left < parent < right. Search O(log n) if balanced.",
        "graph": "📈 **Graph**: Non-linear structure with vertices and edges. Algorithms: BFS, DFS, Dijkstra's, Kruskal's. Used in social networks, maps.",
        "dp": "🎯 **Dynamic Programming**: Optimizes recursion by storing subproblem results. Key: overlapping subproblems, optimal substructure.",
        "python": "🐍 **Python**: Great for beginners! Learn: variables, loops, functions, lists, dictionaries, OOP.",
        "java": "☕ **Java**: Object-oriented, platform independent. Learn: OOP concepts, collections, multithreading.",
        "javascript": "💛 **JavaScript**: ES6 features (arrow functions, destructuring, spread). Learn async/await, promises.",
        "study tip": "📚 **Study Tips**: 1. Pomodoro (25 min study, 5 min break). 2. Active recall. 3. Spaced repetition.",
        "exam": "📝 **Exam Prep**: Start 2 weeks early, practice past papers, create summary notes, sleep 7-8 hours.",
        "hello": "👋 Hello! I'm NeuroStudy AI. Ask me about DSA, programming, study tips, or exam preparation!",
        "hi": "👋 Hi there! How can I help you study today?",
        "thank": "🎓 You're welcome! Keep studying hard and smart!",
        "who are you": "🧠 I'm NeuroStudy AI, your intelligent study assistant powered by AI. Ask me anything!"
    }
    
    response = None
    for key, val in responses.items():
        if key in query:
            response = val
            break
    
    if not response:
        response = "📚 I'm NeuroStudy AI! Ask me about:\n• Data Structures (Arrays, Linked Lists, Trees, Graphs)\n• Algorithms (Sorting, DP, BFS, DFS)\n• Programming (Python, Java, JavaScript)\n• Study Tips & Exam Preparation\n\nWhat would you like to learn?"
    
    return jsonify({"response": response})


# ============================================================
# AI Model Instances
# ============================================================
exam_predictor = ExamScorePredictor()
time_optimizer = TimeOptimizer()
quiz_generator = QuizGenerator()
burnout_predictor = BurnoutPredictor()


# ============================================================
# NEW AI ROUTES
# ============================================================

@app.route("/api/ai/exam-predict", methods=["GET"])
def predict_exam_scores():
    subjects_list = Subject.query.all()
    sessions = StudySession.query.all()
    
    sessions_by_subject = {}
    for s in sessions:
        if s.subject_id not in sessions_by_subject:
            sessions_by_subject[s.subject_id] = []
        sessions_by_subject[s.subject_id].append({
            'date_studied': s.date_studied,
            'cognitive_load': s.cognitive_load,
            'actual_hours': s.actual_hours
        })
    
    subjects_data = []
    for subj in subjects_list:
        subjects_data.append({
            'id': subj.id,
            'name': subj.name,
            'difficulty': subj.difficulty,
            'completed_hours': subj.completed_hours,
            'estimated_hours': subj.estimated_hours,
            'days_left': subj.days_left(),
            'sessions': sessions_by_subject.get(subj.id, [])
        })
    
    predictions = exam_predictor.predict_all_subjects(subjects_data)
    return jsonify(predictions)


@app.route("/api/ai/time-optimize", methods=["GET"])
def get_time_recommendations():
    subjects_list = Subject.query.all()
    subjects_data = [{'id': s.id, 'name': s.name, 'type': s.subject_type} for s in subjects_list]
    
    recommendations = time_optimizer.get_all_recommendations(subjects_data)
    return jsonify(recommendations)


@app.route("/api/ai/generate-quiz", methods=["POST"])
def generate_quiz():
    data = request.json
    subject_id = data.get('subject_id')
    num_questions = data.get('num_questions', 3)
    
    subject = Subject.query.get_or_404(subject_id)
    questions = quiz_generator.generate_questions(subject.name, subject.subject_type, num_questions)
    
    return jsonify({
        'subject_id': subject.id,
        'subject_name': subject.name,
        'questions': questions
    })


@app.route("/api/ai/generate-quiz-all", methods=["GET"])
def generate_quiz_all():
    weak_subjects = Subject.query.filter_by(is_weak=True).all()
    if not weak_subjects:
        weak_subjects = Subject.query.limit(3).all()
    
    subjects_data = [{'id': s.id, 'name': s.name, 'type': s.subject_type} for s in weak_subjects]
    all_questions = quiz_generator.generate_quiz_for_multiple_subjects(subjects_data, 2)
    
    return jsonify({
        'total_questions': len(all_questions),
        'questions': all_questions
    })


@app.route("/api/ai/burnout-predict", methods=["GET"])
def predict_burnout():
    fourteen_days_ago = (datetime.utcnow() - timedelta(days=14)).strftime("%Y-%m-%d")
    sessions = StudySession.query.filter(
        StudySession.date_studied >= fourteen_days_ago
    ).all()
    
    session_data = []
    daily_hours = {}
    cognitive_loads = []
    
    for s in sessions:
        session_data.append({
            'date_studied': s.date_studied,
            'cognitive_load': s.cognitive_load,
            'actual_hours': s.actual_hours,
            'start_time': s.start_time.isoformat() if s.start_time else None
        })
        
        if s.date_studied:
            daily_hours[s.date_studied] = daily_hours.get(s.date_studied, 0) + s.actual_hours
        if s.cognitive_load > 0:
            cognitive_loads.append(s.cognitive_load)
    
    study_hours_per_day = list(daily_hours.values())
    
    risk_score, risk_level, recommendation = burnout_predictor.predict_burnout_risk(
        session_data, cognitive_loads, study_hours_per_day
    )
    
    recovery_plan = burnout_predictor.get_recovery_plan(risk_level)
    weekly_prediction = burnout_predictor.predict_for_week(study_hours_per_day[-7:] if len(study_hours_per_day) >= 7 else study_hours_per_day)
    
    today = date.today().isoformat()
    today_hours = daily_hours.get(today, 0)
    consecutive_days = burnout_predictor._get_consecutive_study_days(session_data)
    daily_alert = burnout_predictor.get_daily_alert(today_hours, consecutive_days)
    
    return jsonify({
        'risk_score': risk_score,
        'risk_level': risk_level,
        'recommendation': recommendation,
        'recovery_plan': recovery_plan,
        'weekly_prediction': weekly_prediction,
        'daily_alert': daily_alert,
        'total_hours_last_14_days': sum(study_hours_per_day),
        'avg_daily_hours': round(sum(study_hours_per_day) / max(len(study_hours_per_day), 1), 1)
    })


@app.route("/api/ai/study-plan", methods=["POST"])
def get_ai_study_plan():
    data = request.json
    target_score = data.get('target_score', 85)
    
    subjects_list = Subject.query.all()
    sessions = StudySession.query.all()
    
    sessions_by_subject = {}
    for s in sessions:
        if s.subject_id not in sessions_by_subject:
            sessions_by_subject[s.subject_id] = []
        sessions_by_subject[s.subject_id].append({
            'date_studied': s.date_studied,
            'cognitive_load': s.cognitive_load,
            'actual_hours': s.actual_hours
        })
    
    subjects_data = []
    for subj in subjects_list:
        pred, _ = exam_predictor.predict_score({
            'id': subj.id,
            'name': subj.name,
            'difficulty': subj.difficulty,
            'completed_hours': subj.completed_hours,
            'days_left': subj.days_left()
        }, sessions_by_subject.get(subj.id, []))
        
        opt_time = time_optimizer.get_optimal_time(subj.subject_type)
        
        subjects_data.append({
            'id': subj.id,
            'name': subj.name,
            'predicted_score': pred,
            'optimal_time': opt_time,
            'difficulty': subj.difficulty,
            'progress': round((subj.completed_hours / max(subj.estimated_hours, 1)) * 100, 1),
            'priority': 'high' if subj.days_left() < 7 else 'medium' if subj.days_left() < 14 else 'low'
        })
    
    subjects_data.sort(key=lambda x: (x['priority'] == 'high', -x['predicted_score']))
    
    return jsonify({
        'subjects': subjects_data,
        'total_subjects': len(subjects_data),
        'avg_predicted_score': round(sum(s['predicted_score'] for s in subjects_data) / max(len(subjects_data), 1), 1),
        'recommendation': "Focus on subjects with 'high' priority first. Study during optimal times for better retention."
    })


# ============================================================
# Initialize Database with Example Subject
# ============================================================
def init_db():
    with app.app_context():
        db.create_all()
        
        if Subject.query.count() == 0:
            example = Subject(
                name="Data Structures & Algorithms",
                difficulty=8,
                subject_type="coding",
                deadline=(date.today() + timedelta(days=30)).isoformat(),
                estimated_hours=40,
                color="#4f46e5",
                schedule_slots=json.dumps([
                    {"days": ["monday", "wednesday", "friday"], "startTime": "14:00", "endTime": "16:00"}
                ])
            )
            db.session.add(example)
            db.session.commit()
            print("✅ Added example subject: Data Structures & Algorithms")
        
        print("✅ Database initialized")
        print(f"📊 Current subjects: {Subject.query.count()}")
        print(f"📈 Total study sessions: {StudySession.query.count()}")


if __name__ == "__main__":
    init_db()
    print("🚀 Starting NeuroStudy AI at http://localhost:5000")
    app.run(debug=True, host="0.0.0.0", port=5000)