"""
Smoke test for cryptography wheel stability.

Standalone script — no dependencies beyond `cryptography` and the Python stdlib.
Exercises core primitives to verify the wheel loads and works correctly.
Exit code 0 on success, 1 on any failure.
"""

import datetime
import os
import sys
import traceback


def test_import_and_version():
    """Import cryptography and print version."""
    import cryptography

    version = cryptography.__version__
    assert version, "Version string is empty"
    print(f"  cryptography version: {version}")


def test_openssl_backend():
    """Verify the OpenSSL backend loads and report version."""
    from cryptography.hazmat.backends.openssl.backend import backend

    text = backend.openssl_version_text()
    assert "OpenSSL" in text or "BoringSSL" in text or "LibreSSL" in text
    print(f"  OpenSSL version: {text}")


def test_fernet_roundtrip():
    """Fernet symmetric encrypt/decrypt roundtrip."""
    from cryptography.fernet import Fernet, MultiFernet

    key = Fernet.generate_key()
    f = Fernet(key)
    plaintext = b"smoke-test-payload"
    token = f.encrypt(plaintext)
    assert f.decrypt(token) == plaintext

    # MultiFernet rotation
    key2 = Fernet.generate_key()
    mf = MultiFernet([Fernet(key2), f])
    rotated = mf.rotate(token)
    assert mf.decrypt(rotated) == plaintext


def test_sha256():
    """SHA-256 hash computation."""
    from cryptography.hazmat.primitives import hashes

    digest = hashes.Hash(hashes.SHA256())
    digest.update(b"hello ")
    digest.update(b"world")
    result = digest.finalize()
    assert len(result) == 32
    expected = "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"
    assert result.hex() == expected


def test_hmac():
    """HMAC-SHA256 message authentication."""
    from cryptography.hazmat.primitives import hmac, hashes

    h = hmac.HMAC(b"secret-key", hashes.SHA256())
    h.update(b"message")
    sig = h.finalize()
    assert len(sig) == 32

    # Verify path
    h2 = hmac.HMAC(b"secret-key", hashes.SHA256())
    h2.update(b"message")
    h2.verify(sig)  # raises on mismatch


def test_aesgcm():
    """AES-GCM authenticated encryption with associated data."""
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM

    key = AESGCM.generate_key(bit_length=256)
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    aad = b"authenticated-but-unencrypted"
    plaintext = b"secret data"
    ct = aesgcm.encrypt(nonce, plaintext, aad)
    assert aesgcm.decrypt(nonce, ct, aad) == plaintext


def test_chacha20poly1305():
    """ChaCha20Poly1305 AEAD."""
    from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305

    key = ChaCha20Poly1305.generate_key()
    cipher = ChaCha20Poly1305(key)
    nonce = os.urandom(12)
    ct = cipher.encrypt(nonce, b"data", b"aad")
    assert cipher.decrypt(nonce, ct, b"aad") == b"data"


def test_rsa_sign_verify():
    """RSA-2048 PSS sign and verify."""
    from cryptography.hazmat.primitives.asymmetric import rsa, padding
    from cryptography.hazmat.primitives import hashes

    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    message = b"rsa smoke test"
    signature = private_key.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH,
        ),
        hashes.SHA256(),
    )
    private_key.public_key().verify(
        signature,
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH,
        ),
        hashes.SHA256(),
    )


def test_ec_sign_verify():
    """ECDSA P-256 sign and verify."""
    from cryptography.hazmat.primitives.asymmetric import ec
    from cryptography.hazmat.primitives import hashes

    private_key = ec.generate_private_key(ec.SECP256R1())
    message = b"ecdsa smoke test"
    signature = private_key.sign(message, ec.ECDSA(hashes.SHA256()))
    private_key.public_key().verify(signature, message, ec.ECDSA(hashes.SHA256()))


def test_ed25519():
    """Ed25519 sign and verify."""
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

    private_key = Ed25519PrivateKey.generate()
    message = b"ed25519 smoke test"
    signature = private_key.sign(message)
    private_key.public_key().verify(signature, message)


def test_x25519_key_exchange():
    """X25519 Diffie-Hellman key exchange."""
    from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey

    sk_a = X25519PrivateKey.generate()
    sk_b = X25519PrivateKey.generate()
    shared_a = sk_a.exchange(sk_b.public_key())
    shared_b = sk_b.exchange(sk_a.public_key())
    assert shared_a == shared_b
    assert len(shared_a) == 32


def test_x509_self_signed():
    """Generate a self-signed X.509 certificate."""
    from cryptography import x509
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import ec
    from cryptography.x509.oid import NameOID

    key = ec.generate_private_key(ec.SECP256R1())
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, "smoke-test"),
    ])
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.now(datetime.timezone.utc))
        .not_valid_after(
            datetime.datetime.now(datetime.timezone.utc)
            + datetime.timedelta(days=1)
        )
        .sign(key, hashes.SHA256())
    )
    assert cert.subject == subject
    assert cert.issuer == issuer


def test_hkdf():
    """HKDF key derivation."""
    from cryptography.hazmat.primitives.kdf.hkdf import HKDF
    from cryptography.hazmat.primitives import hashes

    derived = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b"salt",
        info=b"info",
    ).derive(b"input-key-material")
    assert len(derived) == 32


def test_pbkdf2():
    """PBKDF2-HMAC password-based key derivation."""
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b"smoke-salt",
        iterations=100_000,
    )
    key = kdf.derive(b"password")
    assert len(key) == 32

    # Verify path
    kdf2 = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b"smoke-salt",
        iterations=100_000,
    )
    kdf2.verify(b"password", key)  # raises on mismatch


def test_key_serialization_roundtrip():
    """EC key PEM serialization roundtrip."""
    from cryptography.hazmat.primitives.asymmetric import ec
    from cryptography.hazmat.primitives import serialization

    private_key = ec.generate_private_key(ec.SECP256R1())

    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    loaded = serialization.load_pem_private_key(pem, password=None)
    assert (
        loaded.private_numbers().private_value
        == private_key.private_numbers().private_value
    )

    # Public key roundtrip
    pub_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    loaded_pub = serialization.load_pem_public_key(pub_pem)
    assert (
        loaded_pub.public_numbers().x
        == private_key.public_key().public_numbers().x
    )


# ---------------------------------------------------------------------------

ALL_TESTS = [
    test_import_and_version,
    test_openssl_backend,
    test_fernet_roundtrip,
    test_sha256,
    test_hmac,
    test_aesgcm,
    test_chacha20poly1305,
    test_rsa_sign_verify,
    test_ec_sign_verify,
    test_ed25519,
    test_x25519_key_exchange,
    test_x509_self_signed,
    test_hkdf,
    test_pbkdf2,
    test_key_serialization_roundtrip,
]


def main():
    passed = 0
    failed = 0
    errors = []

    print(f"Running {len(ALL_TESTS)} cryptography smoke tests ...\n")

    for test_fn in ALL_TESTS:
        name = test_fn.__name__
        try:
            test_fn()
            print(f"  PASS  {name}")
            passed += 1
        except Exception:
            print(f"  FAIL  {name}")
            traceback.print_exc()
            errors.append(name)
            failed += 1

    print(f"\n{'='*50}")
    print(f"Results: {passed} passed, {failed} failed, {len(ALL_TESTS)} total")
    if errors:
        print(f"Failed:  {', '.join(errors)}")
    print(f"{'='*50}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
