import time
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
from func_timeout import func_timeout, FunctionTimedOut

# Combined logic: Retries up to 3 times, exponential backoff, filters exceptions
@retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(2), # Waits 2s between retries
    retry=retry_if_exception_type((FunctionTimedOut, Exception)),  # Retry on timeout or any other exception
    reraise=True # Raises the original exception if all attempts fail
)
def llm_output_validation(model, llm_output: str):
    return func_timeout(10, model.predict, args=(llm_output,))
    