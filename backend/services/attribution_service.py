# -*- coding: utf-8 -*-
import math
from typing import List, Dict, Any
from shapely.geometry import shape, Point

def haversine_km(lon1, lat1, lon2, lat2):
    R, lon1, lat1, lon2, lat2 = 6371.0, *map(math.radians, [lon1, lat1, lon2, lat2])
    a = math.sin((lat2-lat1)/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin((lon2-lon1)/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def score_spatial(vessel, centroid):
    min_dist = min(haversine_km(c[0], c[1], centroid[0], centroid[1]) for c in vessel["trajectory"])
    return 100 if min_dist < 2.0 else 85 if min_dist < 5.0 else 60 if min_dist < 10.0 else 30

def calculate_attribution(vessels, drift_result, behavior_results, target_time):
    centroid, source_poly = drift_result["centroid"], drift_result["source_polygon"]
    ranked = []
    for v in vessels:
        behav = behavior_results.get(v["mmsi"], {})
        s_spatial = score_spatial(v, centroid)
        s_temporal = 85 if behav.get("ais_gaps") else 50
        s_behavior = min(100, 50 + (20 if behav.get("speed_drop_knots", 0) > 3.0 else 0) + (15 if behav.get("loitering_detected") else 0) + (15 if behav.get("is_dark_vessel") else 0))
        s_drift = 90 if any(Point(c[0], c[1]).within(shape(source_poly)) for c in v["trajectory"]) else 40
        overall = int(s_spatial * 0.25 + s_temporal * 0.20 + s_behavior * 0.25 + s_drift * 0.20 + 50 * 0.10)
        ranked.append({"mmsi": v["mmsi"], "name": v["name"], "vessel_type": v["vessel_type"], "overall_score": overall,
            "factors": {"spatial": s_spatial, "temporal": s_temporal, "trajectory": s_spatial, "drift": s_drift, "behavior": s_behavior, "historical": 50},
            "behavior_evidence": behav, "data_classification": "INFERRED"})
    ranked.sort(key=lambda x: x["overall_score"], reverse=True)
    return ranked

def generate_explanation(top_vessel):
    name, score, behav = top_vessel["name"], top_vessel["overall_score"], top_vessel["behavior_evidence"]
    lines = [f"Vessel {name} ranked #1 based on available evidence:"]
    if top_vessel["factors"]["spatial"] > 70: lines.append("- Entered probable source region during estimated release window.")
    if top_vessel["factors"]["drift"] > 70: lines.append("- Trajectory intersects high-probability drift corridor.")
    if behav.get("speed_drop_knots", 0) > 2.0: lines.append(f"- Speed decreased by {behav['speed_drop_knots']} knots near estimated release time.")
    if behav.get("is_dark_vessel"): lines.append("- AIS gap overlaps part of the critical window.")
    lines.extend([f"\nOverall attribution confidence score: {score}/100.", "NOTE: This is an investigative lead, not legal proof of guilt."])
    return "\n".join(lines)

