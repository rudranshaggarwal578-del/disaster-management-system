from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


from difflib import SequenceMatcher


def find_duplicate(
    disaster_type,
    description,
    location,
    existing_reports,
    threshold=60
):
    """
    Compare a new disaster report with existing reports.

    Returns:
        duplicate_flag: True/False
        duplicate_id: ID of similar report or None
        similarity: Final similarity percentage
    """

    if not existing_reports:
        return False, None, 0.0

    new_type = (disaster_type or "").strip().lower()
    new_location = (location or "").strip().lower()
    new_description = (description or "").strip().lower()

    best_score = 0
    duplicate_id = None

    for report in existing_reports:

        old_type = (report["disaster_type"] or "").strip().lower()
        old_location = (report["location"] or "").strip().lower()
        old_description = (report["description"] or "").strip().lower()

        # 1. Disaster type score (20%)
        type_score = 20 if new_type == old_type else 0

        # 2. Location score (30%)
        location_similarity = SequenceMatcher(
            None,
            new_location,
            old_location
        ).ratio()

        location_score = location_similarity * 30

        # 3. Description score (50%)
        description_score = 0

        if new_description and old_description:

            vectorizer = TfidfVectorizer(
                lowercase=True,
                ngram_range=(1, 2)
            )

            try:
                vectors = vectorizer.fit_transform([
                    new_description,
                    old_description
                ])

                description_similarity = cosine_similarity(
                    vectors[0:1],
                    vectors[1:2]
                )[0][0]

                description_score = description_similarity * 50

            except ValueError:
                description_score = 0

        # Final weighted score
        total_score = (
            type_score +
            location_score +
            description_score
        )

        if total_score > best_score:
            best_score = total_score
            duplicate_id = report["id"]

    if best_score >= threshold:
        return True, duplicate_id, best_score

    return False, None, best_score