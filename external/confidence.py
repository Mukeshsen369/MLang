def aggregate(results):
    """
    Conservative aggregation:
    - average confidence
    - penalize disagreement
    """
    if not results:
        return 0.0

    base = sum(r["confidence"] for r in results) / len(results)

    # If sources disagree → reduce confidence
    if len(results) > 1:
        summaries = set(
            s for r in results for s in r["summaries"]
        )
        if len(summaries) > len(results):
            base *= 0.85

    return round(base, 2)
