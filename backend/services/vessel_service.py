import json
import os
from datetime import datetime
from typing import List, Dict, Any

def load_demo_case(case_id: str = "demo_case_001") -> Dict[str, Any]:
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    case_path = os.path.join(base_dir, "data", "cases", f"{case_id}.json")
    if os.path.exists(case_path):
        with open(case_path, "r") as f:
            return json.load(f)
    raise FileNotFoundError(f"Case {case_id} not found")

def get_vessels_in_window(case_data: Dict[str, Any], source_time: datetime, window_hours: float = 2.0) -> List[Dict[str, Any]]:
    vessels = case_data.get("vessels", [])
    filtered = []
    for vessel in vessels:
        for point in vessel.get("trajectory", []):
            pt_time = datetime.fromisoformat(point["time"].replace("Z", "+00:00"))
            if abs((pt_time - source_time).total_seconds() / 3600) <= window_hours:
                filtered.append(vessel)
                break
    return filtered

