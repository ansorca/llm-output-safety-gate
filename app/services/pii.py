from presidio_analyzer import AnalyzerEngine

SENSITIVE_PII = {"EMAIL_ADDRESS", "PHONE_NUMBER", "PERSON", "CREDIT_CARD", "US_SSN"}

def detect_pii(analyzer: AnalyzerEngine, text: str) -> list[str]:
    results = analyzer.analyze(text=text, language='en')
    return list({r.entity_type for r in results if r.entity_type in SENSITIVE_PII})