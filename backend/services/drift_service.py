# -*- coding: utf-8 -*-
import logging, random, math
from datetime import datetime, timedelta
from typing import List, Dict, Any

REGIONAL_PROFILES = {
    "Arabian Sea": {"current_x": 0.35, "current_y": 0.45, "wind_x": 6.0, "wind_y": 4.0},
    "Bay of Bengal": {"current_x": 0.15, "current_y": 0.30, "wind_x": 4.0, "wind_y": 3.0},
    "Deep Indian Ocean": {"current_x": -0.40, "current_y": 0.10, "wind_x": -5.0, "wind_y": 1.0}
}

def get_region(lon: float, lat: float) -> str:
    if 60 <= lon <= 78 and 0 <= lat <= 25: return "Arabian Sea"
    elif 80 <= lon <= 95 and 0 <= lat <= 22: return "Bay of Bengal"
    return "Arabian Sea"

def run_single_drift_simulation(lon: float, lat: float, hours: int, windage: float, noise_scale: float) -> List[List[float]]:
    profile = REGIONAL_PROFILES[get_region(lon, lat)]
    drift_x = profile["current_x"] + (profile["wind_x"] * windage)
    drift_y = profile["current_y"] + (profile["wind_y"] * windage)
    coordinates, current_lon, current_lat = [], float(lon), float(lat)
    for _ in range(hours + 1):
        coordinates.append([round(current_lon, 5), round(current_lat, 5)])
        current_lon -= (drift_x * 3600) / 111320 + random.uniform(-noise_scale, noise_scale)
        current_lat -= (drift_y * 3600) / 110540 + random.uniform(-noise_scale, noise_scale)
    return coordinates[::-1]

def calculate_ensemble_backward_trajectory(lon: float, lat: float, timestamp: str, hours_backward: int, num_ensemble: int = 10) -> Dict[str, Any]:
    random.seed(42)
    try:
        start_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        end_time = start_time - timedelta(hours=hours_backward)
        all_endpoints, all_trajectories = [], []
        windages = [0.02, 0.03, 0.04, 0.05, 0.025, 0.035, 0.045, 0.02, 0.04, 0.05]
        noises = [0.005, 0.01, 0.015, 0.02, 0.008, 0.012, 0.018, 0.005, 0.015, 0.02]
        
        for i in range(num_ensemble):
            traj = run_single_drift_simulation(lon, lat, hours_backward, windage=windages[i], noise_scale=noises[i])
            all_trajectories.append(traj)
            all_endpoints.append(traj[-1])
            
        mean_lon = sum(p[0] for p in all_endpoints) / num_ensemble
        mean_lat = sum(p[1] for p in all_endpoints) / num_ensemble
        uncertainty_deg = math.sqrt(sum((p[0]-mean_lon)**2 + (p[1]-mean_lat)**2 for p in all_endpoints) / num_ensemble)
        uncertainty_km = max(2.5, uncertainty_deg * 111.0)
        
        radius_deg = (uncertainty_km / 111.0) * 1.5
        source_polygon_coords = [[mean_lon + radius_deg * math.cos(2 * math.pi * i / 16), mean_lat + radius_deg * math.sin(2 * math.pi * i / 16)] for i in range(16)]
        source_polygon_coords.append(source_polygon_coords[0])
        
        return {
            "engine": "deterministic_fallback", "region_detected": get_region(lon, lat),
            "centroid": [round(mean_lon, 5), round(mean_lat, 5)], "uncertainty_km": round(uncertainty_km, 2),
            "confidence_level": 0.90, "ensemble_count": num_ensemble,
            "source_polygon": {"type": "Polygon", "coordinates": [source_polygon_coords]},
            "trajectories": all_trajectories[:3], "estimated_source_time": end_time.isoformat() + "Z",
            "data_classification": "SIMULATED"
        }
    except Exception as e:
        return {"error": str(e), "engine": "failed"}

