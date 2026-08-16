import time
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
from func_timeout import func_timeout, FunctionTimedOut
from app.logger import log

class ToxicityModelTimeout(Exception):
    """Custom exception for toxicity model timeout."""
    pass

def my_before_sleep(retry_state):
    log.warning(f"Retrying due to: {retry_state.outcome.exception()}. Attempt {retry_state.attempt_number} of {retry_state.retry_object.stop.max_attempt_number}. Waiting {retry_state.next_action.sleep} seconds before next attempt.")


# Combined logic: Retries up to 3 times, exponential backoff, filters exceptions
@retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(2), # Waits 2s between retries
    retry=retry_if_exception_type((ToxicityModelTimeout, )),  # Retry on timeout
    reraise=True, # Raises the original exception if all attempts fail
    before_sleep=my_before_sleep
)
def llm_output_validation(model, llm_output: str):
    try:
        result = func_timeout(10, model.predict, args=(llm_output,))
        return result
    except FunctionTimedOut:
        log.error("Toxicity model timed out after exhausting all retries")
        raise ToxicityModelTimeout("Function timed out after 3 retries")

    