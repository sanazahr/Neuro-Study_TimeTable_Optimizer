"""
AI Smart Study Time Optimizer
Recommends optimal study times based on subject type and user performance
"""

from datetime import datetime
import random

class TimeOptimizer:
    """Recommends optimal study times using circadian rhythm patterns"""
    
    # Different optimal times for different subjects
    TIME_PREFERENCES = {
        'coding': {
            'best': ['09:00-11:00', '14:00-16:00'],
            'good': ['11:00-13:00', '16:00-18:00'],
            'avoid': ['20:00-23:00', '06:00-08:00']
        },
        'math': {
            'best': ['08:00-10:00', '15:00-17:00'],
            'good': ['10:00-12:00', '17:00-19:00'],
            'avoid': ['21:00-23:00', '05:00-07:00']
        },
        'theory': {
            'best': ['10:00-12:00', '19:00-21:00'],
            'good': ['08:00-10:00', '14:00-16:00', '21:00-23:00'],
            'avoid': ['05:00-07:00']
        },
        'project': {
            'best': ['13:00-15:00', '20:00-22:00'],
            'good': ['10:00-12:00', '15:00-17:00', '22:00-00:00'],
            'avoid': ['06:00-08:00']
        }
    }
    
    # Productivity multipliers by time of day
    PRODUCTIVITY_MULTIPLIERS = {
        'morning_early': (6, 8, 0.7),
        'morning_peak': (8, 12, 1.2),
        'afternoon_dip': (12, 14, 0.8),
        'afternoon_peak': (14, 17, 1.1),
        'evening': (17, 20, 1.0),
        'night': (20, 23, 0.9),
        'late_night': (23, 24, 0.6)
    }
    
    def get_optimal_time(self, subject_type, subject_name=""):
        """Get optimal study time recommendation - different for each subject"""
        prefs = self.TIME_PREFERENCES.get(subject_type, self.TIME_PREFERENCES['theory'])
        
        # Use subject name to create variation even within same type
        name_hash = sum(ord(c) for c in subject_name) % len(prefs['best'])
        best_time = prefs['best'][name_hash % len(prefs['best'])]
        
        # Convert to AM/PM format
        best_time_ampm = self._convert_to_ampm(best_time)
        
        return best_time_ampm
    
    def _convert_to_ampm(self, time_range):
        """Convert 24-hour time range to AM/PM format"""
        parts = time_range.split('-')
        start_hour = int(parts[0].split(':')[0])
        end_hour = int(parts[1].split(':')[0])
        
        def hour_to_ampm(hour):
            if hour == 0:
                return "12:00 AM"
            elif hour < 12:
                return f"{hour}:00 AM"
            elif hour == 12:
                return "12:00 PM"
            else:
                return f"{hour-12}:00 PM"
        
        return f"{hour_to_ampm(start_hour)} - {hour_to_ampm(end_hour)}"
    
    def get_productivity_boost(self, time_range):
        """Calculate productivity boost percentage"""
        try:
            hour = int(time_range.split(':')[0]) if ':' in time_range else 9
            for period, (start, end, multiplier) in self.PRODUCTIVITY_MULTIPLIERS.items():
                if start <= hour < end:
                    boost = int((multiplier - 1) * 100)
                    return f"+{boost}%" if boost > 0 else f"{boost}%"
            return "+0%"
        except:
            return "+10%"
    
    def get_all_recommendations(self, subjects):
        """Get time recommendations for all subjects - each gets different time"""
        recommendations = []
        used_times = set()
        
        for i, subj in enumerate(subjects):
            subj_type = subj.get('type', 'theory')
            prefs = self.TIME_PREFERENCES.get(subj_type, self.TIME_PREFERENCES['theory'])
            
            # Distribute different times across subjects
            available_times = prefs['best'][:]
            for ut in used_times:
                if ut in available_times:
                    available_times.remove(ut)
            
            if not available_times:
                available_times = prefs['best'][:]
            
            chosen_time = available_times[0] if available_times else prefs['best'][0]
            used_times.add(chosen_time)
            
            opt_time_ampm = self._convert_to_ampm(chosen_time)
            boost = self.get_productivity_boost(chosen_time.split('-')[0])
            
            recommendations.append({
                'subject_id': subj.get('id'),
                'subject_name': subj.get('name'),
                'subject_type': subj_type,
                'optimal_time': opt_time_ampm,
                'optimal_time_24h': chosen_time,
                'productivity_boost': boost,
                'reason': self._get_reason(subj_type)
            })
        
        return recommendations
    
    def _get_reason(self, subject_type):
        """Get explanation for time recommendation"""
        reasons = {
            'coding': "Morning hours are best for logical thinking and problem-solving",
            'math': "Early hours provide fresh mental energy for complex calculations",
            'theory': "Mid-day or evening works well for reading and memorization",
            'project': "Afternoon/evening allows for creative and extended work sessions"
        }
        return reasons.get(subject_type, "This time maximizes your focus and retention")