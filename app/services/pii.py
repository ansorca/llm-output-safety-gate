from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import SpacyNlpEngine
from spacy import Language


class LoadedSpacyNlpEngine(SpacyNlpEngine):
    def __init__(self, loaded_spacy_model: Language) -> None:
        super().__init__()
        # presidio's SpacyNlpEngine.nlp is untyped/None-inferred upstream; this is the documented
        #  override pattern
        self.nlp: dict[str, Language] = {"en": loaded_spacy_model}  # type: ignore[assignment]


SENSITIVE_PII = {"EMAIL_ADDRESS", "PHONE_NUMBER", "PERSON", "CREDIT_CARD", "US_SSN"}


def detect_pii(analyzer: AnalyzerEngine, text: str) -> list[str]:
    results = analyzer.analyze(text=text, language="en")
    return list({r.entity_type for r in results if r.entity_type in SENSITIVE_PII})