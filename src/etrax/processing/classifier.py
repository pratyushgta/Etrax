from ..database.merchant_rules import find_matching_rule


def classify_transaction(
    description,
    database_path=None
):
    rule = find_matching_rule(
        description,
        database_path=database_path
    )

    if rule is None:
        return {
            "transaction_type": "OTHER",
            "category": "Other",
            "subcategory": None,
            "confidence": 0.0,
            "needs_review": 1,
            "rule_id": None
        }

    return {
        "transaction_type": (
            rule["transaction_type"] or "OTHER"
        ),
        "category": rule["category"] or "Other",
        "subcategory": rule["subcategory"],
        "confidence": 1.0,
        "needs_review": 0,
        "rule_id": rule["rule_id"]
    }