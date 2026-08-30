import logging
import random
from datetime import datetime, timedelta
from typing import Any, Dict, List
import math

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

REGIONAL_PROFILES = {
    "Arabian Sea": {"current_x": 0.35, "current_y": 0.45, "wind_x": 6.0, "wind_y": 4.0},
    "Bay of Bengal": {"current_x": 0.15, "current_y": 0.30, "wind_x": 4.0, "wind_y": 3.0},
    "Deep Indian Ocean": {"current_x": -0.40, "current_y": 0.10, "wind_x": -5.0, "wind_y": 1.0}
}

def get_region(lon: float, lat: float) -> str:
    if 60 <= lon <= 78 and 0 <= lat <= 25: return "Arabian Sea"
    elif 80 <= lon <= 95 and 0 <= lat <= 22: return "Bay of Bengal"
    return "Arabian Sea"

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat, dlon = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

def calculate_backward_trajectory_ensemble(lon: float, lat: float, timestamp: Any, hours_backward: Any, num_ensemble: int = 10) -> dict:
    try:
        start_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00')) if isinstance(timestamp, str) else timestamp
        hours = int(float(hours_backward))
        end_time = start_time - timedelta(hours=hours)
        region = get_region(lon, lat)
        profile = REGIONAL_PROFILES[region]
        
        all_trajectories = []
        for _ in range(num_ensemble):
            perturbation = random.uniform(0.8, 1.2)
            windage = 0.03 * random.uniform(0.8, 1.2)
            drift_x = (profile["current_x"] * perturbation) + (profile["wind_x"] * windage)
            drift_y = (profile["current_y"] * perturbation) + (profile["wind_y"] * windage)
            
            coordinates = []
            particles = [{"lon": float(lon) + random.uniform(-0.001, 0.001), "lat": float(lat) + random.uniform(-0.001, 0.001)} for _ in range(15)]
            
            for _ in range(hours + 1):
                mean_lon = sum(p["lon"] for p in particles) / len(particles)
                mean_lat = sum(p["lat"] for p in particles) / len(particles)
                coordinates.append([round(mean_lon, 5), round(mean_lat, 5)])
                for p in particles:
                    p["lon"] -= (drift_x * 3600) / 111320 + random.uniform(-0.002, 0.002)
                    p["lat"] -= (drift_y * 3600) / 110540 + random.uniform(-0.002, 0.002)
            all_trajectories.append(coordinates[::-1])
            
        source_points = [traj[-1] for traj in all_trajectories if len(traj) > 0]
        mean_source_lon = sum(p[0] for p in source_points) / len(source_points)
        mean_source_lat = sum(p[1] for p in source_points) / len(source_points)
        uncertainty_km = round(max(haversine(mean_source_lat, mean_source_lon, p[1], p[0]) for p in source_points), 2)
        
        mean_trajectory = [[round(sum(traj[i][0] for traj in all_trajectories)/len(all_trajectories), 5), round(sum(traj[i][1] for traj in all_trajectories)/len(all_trajectories), 5)] for i in range(len(all_trajectories[0]))]

        return {
            "engine": "fallback_ensemble", "ensemble_count": num_ensemble,
            "drift_path": {"type": "LineString", "coordinates": mean_trajectory},
            "source_polygon": {"type": "Polygon", "coordinates": [[[mean_source_lon - (uncertainty_km/111), mean_source_lat - (uncertainty_km/111)], [mean_source_lon + (uncertainty_km/111), mean_source_lat - (uncertainty_km/111)], [mean_source_lon + (uncertainty_km/111), mean_source_lat + (uncertainty_km/111)], [mean_source_lon - (uncertainty_km/111), mean_source_lat + (uncertainty_km/111)], [mean_source_lon - (uncertainty_km/111), mean_source_lat - (uncertainty_km/111)]]]},
            "estimated_source_time": end_time.isoformat(), "region_detected": region,
            "uncertainty": {"radius_km": uncertainty_km, "confidence_level": 0.90, "centroid": [round(mean_source_lon, 5), round(mean_source_lat, 5)]}
        }
    except Exception as e:
        logger.error(f"Drift service error: {str(e)}")
        return {"engine": "fallback_error", "uncertainty": {"radius_km": 10.0, "confidence_level": 0.50, "centroid": [float(lon), float(lat)]}}

