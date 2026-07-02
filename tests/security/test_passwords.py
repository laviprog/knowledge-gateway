from knowledge_gateway.security.passwords import hash_password, verify_password


def test_hash_password_roundtrip() -> None:
    password = "correct horse battery staple"
    password_hash = hash_password(password)

    assert password_hash != password
    assert verify_password(password, password_hash) is True


def test_verify_password_rejects_wrong_password() -> None:
    password_hash = hash_password("right")

    assert verify_password("wrong", password_hash) is False


def test_verify_password_rejects_malformed_hash() -> None:
    assert verify_password("anything", "not-a-valid-argon2-hash") is False


def test_hash_password_is_salted() -> None:
    # Argon2 embeds a random salt, so hashing the same password twice differs.
    assert hash_password("same") != hash_password("same")
