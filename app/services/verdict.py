from app.models.models import SafetyVerdict
from app.logger import log
import time
from app.services.pii import detect_pii
from app.services.toxicity import llm_output_validation
from detoxify import Detoxify
from presidio_analyzer import AnalyzerEngine

def build_verdict(text: str, model: Detoxify, pii_analyzer: AnalyzerEngine, toxicity_threshold: float) -> SafetyVerdict:
        log.info("Build verdict request started", )
        start = time.perf_counter()
        input_length = len(text)

        validation =  llm_output_validation(model,  text)
        score = float(validation['toxicity'])
        pii_flags = detect_pii(pii_analyzer, text)
        flags = [k for k, v in validation.items() if v >= toxicity_threshold] + pii_flags  
        safe = score <= toxicity_threshold and len(pii_flags) == 0 and len(flags) == 0
        end = time.perf_counter()
        latency_ms = (end - start) * 1000
        log.info("Build verdict request completed", latency_ms=latency_ms, input_length=input_length, safe=safe, score=score, flags=flags)
        return SafetyVerdict(latency_ms=latency_ms, safe=safe, score=score, flags=flags)
    