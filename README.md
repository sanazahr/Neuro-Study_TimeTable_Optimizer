# 🧠 AI Study Planner — Intelligent Timetable Optimizer

**AI Course Project** | Demonstrates: A* Search, DAG Knowledge Graphs, CSP, Adaptive RL, NLP, Predictive Analytics

---

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Initialize DB with sample data (optional)
python init_db.py

# 3. Run the application
python app.py
# → Open http://localhost:5000
```

---

## 📁 Project Structure

```
study_planner/
├── app.py                  # Flask backend + ALL AI algorithms
├── init_db.py              # Database seeder with sample data
├── requirements.txt
├── templates/
│   └── index.html          # Full SPA frontend (Tailwind + Chart.js + FullCalendar)
└── static/
    └── data/
        └── quotes.json     # 110 categorized motivational quotes
```

---

## 🤖 AI Techniques Implemented

### 1. A* Search Algorithm (`app.py: astar_study_schedule`)
- **State**: Tuple of remaining subject IDs
- **g(n)**: Cumulative hours scheduled so far
- **h(n)**: Σ(difficulty² / days_left) — admissible heuristic
- **f(n) = g(n) + h(n)**
- Uses `heapq` priority queue

### 2. Knowledge Graph / DAG (`app.py: build_prerequisite_graph`)
- Built with `networkx.DiGraph`
- Nodes: subjects with attributes (difficulty, type, deadline)
- Edges: prerequisite relationships
- **Weight = difficulty ^ 1.5**
- Visualized with `vis-network` in browser

### 3. Topological Sort — Kahn's Algorithm (`app.py: topological_sort_subjects`)
- BFS-based Kahn's algorithm on the prerequisite DAG
- Guarantees prerequisites are studied before dependent subjects
- Output shown in timetable view

### 4. CSP — Constraint Satisfaction (`app.py: csp_allocate_timetable`)
- Time slots: 30-min intervals, 8AM–10PM
- Constraints: Max 6h/day, break after 2h continuous, prerequisite order
- Backtracking calendar matrix allocation

### 5. Adaptive Learning — Reinforcement-inspired (`app.py: adaptive_difficulty_update`)
- Cognitive Load = (actual_time / estimated_time) × difficulty
- Difficulty updated via learning rate α=0.2 after each session

### 6. NLP Classification (`app.py: classify_subject_type`)
- Bag-of-words keyword matching
- Categories: coding / theory / math / project
- Applied automatically when adding subjects

### 7. Predictive Analytics (`app.py: predict_completion_probability`)
- Logistic sigmoid function on: pace ratio, progress, difficulty penalty
- Returns completion probability (0–1) per subject

### 8. Spaced Repetition (`app.py: get_spaced_repetition_queue`)
- BFS queue with intervals: 1, 3, 7, 15 days
- Alerts user when a subject is due for review

### 9. Burnout Protection (`app.py: get_burnout_status`)
- Rolling 7-day cognitive load average
- Levels: healthy / warning / critical

---

## 💬 Quotes System (110 quotes)

| Feature | Implementation |
|---------|---------------|
| 5 display locations | Dashboard, Sidebar, Timetable header, Post-session, Burnout popup |
| Smart selection | By category, mood, difficulty level, time of day |
| Quote of the Day | Date-seeded, localStorage persistent |
| Pin quotes | localStorage |
| Copy to clipboard | Browser Clipboard API |
| Filters | Category + Level + Mood + Time of Day |
| Progress milestones | After 1h, 3h, 5h study |

---

## 🎓 Data Structures Used

| Structure | Use |
|-----------|-----|
| `heapq` (Priority Queue) | A* open set |
| `networkx.DiGraph` | Prerequisite DAG |
| Dict/HashMap | O(1) subject lookup in A* |
| `deque` | Kahn's BFS, Spaced Repetition |
| 2D Matrix `calendar[day][slot]` | CSP time slot allocation |
| SQLite + SQLAlchemy | Persistent storage |

---

## 📊 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/subjects` | All subjects with AI predictions |
| POST | `/api/subjects` | Add subject (auto NLP classification) |
| DELETE | `/api/subjects/<id>` | Remove subject |
| POST | `/api/sessions` | Log study session (triggers adaptive update) |
| GET | `/api/schedule` | Generate A* + CSP timetable |
| GET | `/api/graph` | Knowledge graph data |
| POST | `/api/prerequisites` | Add prerequisite edge |
| GET | `/api/analytics` | Heatmap, burnout, spaced repetition |
| GET | `/api/leetcode?topic=` | Practice problems |
| GET | `/api/export/json` | Export full study plan |
| GET | `/api/quotes/smart` | Server-side smart quote selection |
