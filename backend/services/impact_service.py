# -*- coding: utf-8 -*-
import json, os
from typing import List, Dict, Any
from shapely.geometry import Point

def load_impact_zones():
    filepath = os.path.join(os.path.dirname(__file__), "../../data/impact/zones.geojson")
    if not os.path.exists(filepath): return []
    with open(filepath, "r") as f:
        return [{"name": f["properties"]["name"], "zone_type": f["properties"]["zone_type"], "vulnerability_score": f["properties"]["vulnerability_score"], "geometry": f["geometry"]} for f in json.load(f)["features"]]

def analyze_forward_impact(forward_drift_endpoint, zones):
    results = []
    try:
        endpoint_pt = Point(forward_drift_endpoint[0], forward_drift_endpoint[1])
        for zone in zones:
            dist = endpoint_pt.distance(Point(zone["geometry"]["coordinates"][0], zone["geometry"]["coordinates"][1])) * 111.0
            if dist < 20.0:
                results.append({"zone": zone["name"], "zone_type": zone["zone_type"], "distance_km": round(dist, 2), "intersection": dist < 5.0, "vulnerability_score": zone["vulnerability_score"], "severity": "HIGH" if zone["vulnerability_score"] > 0.8 else "MEDIUM", "data_classification": "SIMULATED"})
    except Exception: pass
    return results

