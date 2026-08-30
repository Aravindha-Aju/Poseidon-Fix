from datetime import datetime
from typing import List, Dict, Any
import math

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat, dlon = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

def analyze_vessel_behavior(trajectory: List[Dict[str, Any]], source_time: datetime, source_location: Dict[str, float]) -> Dict[str, Any]:
    if len(trajectory) < 2: return {"error": "Insufficient data"}
    
    points_near = [(i, p, abs((datetime.fromisoformat(p["time"].replace("Z", "+00:00")) - source_time).total_seconds() / 3600)) for i, p in enumerate(trajectory) if abs((datetime.fromisoformat(p["time"].replace("Z", "+00:00")) - source_time).total_seconds() / 3600) <= 2.0]
    if not points_near: return {"error": "No points near source time"}
    
    speeds = []
    for i in range(1, len(trajectory)):
        t1, t2 = datetime.fromisoformat(trajectory[i-1]["time"].replace("Z", "+00:00")), datetime.fromisoformat(trajectory[i]["time"].replace("Z", "+00:00"))
        hrs = (t2 - t1).total_seconds() / 3600
        if hrs > 0: speeds.append(haversine(trajectory[i-1]["lat"], trajectory[i-1]["lon"], trajectory[i]["lat"], trajectory[i]["lon"]) / hrs)
    normal_speed = sum(speeds) / len(speeds) if speeds else 15.0
    
    src_speeds = []
    for i, p, _ in points_near:
        if i > 0:
            t1, t2 = datetime.fromisoformat(trajectory[i-1]["time"].replace("Z", "+00:00")), datetime.fromisoformat(p["time"].replace("Z", "+00:00"))
            hrs = (t2 - t1).total_seconds() / 3600
            if hrs > 0: src_speeds.append(haversine(trajectory[i-1]["lat"], trajectory[i-1]["lon"], p["lat"], p["lon"]) / hrs)
    src_speed = sum(src_speeds) / len(src_speeds) if src_speeds else normal_speed
    
    ais_gaps = []
    for i in range(1, len(trajectory)):
        if not trajectory[i]["ais_active"] and trajectory[i-1]["ais_active"]:
            gap_end = i
            for j in range(i, len(trajectory)):
                if not trajectory[j]["ais_active"]: gap_end = j
                else: break
            t_start = datetime.fromisoformat(trajectory[i-1]["time"].replace("Z", "+00:00"))
            t_end = datetime.fromisoformat(trajectory[gap_end]["time"].replace("Z", "+00:00"))
            ais_gaps.append({
                "start_time": trajectory[i-1]["time"], "end_time": trajectory[gap_end]["time"], 
                "duration_hours": round((t_end - t_start).total_seconds() / 3600, 2), 
                "overlaps_source_window": abs((t_start - source_time).total_seconds() / 3600) <= 2.0 or abs((t_end - source_time).total_seconds() / 3600) <= 2.0
            })
    
    is_dark = len(ais_gaps) > 0 and any(g["overlaps_source_window"] for g in ais_gaps)
    min_dist = min((haversine(p["lat"], p["lon"], source_location["lat"], source_location["lon"]) for _, p, _ in points_near), default=100.0)
    
    return {
        "normal_speed_knots": round(normal_speed, 2), "source_window_speed_knots": round(src_speed, 2),
        "speed_drop_knots": round(normal_speed - src_speed, 2), "min_distance_to_source_km": round(min_dist, 2),
        "ais_gaps": ais_gaps, "is_dark_vessel": is_dark,
        "suspicious_behavior_detected": (normal_speed - src_speed) > 3.0 or is_dark or min_dist < 5.0
    }

