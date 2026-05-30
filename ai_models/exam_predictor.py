"""
AI Exam Score Predictor
Uses Linear Regression to predict exam scores based on study patterns
"""

import math
import random
from datetime import datetime, timedelta

class ExamScorePredictor:
    """Predicts exam scores using multi-factor regression model"""
    
    def __init__(self):
        self.model_weights = {
            'study_hours': 0.4,
            'difficulty': -0.25,
            'consistency': 0.2,
            'days_before_exam': 0.1,
            'cognitive_load': -0.05
        }
    
    def predict_score(self, subject, study_sessions):
        """
        Predict exam score based on subject data and study history
        
        Formula: Score = 50 + (study_hours * 2) - (difficulty * 3) + (consistency * 10) + (days_factor)
        """
        if not subject:
            return 0, "No data available"
        
        # Base score
        base_score = 50
        
        # Factor 1: Study hours (each hour adds ~2 points, max 40)
        study_hours = subject.get('completed_hours', 0)
        hours_factor = min(40, study_hours * 2)
        
        # Factor 2: Difficulty penalty (higher difficulty = lower score)
        difficulty = subject.get('difficulty', 5)
        difficulty_penalty = (difficulty - 1) * 2.5  # Max 22.5 penalty
        
        # Factor 3: Consistency (regular study vs cramming)
        consistency = self._calculate_consistency(study_sessions)
        consistency_bonus = consistency * 15  # Max 15 points
        
        # Factor 4: Days before exam factor
        days_left = subject.get('days_left', 30)
        if days_left < 999:
            if days_left < 3:
                days_factor = -15  # Cramming penalty
            elif days_left < 7:
                days_factor = -5
            elif days_left < 14:
                days_factor = 5
            else:
                days_factor = 10
        else:
            days_factor = 0
        
        # Factor 5: Cognitive load penalty
        cognitive_load = self._get_avg_cognitive_load(study_sessions)
        cognitive_penalty = cognitive_load * 2
        
        # Calculate final score
        predicted_score = base_score + hours_factor - difficulty_penalty + consistency_bonus + days_factor - cognitive_penalty
        
        # Ensure score is between 0 and 100
        predicted_score = max(0, min(100, predicted_score))
        
        # Generate recommendation
        recommendation = self._generate_recommendation(predicted_score, study_hours, difficulty, days_left)
        
        return round(predicted_score, 1), recommendation
    
    def _calculate_consistency(self, sessions):
        """Calculate study consistency score (0-1)"""
        if not sessions or len(sessions) < 2:
            return 0.3  # Default low consistency
        
        # Check if sessions are spread out vs crammed
        dates = []
        for s in sessions:
            if s.get('date_studied'):
                try:
                    dates.append(datetime.strptime(s['date_studied'], "%Y-%m-%d"))
                except:
                    pass
        
        if len(dates) < 2:
            return 0.3
        
        # Calculate average gap between study days
        dates.sort()
        gaps = []
        for i in range(1, len(dates)):
            gap = (dates[i] - dates[i-1]).days
            gaps.append(gap)
        
        avg_gap = sum(gaps) / len(gaps)
        
        # Optimal gap is 1-2 days
        if 1 <= avg_gap <= 2:
            return 1.0
        elif avg_gap <= 1:
            return 0.7  # Studying too frequently (might be cramming)
        elif avg_gap <= 4:
            return 0.8
        elif avg_gap <= 7:
            return 0.5
        else:
            return 0.2
    
    def _get_avg_cognitive_load(self, sessions):
        """Calculate average cognitive load from sessions"""
        if not sessions:
            return 0
        loads = [s.get('cognitive_load', 0) for s in sessions if s.get('cognitive_load', 0) > 0]
        if not loads:
            return 0
        return sum(loads) / len(loads)
    
    def _generate_recommendation(self, score, hours, difficulty, days_left):
        """Generate personalized study recommendation"""
        if score >= 85:
            return "🎉 Excellent! You're well prepared. Focus on revision and practice tests."
        elif score >= 70:
            remaining_needed = (85 - score) / 2
            return f"📚 Good progress! Study {int(remaining_needed)} more hours to reach 85%."
        elif score >= 50:
            remaining_needed = (85 - score) / 1.5
            return f"⚠️ You need more preparation. Study {int(remaining_needed)} additional hours spread over {max(3, days_left//2)} days."
        else:
            return f"🔴 Critical: Start studying immediately! Focus on {int(difficulty)} hours daily for the next {min(7, days_left)} days."
    
    def predict_all_subjects(self, subjects_data):
        """Predict scores for all subjects"""
        predictions = []
        for subj in subjects_data:
            pred, rec = self.predict_score(subj, subj.get('sessions', []))
            predictions.append({
                'subject_id': subj.get('id'),
                'subject_name': subj.get('name'),
                'predicted_score': pred,
                'recommendation': rec,
                'risk_level': 'high' if pred < 50 else 'medium' if pred < 70 else 'low'
            })
        return predictions
    
    def get_study_plan_to_target(self, current_score, target_score, days_left, difficulty):
        """Calculate hours needed to reach target score"""
        if current_score >= target_score:
            return 0, "You've already reached your target!"
        
        points_needed = target_score - current_score
        # Each hour adds approximately 1.5-2 points
        hours_needed = int(points_needed / 1.8)
        
        # Adjust for difficulty
        hours_needed = int(hours_needed * (1 + (difficulty - 5) / 10))
        
        # Distribute across days
        hours_per_day = max(1, hours_needed // max(1, days_left))
        
        return hours_needed, f"Study {hours_per_day} hours per day for {days_left} days"