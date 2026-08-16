from contextlib import asynccontextmanager

import spacy
from detoxify import Detoxify
from presidio_analyzer import AnalyzerEngine
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.services.toxicity import ToxicityModelTimeout

from app.config.settings import settings
from app.routers import check, health
from app.services.pii import LoadedSpacyNlpEngine


@asynccontextmanager
async def lifespan(app: FastAPI):
    nlp = spacy.load(settings.spacy_model)
    loaded_nlp_engine = LoadedSpacyNlpEngine(loaded_spacy_model=nlp)

    app.state.model = Detoxify('multilingual')
    app.state.pii_analyzer = AnalyzerEngine(nlp_engine=loaded_nlp_engine)
    app.state.toxicity_threshold = settings.toxicity_threshold
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(health.router)
app.include_router(check.router)

@app.exception_handler(ToxicityModelTimeout)
async def timeout_handler(request: Request, exc: ToxicityModelTimeout):
    return JSONResponse(
        status_code=504,
        content={"detail": "Upstream dependency timed out"},
    )