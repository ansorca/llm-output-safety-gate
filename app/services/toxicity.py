from typing import Protocol

from func_timeout import FunctionTimedOut, func_timeout
from tenacity import RetryCallState, retry, retry_if_exception_type, stop_after_attempt, wait_fixed

from app.config.settings import settings
from app.logger import log


class SupportsPredict(Protocol):
    def predict(self, text: str) -> dict[str, float]: ...


class ToxicityModelTimeout(Exception):
    """Custom exception for toxicity model timeout."""

    pass


def my_before_sleep(retry_state: RetryCallState) -> None:
    assert retry_state.outcome is not None, "Retry state outcome should not be None"
    max_attempts = getattr(retry_state.retry_object.stop, "max_attempt_number", "unknown")
    sleep_time = getattr(retry_state.next_action, "sleep", 0)

    log.warning(
        f"Retrying due to: {retry_state.outcome.exception()}.\
        Attempt {retry_state.attempt_number} of {max_attempts}.\
        Waiting {sleep_time} seconds before next attempt."
    )


# Combined logic: Retries up to 3 times, exponential backoff, filters exceptions
@retry(
    stop=stop_after_attempt(settings.toxicity_model_retries),
    wait=wait_fixed(settings.toxicity_model_wait_time),  # Waits specified time between retries
    retry=retry_if_exception_type((ToxicityModelTimeout,)),  # Retry on timeout
    reraise=True,  # Raises the original exception if all attempts fail
    before_sleep=my_before_sleep,
)
def llm_output_validation(model: SupportsPredict, llm_output: str) -> dict[str, float]:
    try:
        result = func_timeout(10, model.predict, args=(llm_output,))
        return result
    except FunctionTimedOut as e:
        msg = f"Function timed out after {settings.toxicity_model_retries} retries"
        raise ToxicityModelTimeout(msg) from e
