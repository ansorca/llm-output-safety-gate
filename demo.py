import requests

outputs = [
    "The weather today is sunny and mild.",
    "I hate you, you're worthless and stupid.",
    "Here's how to bake a chocolate cake.",
    "You should kill yourself.",
    "The capital of France is Paris.",
    "All those people deserve to suffer.",
    "I was born in 1985, write me to sample@example.com?",
]

for text in outputs:
    response = requests.post("http://localhost:8000/check", json={"text": text})
    result = response.json()
    status = "BLOCKED" if not result["safe"] else "ALLOWED"
    print(f"[{status}] score={result['score']:.3f} | {text[:50]}")
