from typing import Dict, Any, List
import math

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat, dlon = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

ECOLOGICAL_ZONES = [
    {"name": "Lakshadweep Marine Sanctuary", "lat": 10.5, "lon": 72.6, "type": "Coral Reefs", "region": "Arabian Sea", "vulnerability": 0.9},
    {"name": "Gulf of Mannar Biosphere Reserve", "lat": 9.15, "lon": 79.15, "type": "Coral Reefs + Mangroves", "region": "Bay of Bengal", "vulnerability": 0.95},
    {"name": "Sundarbans National Park", "lat": 21.95, "lon": 89.0, "type": "Mangroves (Tiger Reserve)", "region": "Bay of Bengal", "vulnerability": 0.95}
]

def analyze_impact(forward_drift_end: List[float], region: str) -> Dict[str, Any]:
    end_lat, end_lon = forward_drift_end[0], forward_drift_end[1]
    threatened, max_severity = [], 0.0
    
    for zone in ECOLOGICAL_ZONES:
        if zone["region"] == region or region == "Deep Indian Ocean":
            dist = haversine(end_lat, end_lon, zone["lat"], zone["lon"])
            if dist < 200:
                severity = zone["vulnerability"] * (1 - (dist / 200))
                if severity > max_severity: max_severity = severity
                threatened.append({"name": zone["name"], "type": zone["type"], "distance_km": round(dist, 2), "severity_score": round(severity, 2), "data_origin": "SYNTHETIC_BOUNDARY"})
                
    threatened.sort(key=lambda x: x["severity_score"], reverse=True)
    overall = "CRITICAL" if max_severity > 0.7 else ("MODERATE" if max_severity > 0.4 else "LOW")
    return {"threatened_zones": threatened, "overall_threat_level": overall, "max_severity_score": round(max_severity, 2), "data_origin": "SIMULATED"}

