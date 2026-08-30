# -*- coding: utf-8 -*-
import json, hashlib
from datetime import datetime
from typing import Dict, Any

def calculate_sha256(data: Any) -> str:
    return hashlib.sha256(json.dumps(data, sort_keys=True, separators=(',', ':')).encode('utf-8')).hexdigest()

def generate_evidence_package(pipeline_result: Dict[str, Any]) -> Dict[str, Any]:
    artifacts = {"spill_polygon": pipeline_result.get("detection", {}).get("spill_polygon"), "drift_parameters": pipeline_result.get("drift", {}), "ais_subset": pipeline_result.get("vessels", {}).get("candidates"), "model_config": {"model": "U-Net", "version": "1.0.0"}}
    return {"case_id": pipeline_result.get("case_id"), "generated_at": datetime.utcnow().isoformat() + "Z", "hashes": [{"artifact": k, "sha256": calculate_sha256(v), "timestamp": datetime.utcnow().isoformat() + "Z"} for k, v in artifacts.items() if v], "data_classification": "INFERRED/SIMULATED"}

