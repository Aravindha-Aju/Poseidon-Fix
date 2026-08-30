class PipelineRequest(BaseModel):
    case_id: str = "demo_case_001"
    image_id: Optional[str] = "sample_sar_001"
    hours_backward: int = 12

class AttributionCandidate(BaseModel):
    mmsi: str; name: str; total_score: float; spatial: float; temporal: float; trajectory: float; drift: float; behavioral: float; ais: float; explanation: str; is_dark_vessel: bool

class AttributionResult(BaseModel):
    ranking: List[AttributionCandidate]
    top_candidate: Optional[AttributionCandidate]
    explanation: str

class PipelineResponse(BaseModel):
    case_id: str; detection: Dict[str, Any]; drift: Dict[str, Any]; source_zone: Dict[str, Any]
    vessels: List[Dict[str, Any]]; behavior: Dict[str, Any]; attribution: AttributionResult
    impact: Dict[str, Any]; evidence: Dict[str, Any]; metrics: Dict[str, Any]; metadata: Dict[str, Any]

