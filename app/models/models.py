from pydantic import BaseModel, field_validator


class CheckRequest(BaseModel): 
    text: str

    @field_validator('text')
    @classmethod
    def check_feature_count(cls, v):
        l = len(v)
        if l == 0:
            raise ValueError("Empty string")
        if 10000 < l:
            raise ValueError("String is too large")
        return v
    
class SafetyVerdict(BaseModel):
    safe: bool
    score: float
    flags: list[str]
    latency_ms: float