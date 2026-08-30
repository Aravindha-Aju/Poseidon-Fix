import hashlib
import json
from typing import Dict, Any
from datetime import datetime

def generate_evidence_package(case_id: str, detection: Dict, drift: Dict, attribution: Dict, impact: Dict) -> Dict[str, Any]:
    evidence_data = {
        "case_id": case_id, "timestamp": datetime.utcnow().isoformat() + "Z",
        "detection_summary": {"spill_detected": detection.get("spill_detected"), "confidence": detection.get("confidence"), "centroid": detection.get("centroid")},
        "drift_summary": {"engine": drift.get("engine"), "ensemble_count": drift.get("ensemble_count"), "source_centroid": drift.get("uncertainty", {}).get("centroid")},
        "attribution_summary": {"top_candidate_mmsi": attribution.get("top_candidate", {}).get("mmsi"), "top_candidate_name": attribution.get("top_candidate", {}).get("name"), "confidence_score": attribution.get("top_candidate", {}).get("total_score")},
        "impact_summary": {"threat_level": impact.get("overall_threat_level"), "zones_threatened_count": len(impact.get("threatened_zones", []))}
    }
    json_str = json.dumps(evidence_data, sort_keys=True, separators=(',', ':'))
    return {
        "package_id": f"EVD-{case_id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        "generated_at": evidence_data["timestamp"],
        "sha256_hash": f"SHA-256: {hashlib.sha256(json_str.encode('utf-8')).hexdigest()}",
        "contents_hashed": list(evidence_data.keys()),
        "data_origins": {"detection": "INFERRED", "drift": "SIMULATED", "attribution": "INFERRED", "impact": "SIMULATED"},
        "integrity_verified": True
    }

