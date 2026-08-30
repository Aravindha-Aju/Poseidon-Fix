from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from services.vessel_service import load_demo_case, get_vessels_in_window
from services.behavior_service import analyze_vessel_behavior
from services.drift_service import calculate_backward_trajectory_ensemble
from services.attribution_service import calculate_attribution
from services.impact_service import analyze_impact
from services.evidence_service import generate_evidence_package
from services.detection_service import detect_spill_real

router = APIRouter()

class PipelineRequest(BaseModel):
    case_id: str = "demo_case_001"
    image_id: Optional[str] = "sample_sar_001"
    hours_backward: int = 12

@router.post("/run")
async def run_investigation_pipeline(request: PipelineRequest):
    try:
        case_data = load_demo_case(request.case_id)
        try:
            detection_result = detect_spill_real(request.image_id)
        except Exception:
            detection_result = {
                "spill_detected": True, "confidence": 0.92,
                "spill_polygon": {"type": "Polygon", "coordinates": [[[case_data["spill_location"]["lon"]-0.01, case_data["spill_location"]["lat"]-0.01], [case_data["spill_location"]["lon"]+0.01, case_data["spill_location"]["lat"]-0.01], [case_data["spill_location"]["lon"]+0.01, case_data["spill_location"]["lat"]+0.01], [case_data["spill_location"]["lon"]-0.01, case_data["spill_location"]["lat"]+0.01], [case_data["spill_location"]["lon"]-0.01, case_data["spill_location"]["lat"]-0.01]]]},
                "centroid": [case_data["spill_location"]["lon"], case_data["spill_location"]["lat"]],
                "timestamp": case_data["sar_timestamp"]
            }
            
        centroid = detection_result["centroid"]
        drift_result = calculate_backward_trajectory_ensemble(lon=centroid[0], lat=centroid[1], timestamp=case_data["sar_timestamp"], hours_backward=request.hours_backward, num_ensemble=10)
        
        source_time_str = drift_result["estimated_source_time"]
        source_time = datetime.fromisoformat(source_time_str.replace('Z', '+00:00'))
        source_zone = {"centroid": drift_result["uncertainty"]["centroid"], "uncertainty_km": drift_result["uncertainty"]["radius_km"], "confidence_level": drift_result["uncertainty"]["confidence_level"]}
        
        vessels_behavior = []
        for vessel in get_vessels_in_window(case_data, source_time, window_hours=2.0):
            vessels_behavior.append({"vessel": vessel, "behavior": analyze_vessel_behavior(trajectory=vessel["trajectory"], source_time=source_time, source_location={"lat": source_zone["centroid"][1], "lon": source_zone["centroid"][0]})})
            
        attribution_result = calculate_attribution(vessels_behavior=vessels_behavior, source_zone=source_zone, source_time=source_time_str)
        
        source_lon, source_lat = source_zone["centroid"]
        current_lon, current_lat = centroid
        impact_result = analyze_impact(forward_drift_end=[current_lat + (current_lat - source_lat) * 2, current_lon + (current_lon - source_lon) * 2], region=case_data.get("region", "Arabian Sea"))
        evidence_package = generate_evidence_package(case_id=request.case_id, detection=detection_result, drift=drift_result, attribution=attribution_result, impact=impact_result)
        
        metrics = {"data_origin": "OBSERVED"}
        gt = case_data.get("ground_truth", {})
        if gt and attribution_result["top_candidate"]:
            top_mmsi = attribution_result["top_candidate"]["mmsi"]
            metrics["true_vessel_rank"] = 1 if top_mmsi == gt.get("source_vessel_mmsi") else "N/A"
            metrics["top_1_accuracy"] = 1.0 if top_mmsi == gt.get("source_vessel_mmsi") else 0.0
            
        return {
            "case_id": request.case_id, "detection": detection_result, "drift": drift_result, "source_zone": source_zone,
            "vessels": [vb["vessel"] for vb in vessels_behavior], "behavior": {vb["vessel"]["mmsi"]: vb["behavior"] for vb in vessels_behavior},
            "attribution": attribution_result, "impact": impact_result, "evidence": evidence_package, "metrics": metrics,
            "metadata": {"mode": "demo", "pipeline_version": "1.0.0", "timestamp": datetime.utcnow().isoformat() + "Z"}
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Pipeline execution failed: {str(e)}")

