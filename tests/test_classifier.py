from src.etrax.database.merchant_rules import create_rule
from src.etrax.processing.classifier import classify_transaction


def test_known_merchant_is_classified(test_database):
    create_rule(
        merchant_pattern="SWIGGY",
        category="Dining",
        subcategory="Food Delivery",
        transaction_type="EXPENSE",
        database_path=test_database
    )

    result = classify_transaction(
        "Swiggy India",
        database_path=test_database
    )

    assert result["transaction_type"] == "EXPENSE"
    assert result["category"] == "Dining"
    assert result["subcategory"] == "Food Delivery"
    assert result["confidence"] == 1.0
    assert result["needs_review"] == 0
    assert result["rule_id"] == 1


def test_unknown_merchant_needs_review(test_database):
    result = classify_transaction(
        "UNKNOWN MERCHANT",
        database_path=test_database
    )

    assert result["transaction_type"] == "OTHER"
    assert result["category"] == "Other"
    assert result["confidence"] == 0.0
    assert result["needs_review"] == 1
    assert result["rule_id"] is None


def test_high_priority_rule_is_used(test_database):
    create_rule(
        merchant_pattern="AMAZON",
        category="Shopping",
        transaction_type="EXPENSE",
        priority=100,
        database_path=test_database
    )

    create_rule(
        merchant_pattern="AMAZON INDIA",
        category="Shopping",
        subcategory="Electronics",
        transaction_type="EXPENSE",
        priority=200,
        database_path=test_database
    )

    result = classify_transaction(
        "AMAZON INDIA ORDER",
        database_path=test_database
    )

    assert result["subcategory"] == "Electronics"
    assert result["rule_id"] == 2