from fastapi import APIRouter, Request
from app.models.models import CheckRequest, SafetyVerdict
from app.services.verdict import build_verdict

router = APIRouter()


@router.post("/check", response_model=SafetyVerdict)
def check(llm_output: CheckRequest, request: Request) -> SafetyVerdict:
    verdict = build_verdict(llm_output.text, request.app.state.model, request.app.state.pii_analyzer, request.app.state.toxicity_threshold)
    return verdict
