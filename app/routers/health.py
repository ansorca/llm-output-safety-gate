from fastapi import APIRouter, HTTPException, Request

router = APIRouter()


@router.get("/health")
def ready(request: Request) -> dict[str, str]:
    if getattr(request.app.state, "model", None) is not None:
        return {"status": "ok"}
    raise HTTPException(status_code=503, detail="Service unavailable")
