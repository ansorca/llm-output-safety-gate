import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    spacy_model: str
    toxicity_threshold: float
    toxicity_model_retries: int
    toxicity_model_wait_time: int   

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            spacy_model=os.getenv("SPACY_MODEL", "en_core_web_sm"),
            toxicity_threshold=float(os.getenv("TOXICITY_THRESHOLD", 0.5)),
            toxicity_model_retries=int(os.getenv("TOXICITY_MODEL_RETRIES", 3)),
            toxicity_model_wait_time=int(os.getenv("TOXICITY_MODEL_WAIT_TIME", 2))
        )


settings = Settings.from_env()
