# -*- coding: utf-8 -*-
import json
import os
from typing import List, Dict, Any
from shapely.geometry import shape, Point

DATA_DIR = os.path.join(os.path.dirname(__file__), "../../data")

def load_vessels(case_id: str) -> List[Dict[str, Any]]:
    filepath = os.path.join(DATA_DIR, "ais", f"{case_id}.geojson")
    if not os.path.exists(filepath):
        filepath = os.path.join(DATA_DIR, "ais", "demo_case_001.geojson")
    with open(filepath, "r") as f:
        geojson = json.load(f)
    return [{
        "mmsi": f["properties"]["mmsi"], "name": f["properties"]["name"],
        "vessel_type": f["properties"]["vessel_type"], "flag": f["properties"]["flag"],
        "imo": f["properties"]["imo"], "trajectory": f["geometry"]["coordinates"]
    } for f in geojson["features"]]

def query_vessels(source_polygon: Dict[str, Any], start_time: str, end_time: str, buffer_km: float = 15.0) -> List[Dict[str, Any]]:
    vessels = load_vessels("demo_case_001")
    try:
        buffered_poly = shape(source_polygon).buffer(buffer_km / 111.0)
        return [v for v in vessels if any(Point(c[0], c[1]).within(buffered_poly) for c in v["trajectory"])]
    except Exception:
        return vessels

