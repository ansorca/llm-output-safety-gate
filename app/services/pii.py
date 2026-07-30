from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import SpacyNlpEngine

class LoadedSpacyNlpEngine(SpacyNlpEngine):
    def __init__(self, loaded_spacy_model):
        super().__init__()
        self.nlp = {"en": loaded_spacy_model}

SENSITIVE_PII = {"EMAIL_ADDRESS", "PHONE_NUMBER", "PERSON", "CREDIT_CARD", "US_SSN"}

def detect_pii(analyzer: AnalyzerEngine, text: str) -> list[str]:
    results = analyzer.analyze(text=text, language='en')
    return list({r.entity_type for r in results if r.entity_type in SENSITIVE_PII})