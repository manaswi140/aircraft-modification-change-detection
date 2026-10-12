
import re

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from scipy.optimize import linear_sum_assignment


MODEL_NAME = "all-MiniLM-L6-v2"
SIMILARITY_THRESHOLD = 0.70


def extract_numeric_values(text: str) -> list[str]:
    """Extract numeric values, including decimals and comma separators."""
    return re.findall(
        r"(?<!\w)\d+(?:,\d{3})*(?:\.\d+)?(?!\w)",
        text,
    )


def find_semantic_matches(
    old_requirements: list[dict],
    new_requirements: list[dict],
    similarity_threshold: float = SIMILARITY_THRESHOLD,
) -> list[dict]:
    """
    Find likely corresponding requirements using global one-to-one
    assignment and semantic similarity.

    Matches below the similarity threshold are discarded.
    Numeric differences are flagged for human review.

    Similarity does not establish technical equivalence or safety.
    """
    if not old_requirements or not new_requirements:
        return []

    old_texts = [item["text"] for item in old_requirements]
    new_texts = [item["text"] for item in new_requirements]

    model = SentenceTransformer(MODEL_NAME)

    old_embeddings = model.encode(old_texts)
    new_embeddings = model.encode(new_texts)

    similarity_matrix = cosine_similarity(
        old_embeddings,
        new_embeddings,
    )

    # Find the globally best one-to-one assignment.
    # Invalid pairs receive a large cost so valid pairs are preferred.
    valid_pairs = similarity_matrix >= similarity_threshold

    cost_matrix = np.where(
        valid_pairs,
        -similarity_matrix,
        1_000_000.0,
    )

    old_indices, new_indices = linear_sum_assignment(cost_matrix)

    matches = []

    for old_index, new_index in zip(old_indices, new_indices):
        similarity = float(
            similarity_matrix[old_index, new_index]
        )

        # Do not force low-similarity pairs into the result.
        if similarity < similarity_threshold:
            continue

        old_item = old_requirements[old_index]
        new_item = new_requirements[new_index]

        old_text = old_item["text"]
        new_text = new_item["text"]

        old_numbers = extract_numeric_values(old_text)
        new_numbers = extract_numeric_values(new_text)

        numeric_change = old_numbers != new_numbers

        matches.append({
            "old_id": old_item["id"],
            "new_id": new_item["id"],
            "old_text": old_text,
            "new_text": new_text,
            "similarity": round(similarity, 4),
            "numeric_change": numeric_change,
            "review_required": numeric_change,
            "old_source": old_item["source"],
            "old_location": old_item["location"],
            "new_source": new_item["source"],
            "new_location": new_item["location"],
        })

    # Return matches in the order of the original previous revision.
    old_order = {
        item["id"]: index
        for index, item in enumerate(old_requirements)
    }
    matches.sort(key=lambda item: old_order[item["old_id"]])

    return matches