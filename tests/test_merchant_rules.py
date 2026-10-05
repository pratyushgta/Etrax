from src.etrax.database.merchant_rules import (
    create_rule,
    get_rule,
    list_rules,
    find_matching_rule
)


def test_create_rule(test_database):
    rule_id = create_rule(
        merchant_pattern="SWIGGY",
        category="Dining",
        transaction_type="EXPENSE",
        database_path=test_database
    )

    assert rule_id == 1


def test_get_rule(test_database):
    rule_id = create_rule(
        merchant_pattern="AMAZON",
        category="Shopping",
        transaction_type="EXPENSE",
        database_path=test_database
    )

    rule = get_rule(
        rule_id,
        database_path=test_database
    )

    assert rule["merchant_pattern"] == "AMAZON"
    assert rule["category"] == "Shopping"


def test_list_rules(test_database):
    create_rule(
        merchant_pattern="SWIGGY",
        category="Dining",
        transaction_type="EXPENSE",
        database_path=test_database
    )

    create_rule(
        merchant_pattern="DMART",
        category="Groceries",
        transaction_type="EXPENSE",
        database_path=test_database
    )

    rules = list_rules(database_path=test_database)

    assert len(rules) == 2


def test_matching_is_case_insensitive(test_database):
    create_rule(
        merchant_pattern="SWIGGY",
        category="Dining",
        transaction_type="EXPENSE",
        database_path=test_database
    )

    rule = find_matching_rule(
        "Swiggy India Online",
        database_path=test_database
    )

    assert rule is not None
    assert rule["category"] == "Dining"


def test_priority_wins(test_database):
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

    rule = find_matching_rule(
        "AMAZON INDIA ORDER",
        database_path=test_database
    )

    assert rule is not None
    assert rule["subcategory"] == "Electronics"


def test_no_matching_rule(test_database):
    rule = find_matching_rule(
        "UNKNOWN MERCHANT",
        database_path=test_database
    )

    assert rule is None