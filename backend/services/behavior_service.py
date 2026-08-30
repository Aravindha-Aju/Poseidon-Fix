# -*- coding: utf-8 -*-
import math
from datetime import datetime
from typing import List, Dict, Any

def haversine(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    R = 6371.0
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])
    dlon, dlat = lon2 - lon1, lat2 - lat1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def calculate_speed_knots(coord1, coord2, time1: str, time2: str) -> float:
    dist_km = haversine(coord1[0], coord1[1], coord2[0], coord2[1])
    t1 = datetime.fromisoformat(time1.replace('Z', '+00:00'))
    t2 = datetime.fromisoformat(time2.replace('Z', '+00:00'))
    hours = abs((t2 - t1).total_seconds() / 3600.0)
    return (dist_km / hours) / 1.852 if hours > 0 else 0.0

def analyze_behavior(trajectory: List[List[float]], timestamps: List[str], target_time: str) -> Dict[str, Any]:
    if len(trajectory) < 2 or len(timestamps) < 2:
        return {"error": "Insufficient trajectory data"}
    
    ais_gaps = []
    for i in range(len(timestamps) - 1):
        t1 = datetime.fromisoformat(timestamps[i].replace('Z', '+00:00'))
        t2 = datetime.fromisoformat(timestamps[i+1].replace('Z', '+00:00'))
        gap_hours = (t2 - t1).total_seconds() / 3600.0
        if gap_hours > 1.5:
            ais_gaps.append({"start": timestamps[i], "end": timestamps[i+1], "duration_hours": round(gap_hours, 2)})
    
    speeds = [calculate_speed_knots(trajectory[i], trajectory[i+1], timestamps[i], timestamps[i+1]) for i in range(len(trajectory) - 1)]
    avg_speed = sum(speeds) / len(speeds) if speeds else 0.0
    min_speed = min(speeds) if speeds else 0.0
    
    target_dt = datetime.fromisoformat(target_time.replace('Z', '+00:00'))
    gap_overlaps = False
    overlapping_gap = None
    for gap in ais_gaps:
        g_start = datetime.fromisoformat(gap["start"].replace('Z', '+00:00'))
        g_end = datetime.fromisoformat(gap["end"].replace('Z', '+00:00'))
        if g_start <= target_dt <= g_end:
            gap_overlaps = True
            overlapping_gap = gap
            break
            
    return {
        "avg_speed_knots": round(avg_speed, 2),
        "min_speed_knots": round(min_speed, 2),
        "speed_drop_knots": round(avg_speed - min_speed, 2),
        "loitering_detected": min_speed < 3.0 and len(speeds) > 2,
        "ais_gaps": ais_gaps,
        "is_dark_vessel": gap_overlaps,
        "dark_vessel_reason": "AIS gap overlaps probable spill-source window" if gap_overlaps else None,
        "overlapping_gap": overlapping_gap,
        "data_classification": "INFERRED"
    }

