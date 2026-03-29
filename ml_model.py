import random

def analyze_query(query):
    if "attack" in query.lower():
        return "suspicious"
    return "normal"

def privacy_score(query):
    # simulate differential privacy score
    return random.randint(75, 98)