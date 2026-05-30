"""
AI Burnout Predictor
Predicts study burnout risk based on patterns and cognitive load
"""

from datetime import datetime, timedelta
import math

class BurnoutPredictor:
    """Predicts burnout risk using machine learning-inspired algorithms"""
    
    def __init__(self):
        self.burnout_thresholds = {
            'low': 30,
            'medium': 60,
            'high': 80,
            'critical': 100
        }
    
    def predict_burnout_risk(self, study_sessions, cognitive_loads, study_hours_per_day):
        """
        Calculate burnout risk percentage based on:
        - Consecutive study days
        - Daily study hours
        - Cognitive load trend
        - Sleep deficit (inferred)
        """
        # If no study sessions, return low risk with message
        if not study_sessions or len(study_hours_per_day) == 0:
            return 0, 'low', "✅ No study data yet. Start studying to get burnout insights!"
        
        risk_score = 0
        
        # Factor 1: Daily study hours (40% weight)
        avg_hours = sum(study_hours_per_day) / len(study_hours_per_day)
        if avg_hours > 6:
            risk_score += 40
        elif avg_hours > 4:
            risk_score += 25
        elif avg_hours > 3:
            risk_score += 15
        else:
            risk_score += 5
        
        # Factor 2: Consecutive study days (30% weight)
        consecutive_days = self._get_consecutive_study_days(study_sessions)
        if consecutive_days > 10:
            risk_score += 30
        elif consecutive_days > 7:
            risk_score += 22
        elif consecutive_days > 5:
            risk_score += 15
        elif consecutive_days > 3:
            risk_score += 8
        else:
            risk_score += 0
        
        # Factor 3: Cognitive load trend (20% weight)
        if cognitive_loads:
            avg_load = sum(cognitive_loads) / len(cognitive_loads)
            if avg_load > 8:
                risk_score += 20
            elif avg_load > 6:
                risk_score += 12
            elif avg_load > 4:
                risk_score += 6
            else:
                risk_score += 2
        
        # Factor 4: Late night study (10% weight)
        late_night_sessions = self._count_late_night_sessions(study_sessions)
        if late_night_sessions > 5:
            risk_score += 10
        elif late_night_sessions > 3:
            risk_score += 6
        elif late_night_sessions > 1:
            risk_score += 3
        
        # Ensure score is within 0-100
        risk_score = min(100, risk_score)
        
        # Determine risk level and generate recommendation
        risk_level, recommendation = self._get_risk_level_and_recommendation(risk_score, avg_hours, consecutive_days)
        
        return risk_score, risk_level, recommendation
    
    def _get_consecutive_study_days(self, sessions):
        """Calculate number of consecutive study days"""
        if not sessions:
            return 0
        
        dates = []
        for s in sessions:
            if s.get('date_studied'):
                try:
                    dates.append(datetime.strptime(s['date_studied'], "%Y-%m-%d").date())
                except:
                    pass
        
        if not dates:
            return 0
        
        unique_dates = sorted(set(dates))
        consecutive = 1
        max_consecutive = 1
        
        for i in range(1, len(unique_dates)):
            if (unique_dates[i] - unique_dates[i-1]).days == 1:
                consecutive += 1
                max_consecutive = max(max_consecutive, consecutive)
            else:
                consecutive = 1
        
        return max_consecutive
    
    def _count_late_night_sessions(self, sessions):
        """Count sessions that occur after 10 PM"""
        count = 0
        for s in sessions:
            if s.get('start_time'):
                try:
                    hour = datetime.fromisoformat(s['start_time']).hour
                    if hour >= 22 or hour <= 4:
                        count += 1
                except:
                    pass
        return count
    
    def _get_risk_level_and_recommendation(self, risk_score, avg_hours, consecutive_days):
        """Get risk level and recovery recommendation"""
        if risk_score >= 80:
            return 'critical', "🔴 **CRITICAL BURNOUT RISK!** Stop studying immediately. Take 2-3 full days off. Your health is most important."
        elif risk_score >= 60:
            return 'high', "⚠️ **HIGH BURNOUT RISK** - Take a complete rest day tomorrow. Reduce study hours to 2-3 hours max for the next 3 days."
        elif risk_score >= 35:
            return 'medium', "🟡 **MEDIUM BURNOUT RISK** - Take half-day breaks. Study in 25-minute Pomodoro sessions with 10-minute breaks."
        else:
            return 'low', "✅ **LOW BURNOUT RISK** - You're doing great! Maintain healthy study habits and take regular breaks."
    
    def get_recovery_plan(self, risk_level):
        """Generate recovery plan based on risk level"""
        plans = {
            'critical': {
                'action': "Stop all studying for 2-3 days",
                'rest': "Sleep 8-10 hours daily",
                'activity': "Light physical activity only",
                'return_plan': "Start with 1 hour daily for first week"
            },
            'high': {
                'action': "Take a full rest day tomorrow",
                'rest': "Sleep 7-8 hours",
                'activity': "Take walks outside",
                'return_plan': "Return with 2-3 hours daily"
            },
            'medium': {
                'action': "Take half-day breaks",
                'rest': "Maintain 7-8 hours sleep",
                'activity': "Take 15-min breaks every hour",
                'return_plan': "Continue with reduced load"
            },
            'low': {
                'action': "Maintain current schedule",
                'rest': "Keep regular sleep schedule",
                'activity': "Take regular breaks",
                'return_plan': "Stay consistent"
            }
        }
        return plans.get(risk_level, plans['low'])
    
    def predict_for_week(self, weekly_sessions):
        """Predict burnout risk for upcoming week based on patterns"""
        if not weekly_sessions or len(weekly_sessions) == 0:
            return "Not enough data for weekly prediction. Log more study sessions to get insights."
        
        avg_daily_hours = sum(weekly_sessions) / len(weekly_sessions)
        
        if avg_daily_hours > 5:
            return "⚠️ Warning: Your study load is high. Consider reducing to 3-4 hours daily next week."
        elif avg_daily_hours > 3:
            return "✅ Your study load is balanced. Maintain this pace."
        else:
            return "📚 You can increase study hours slightly if needed."
    
    def get_daily_alert(self, today_hours, consecutive_days):
        """Get daily burnout alert based on today's activity"""
        if today_hours > 6:
            return "🔴 STOP! You've studied too much today. Take a break and rest."
        elif today_hours > 4:
            return "🟡 You're studying a lot today. Take a 30-minute break now."
        elif today_hours > 2 and consecutive_days > 5:
            return "🟢 Good job! Remember to take breaks."
        else:
            return None