from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from app.models.models import CheckRequest, SafetyVerdict
from app.services.toxicity import llm_output_validation
from app.services.pii import detect_pii
from detoxify import Detoxify
import time
from app.logger import log
from presidio_analyzer import AnalyzerEngine
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.model = Detoxify('multilingual')
    app.state.pii_analyzer = AnalyzerEngine()
    app.state.toxicity_threshold = float(os.getenv("TOXICITY_THRESHOLD", 0.5))
    yield

app = FastAPI(lifespan=lifespan)


@app.get("/health")
def ready():
    if getattr(app.state, "model", None) is not None:
        return {"status": "OK"}
    raise HTTPException(status_code=503, detail="Service unavailable")

@app.post("/check", response_model=SafetyVerdict)
def check(llm_output: CheckRequest) -> SafetyVerdict:
    log.info("Check request started", )
    start = time.perf_counter()
    input_length = len(llm_output.text)

    validation =  llm_output_validation(app.state.model,  llm_output.text)
    score = float(validation['toxicity'])


    pii_flags = detect_pii(app.state.pii_analyzer, llm_output.text)
    flags = [k for k, v in validation.items() if v >= app.state.toxicity_threshold] + pii_flags

    safe = score < app.state.toxicity_threshold and len(pii_flags) == 0
    
    end = time.perf_counter()
    latency_ms = (end - start) * 1000
    log.info("Check request completed", latency_ms=latency_ms, input_length=input_length, safe=safe, score=score, flags=flags)

    return SafetyVerdict(latency_ms=latency_ms, safe=safe, score=score, flags=flags)
