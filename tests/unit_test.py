from app.feature_engineering import hashed_feature


def test_hashed_feature_deterministic():
    v1 = hashed_feature("user_123", 100)
    v2 = hashed_feature("user_123", 100)
    assert v1 == v2


def test_hashed_feature_known_value():
    assert hashed_feature("test", 10) == hashed_feature("test", 10)
