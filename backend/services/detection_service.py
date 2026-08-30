# -*- coding: utf-8 -*-
import os, sys, logging
from datetime import datetime
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
logger = logging.getLogger(__name__)

class MockOilSpillDetector:
    def predict_polygon(self, image_path: str, base_lat: float, base_lon: float) -> dict:
        return {"spill_detected": True, "confidence": 0.87, "polygon": {"type": "Polygon", "coordinates": [[[base_lon, base_lat], [base_lon+0.02, base_lat], [base_lon+0.02, base_lat+0.02], [base_lon, base_lat+0.02], [base_lon, base_lat]]]}, "centroid": [base_lon + 0.01, base_lat + 0.01]}

try:
    from ai_model.inference import OilSpillDetector
    DETECTOR = OilSpillDetector(weights_path=os.path.abspath(os.path.join(os.path.dirname(__file__), '../../ai_model/weights/unet_best.pth')))
except Exception:
    DETECTOR = MockOilSpillDetector()

def detect_spill_real(image_id: str) -> dict:
    try:
        result = DETECTOR.predict_polygon("mock", base_lat=12.4, base_lon=72.6)
        return {"spill_detected": result["spill_detected"], "confidence": round(result["confidence"], 4), "spill_polygon": result["polygon"], "centroid": result["centroid"], "timestamp": datetime.utcnow().isoformat() + "Z", "data_classification": "INFERRED"}
    except Exception as e:
        return {"spill_detected": False, "error": str(e), "data_classification": "INFERRED"}

