

def llm_output_validation(model, llm_output: str):
    return model.predict(llm_output)
    