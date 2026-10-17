from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def find_duplicate(
    disaster_type,
    description,
    location,
    existing_reports,
    threshold=0.70
):
    """
    Compare a new disaster report with existing reports.

    Returns:
        duplicate_flag: True/False
        duplicate_id: ID of the most similar report or None
        similarity: similarity percentage
    """

    if not existing_reports:
        return False, None, 0.0

    new_text = (
        f"{disaster_type} "
        f"{description or ''} "
        f"{location}"
    )

    existing_texts = []

    for report in existing_reports:
        text = (
            f"{report['disaster_type']} "
            f"{report['description'] or ''} "
            f"{report['location']}"
        )
        existing_texts.append(text)

    all_texts = [new_text] + existing_texts

    vectorizer = TfidfVectorizer(
        lowercase=True,
        ngram_range=(1, 2)
    )

    vectors = vectorizer.fit_transform(all_texts)

    similarities = cosine_similarity(
        vectors[0:1],
        vectors[1:]
    )[0]

    best_index = similarities.argmax()
    best_similarity = float(similarities[best_index])

    if best_similarity >= threshold:
        duplicate_id = existing_reports[best_index]["id"]
        return True, duplicate_id, best_similarity * 100

    return False, None, best_similarity * 100