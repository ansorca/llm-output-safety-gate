import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    spacy_model: str
    toxicity_threshold: float

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            spacy_model=os.getenv("SPACY_MODEL", "en_core_web_sm"),
            toxicity_threshold=float(os.getenv("TOXICITY_THRESHOLD", 0.5)),
        )


settings = Settings.from_env()
