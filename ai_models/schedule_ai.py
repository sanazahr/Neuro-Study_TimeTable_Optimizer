"""
AI Schedule Optimizer - Intelligent timetable generation
Supports: Daily, Weekly, Monthly planning with user preferences
"""

from datetime import datetime, timedelta
import heapq
import random

class AIScheduleOptimizer:
    """AI-powered schedule generator with user preference integration"""
    
    def __init__(self):
        self.default_slots = [
            "08:00-10:00", "10:00-12:00", "12:00-14:00",
            "14:00-16:00", "16:00-18:00", "18:00-20:00", "20:00-22:00"
        ]
    
    def generate_schedule(self, subjects: list, preferences: dict, duration_type: str = 'weekly') -> dict:
        """
        Generate optimized schedule
        
        duration_type: 'daily', 'weekly', 'monthly'
        preferences: {free_time, weak_subjects, preferred_times, break_duration}
        """
        
        if duration_type == 'daily':
            return self._generate_daily_schedule(subjects, preferences)
        elif duration_type == 'weekly':
            return self._generate_weekly_schedule(subjects, preferences)
        elif duration_type == 'monthly':
            return self._generate_monthly_schedule(subjects, preferences)
        else:
            return self._generate_weekly_schedule(subjects, preferences)
    
    def _generate_daily_schedule(self, subjects: list, preferences: dict) -> dict:
        """Generate single day schedule"""
        free_time = preferences.get('free_time', {})
        today = datetime.now().strftime('%A').lower()
        free_slots = free_time.get(today, self.default_slots[:3])
        
        # Priority queue for subjects (urgent first)
        priority_queue = []
        for subj in subjects:
            urgency = (subj.get('difficulty', 5) ** 2) / max(subj.get('days_left', 7), 1)
            heapq.heappush(priority_queue, (-urgency, subj))
        
        blocks = []
        weak_subjects = preferences.get('weak_subjects', [])
        break_duration = preferences.get('break_duration', 15)  # minutes
        
        for i, slot in enumerate(free_slots):
            if priority_queue:
                _, subj = heapq.heappop(priority_queue)
                is_weak = subj['name'] in weak_subjects
                duration = 2 if is_weak else 1.5  # hours
                
                blocks.append({
                    'subject': subj['name'],
                    'time': slot,
                    'duration': duration,
                    'type': subj.get('type', 'theory'),
                    'difficulty': subj.get('difficulty', 5),
                    'is_weak': is_weak
                })
                
                # Add break between subjects
                if i < len(free_slots) - 1:
                    blocks.append({
                        'subject': 'BREAK',
                        'time': self._add_break_time(slot, duration),
                        'duration': break_duration / 60,
                        'type': 'break',
                        'is_break': True
                    })
        
        return {
            'schedule': blocks,
            'duration_type': 'daily',
            'generated_date': datetime.now().isoformat(),
            'total_hours': sum(b.get('duration', 0) for b in blocks if b.get('subject') != 'BREAK')
        }
    
    def _generate_weekly_schedule(self, subjects: list, preferences: dict) -> dict:
        """Generate weekly schedule (7 days)"""
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        free_time = preferences.get('free_time', {})
        weak_subjects = preferences.get('weak_subjects', [])
        
        weekly_schedule = []
        
        # Distribute subjects across days
        subjects_per_day = max(1, len(subjects) // 5)
        
        for day in days:
            day_slots = free_time.get(day, self.default_slots[:subjects_per_day])
            day_blocks = []
            
            # Select subjects for this day
            day_subjects = subjects[:subjects_per_day] if subjects else []
            subjects = subjects[subjects_per_day:] + subjects[:subjects_per_day]  # rotate
            
            for i, (slot, subj) in enumerate(zip(day_slots, day_subjects)):
                is_weak = subj['name'] in weak_subjects
                duration = 2 if is_weak else 1.5
                
                day_blocks.append({
                    'subject': subj['name'],
                    'time': slot,
                    'duration': duration,
                    'type': subj.get('type', 'theory'),
                    'difficulty': subj.get('difficulty', 5),
                    'is_weak': is_weak
                })
                
                # Add break
                if i < len(day_slots) - 1:
                    day_blocks.append({
                        'subject': 'BREAK',
                        'time': self._add_break_time(slot, duration),
                        'duration': 0.25,
                        'type': 'break',
                        'is_break': True
                    })
            
            if day_blocks:
                weekly_schedule.append({'day': day, 'blocks': day_blocks})
        
        return {
            'schedule': weekly_schedule,
            'duration_type': 'weekly',
            'generated_date': datetime.now().isoformat(),
            'total_days': len(weekly_schedule)
        }
    
    def _generate_monthly_schedule(self, subjects: list, preferences: dict) -> dict:
        """Generate monthly schedule (4 weeks)"""
        weekly = self._generate_weekly_schedule(subjects, preferences)
        
        monthly_schedule = []
        for week_num in range(1, 5):
            week_data = weekly['schedule'].copy()
            # Adjust for week number (add difficulty progression)
            for day in week_data:
                for block in day['blocks']:
                    if block.get('subject') != 'BREAK':
                        # Increase difficulty/complexity each week
                        block['week'] = week_num
                        if week_num > 2:
                            block['duration'] = block.get('duration', 1.5) + 0.25
            monthly_schedule.append({
                'week': week_num,
                'days': week_data,
                'week_start': (datetime.now() + timedelta(weeks=week_num-1)).isoformat()
            })
        
        return {
            'schedule': monthly_schedule,
            'duration_type': 'monthly',
            'generated_date': datetime.now().isoformat(),
            'total_weeks': 4
        }
    
    def _add_break_time(self, time_slot: str, duration_hours: float) -> str:
        """Calculate break time after a study block"""
        start_time = datetime.strptime(time_slot.split('-')[0], "%H:%M")
        end_time = start_time + timedelta(hours=duration_hours)
        return f"{end_time.strftime('%H:%M')}-{(end_time + timedelta(minutes=15)).strftime('%H:%M')}"
    
    def optimize_with_user_feedback(self, current_schedule: dict, feedback: str) -> dict:
        """Adjust schedule based on user feedback"""
        if "too much" in feedback.lower() or "heavy" in feedback.lower():
            # Reduce study hours
            for day in current_schedule.get('schedule', []):
                for block in day.get('blocks', []):
                    if block.get('duration', 0) > 1:
                        block['duration'] = max(1, block['duration'] - 0.5)
            current_schedule['adjustment'] = "Reduced study hours based on your feedback"
        
        elif "easy" in feedback.lower() or "more" in feedback.lower():
            # Increase challenge
            for day in current_schedule.get('schedule', []):
                for block in day.get('blocks', []):
                    block['duration'] = min(3, block.get('duration', 1.5) + 0.5)
            current_schedule['adjustment'] = "Increased study duration to challenge you more"
        
        return current_schedule