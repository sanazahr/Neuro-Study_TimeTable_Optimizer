"""
NeuroStudy AI Chatbot - Intelligent Study Assistant
Supports: General queries, math problems, study advice, schedule optimization
"""

import re
import math
import random
import requests
from datetime import datetime

class NeuroChatbot:
    """AI-powered chatbot for study-related queries"""
    
    def __init__(self):
        self.context = []
        self.study_topics = {
            "programming": ["python", "java", "javascript", "c++", "algorithm", "data structure", "coding"],
            "mathematics": ["math", "calculus", "algebra", "trigonometry", "geometry", "statistics"],
            "science": ["physics", "chemistry", "biology", "science"],
            "study_tips": ["study", "learn", "memory", "focus", "concentration", "productivity"],
            "exam_prep": ["exam", "test", "quiz", "final", "midterm"],
            "time_management": ["time", "schedule", "plan", "organize", "deadline"]
        }
        
    def process_query(self, query: str, user_data: dict = None) -> dict:
        """Process user query and return AI response"""
        query_lower = query.lower().strip()
        
        # Check for math problems
        math_result = self._solve_math(query_lower)
        if math_result:
            return {
                "response": math_result,
                "type": "math",
                "confidence": 0.95
            }
        
        # Check for study advice
        if self._detect_intent(query_lower, "study_tips"):
            return {
                "response": self._get_study_tip(),
                "type": "study_advice",
                "confidence": 0.85
            }
        
        # Check for exam preparation
        if self._detect_intent(query_lower, "exam_prep"):
            return {
                "response": self._get_exam_tip(),
                "type": "exam_advice",
                "confidence": 0.85
            }
        
        # Check for time management
        if self._detect_intent(query_lower, "time_management"):
            return {
                "response": self._get_time_management_tip(),
                "type": "time_advice",
                "confidence": 0.85
            }
        
        # Check for programming help
        if self._detect_intent(query_lower, "programming"):
            return {
                "response": self._get_programming_help(query_lower),
                "type": "coding",
                "confidence": 0.80
            }
        
        # General response
        return {
            "response": self._get_general_response(query_lower, user_data),
            "type": "general",
            "confidence": 0.70
        }
    
    def _detect_intent(self, text: str, category: str) -> bool:
        """Detect user intent based on keywords"""
        keywords = self.study_topics.get(category, [])
        return any(keyword in text for keyword in keywords)
    
    def _solve_math(self, text: str) -> str:
        """Solve basic math problems from text"""
        # Extract numbers and operators
        patterns = [
            (r'(\d+)\s*\+\s*(\d+)', lambda m: int(m[0]) + int(m[1])),
            (r'(\d+)\s*-\s*(\d+)', lambda m: int(m[0]) - int(m[1])),
            (r'(\d+)\s*\*\s*(\d+)', lambda m: int(m[0]) * int(m[1])),
            (r'(\d+)\s*/\s*(\d+)', lambda m: int(m[0]) / int(m[1])),
            (r'(\d+)\s*\^\s*(\d+)', lambda m: int(m[0]) ** int(m[1])),
            (r'sqrt\s*\(\s*(\d+)\s*\)', lambda m: math.sqrt(int(m[0]))),
        ]
        
        for pattern, func in patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    result = func(match.groups())
                    return f"🧮 The answer is: {result}"
                except:
                    pass
        
        # Check for percentage
        percent_match = re.search(r'(\d+)\s*percent\s+of\s+(\d+)', text)
        if percent_match:
            pct = int(percent_match.group(1))
            num = int(percent_match.group(2))
            result = (pct / 100) * num
            return f"📊 {pct}% of {num} is {result}"
        
        return None
    
    def _get_study_tip(self) -> str:
        """Return random study tip"""
        tips = [
            "📚 The Pomodoro Technique: Study for 25 minutes, then take a 5-minute break. Repeat 4 times, then take a longer break.",
            "🎯 Active recall is more effective than passive reading. Test yourself regularly!",
            "📝 Summarize what you learn in your own words. Teaching others is the best way to master a topic.",
            "🌙 Sleep is crucial for memory consolidation. Aim for 7-8 hours after intense study sessions.",
            "🎧 Find your focus zone. Some people study better with music, others in silence. Experiment to find what works for you.",
            "📅 Plan your week every Sunday. Knowing what's ahead reduces anxiety and improves productivity.",
            "💪 Start with the hardest subject when your energy is highest (usually morning).",
            "🏆 Set specific, measurable goals. 'Study math for 2 hours' is better than 'study math'."
        ]
        return random.choice(tips)
    
    def _get_exam_tip(self) -> str:
        """Return exam preparation tip"""
        tips = [
            "📝 Start preparing at least 2 weeks before the exam. Cramming leads to poor retention.",
            "📊 Practice with past papers. Understanding the exam format reduces anxiety.",
            "🎯 Focus on weak areas first. Spend 80% of your time on topics you struggle with.",
            "🧠 Use spaced repetition: Review material after 1 day, 3 days, 1 week, and 2 weeks.",
            "💧 Stay hydrated and eat brain foods like nuts, berries, and dark chocolate before exams.",
            "😴 Get a full night's sleep before the exam. Sleep deprivation reduces cognitive function by 30%.",
            "📋 Make a cheat sheet (even if you can't use it). The act of condensing information helps memory.",
            "🧘 Practice deep breathing before the exam to reduce anxiety."
        ]
        return random.choice(tips)
    
    def _get_time_management_tip(self) -> str:
        """Return time management tip"""
        tips = [
            "⏰ Use the Eisenhower Matrix: Urgent & Important (Do first), Important but not urgent (Schedule), Urgent but not important (Delegate), Neither (Eliminate).",
            "📅 Time blocking: Assign specific time slots for each subject. Protect these blocks like appointments.",
            "🎯 The 80/20 rule: 20% of your efforts produce 80% of results. Identify what's most important.",
            "🚫 Avoid multitasking. It reduces productivity by up to 40%.",
            "✅ Make a daily to-do list with only 3 priority tasks. Complete these before anything else.",
            "⏲️ Set time limits for each task. Parkinson's Law: Work expands to fill the time available."
        ]
        return random.choice(tips)
    
    def _get_programming_help(self, query: str) -> str:
        """Provide programming help"""
        if "python" in query or "code" in query:
            return "💻 Python tip: Use list comprehensions for cleaner code: `[x*2 for x in range(10)]` instead of loops for simple transformations."
        elif "algorithm" in query:
            return "🔄 Algorithm advice: Start with a brute force solution, then optimize. Big O notation helps compare efficiency."
        elif "debug" in query:
            return "🐛 Debugging tip: Print intermediate values, use a debugger, and explain your code to someone (or a rubber duck!)."
        elif "error" in query:
            return "⚠️ Read error messages carefully. They tell you exactly what's wrong and where. Google the exact error text."
        else:
            return "💡 Programming mantra: 'Make it work, make it right, make it fast' - in that order. Don't optimize prematurely."
    
    def _get_general_response(self, query: str, user_data: dict = None) -> str:
        """General response for unclassified queries"""
        greetings = ["hello", "hi", "hey", "greetings"]
        thanks = ["thank", "thanks", "appreciate"]
        
        if any(g in query for g in greetings):
            return "👋 Hello! I'm your AI Study Assistant. Ask me about study tips, math problems, time management, or exam preparation!"
        
        if any(t in query for t in thanks):
            return "🎓 You're welcome! Keep studying hard and smart. I'm here if you need anything else!"
        
        if "who are you" in query or "what are you" in query:
            return "🤖 I'm NeuroStudy AI, your intelligent study assistant. I can help with math problems, study tips, time management, and exam preparation."
        
        if "how are you" in query:
            return "🧠 I'm fully charged and ready to help you study! How can I assist you today?"
        
        # Default response
        return "📚 I'm here to help with your studies! You can ask me about: math problems, study techniques, exam preparation, time management, or programming concepts. What would you like to know?"
    
    def generate_schedule_from_preferences(self, preferences: dict) -> dict:
        """Generate personalized schedule based on user preferences"""
        subjects = preferences.get('subjects', [])
        free_time = preferences.get('free_time', {})  # {'monday': ['9:00-11:00', '14:00-16:00'], ...}
        weak_subjects = preferences.get('weak_subjects', [])
        study_duration = preferences.get('study_duration', 2)  # hours per day
        
        schedule = []
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        
        for day in days:
            day_schedule = {'day': day, 'blocks': []}
            free_slots = free_time.get(day, [])
            current_time_index = 0
            
            for subject in subjects:
                if current_time_index < len(free_slots):
                    time_slot = free_slots[current_time_index]
                    # Determine if this is a weak subject (needs more attention)
                    is_weak = subject['name'] in weak_subjects
                    duration = study_duration + (1 if is_weak else 0)
                    
                    day_schedule['blocks'].append({
                        'subject': subject['name'],
                        'time': time_slot,
                        'duration': duration,
                        'is_weak': is_weak,
                        'type': subject.get('type', 'theory')
                    })
                    current_time_index += 1
            
            if day_schedule['blocks']:
                schedule.append(day_schedule)
        
        return {
            'schedule': schedule,
            'message': f"✅ Generated personalized schedule for {len(schedule)} days. Weak subjects ({', '.join(weak_subjects[:2])}) given extra time."
        }