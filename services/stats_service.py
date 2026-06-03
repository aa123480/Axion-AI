#----------------------------------------------------------------------------------#
# Import Libraries 
#----------------------------------------------------------------------------------#

from fastapi import HTTPException
from models.schemas import Stats

#----------------------------------------------------------------------------------#
# Anaylze player stats and provide feedback
#----------------------------------------------------------------------------------#

def analyze_stats(stats: Stats):
    kills = stats.kills
    deaths = stats.deaths if stats.deaths > 0 else 1
    accuracy = stats.accuracy

    if kills < 0 or deaths < 0 or accuracy < 0 or accuracy > 100:
        raise HTTPException(status_code=400, detail="Invalid stats. Kills and deaths must be 0 or above. Accuracy must be between 0 and 100.")

    kd_ratio = kills / deaths
    score = (kd_ratio * 10) + (accuracy * 0.5)

    feedback = []

    if kd_ratio < 1:
        feedback.append("Your K/D is below 1. Focus on survival, spacing, and fewer isolated fights.")
    elif kd_ratio < 2:
        feedback.append("Your K/D is stable. Look for cleaner aggression when you have timing or utility advantage.")
    else:
        feedback.append("Your K/D is strong. Keep pressing advantages, but stay disciplined after opening picks.")

    if accuracy < 30:
        feedback.append("Accuracy is low. Prioritize crosshair placement, first-shot discipline, and short aim blocks.")
    elif accuracy < 60:
        feedback.append("Accuracy is serviceable. Consistency should improve with tighter pre-aiming and calmer engagements.")
    else:
        feedback.append("Accuracy is strong. Maintain that level and shift more attention to decision-making.")

    return {
        "kills": kills,
        "deaths": deaths,
        "accuracy": accuracy,
        "kd_ratio": round(kd_ratio, 2),
        "performance_score": round(score, 2),
        "coach_feedback": feedback,
    }