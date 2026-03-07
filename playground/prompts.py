DEFAULT_RUN_PROMPT = """You are a helpful AI assistant. Answer the following question or complete the following task:

{query}

Provide a clear, accurate, and well-reasoned response."""

DEFAULT_CORRECTNESS_EVALUATION_PROMPT = """You are an evaluation expert. Compare the model output against the ground truth and determine if it is correct.

Task/Query:
{query}

Model Output:
{result}

Ground Truth:
{ground_truth}

Evaluate whether the model output correctly answers the query. Consider:
1. Factual accuracy
2. Completeness of the answer
3. Appropriate format and reasoning

Respond with a JSON object containing:
- "correct": boolean indicating if the answer is correct
- "score": float between 0 and 1 representing correctness level
- "feedback": string explaining the evaluation"""
