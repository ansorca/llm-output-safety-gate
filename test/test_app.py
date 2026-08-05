from unittest.mock import patch
from urllib import response
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture(scope="session")
def client():
    with TestClient(app) as client:
        yield client

def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_toxic_input_is_flagged(client):
    response = client.post("/check", json={"text": "I hate you"})
    assert response.status_code == 200
    assert response.json()["safe"] == False

def test_pii_input_is_flagged(client):
    response = client.post("/check", json={"text": "My phone number is 212-555-5555"})
    assert response.status_code == 200
    assert response.json()["safe"] == False

def test_safe_input_is_not_flagged(client):
    response = client.post("/check", json={"text": "Hello, how are you?"})
    assert response.status_code == 200
    assert response.json()["safe"] == True

def test_empty_input_is_flagged(client):
    response = client.post("/check", json={"text": ""})
    assert response.status_code == 422
    assert "detail" in response.json()

def test_missing_text_field_returns_error(client):
    response = client.post("/check", json={})
    assert response.status_code == 422  # Unprocessable Entity
    assert "detail" in response.json()

def test_non_string_input_returns_error(client):
    response = client.post("/check", json={"text": 12345})
    assert response.status_code == 422  # Unprocessable Entity
    assert "detail" in response.json()

def test_valid_long_input_is_handled(client):
    long_text = "h" * 10000  # 10,000 characters of 'a'
    response = client.post("/check", json={"text": long_text})
    assert response.status_code == 200
    assert response.json()["safe"] == True  # Assuming long text is safe if it doesn't contain toxic content

def test_invalid_long_input_is_flagged(client):
    long_text = "a" * 10001  # 10,001 characters of 'a'
    response = client.post("/check", json={"text": long_text})
    assert response.status_code == 422
    assert "detail" in response.json()

def test_special_characters_input_is_handled(client):
    special_text = "!@#$%^&*()_+-=[]{}|;':,.<>/?`~"
    response = client.post("/check", json={"text": special_text})
    assert response.status_code == 200
    assert response.json()["safe"] == True  # Assuming special characters alone are safe

def test_multilingual_input_is_handled(client):
    multilingual_text = "Bonjour, comment ça va?"
    response = client.post("/check", json={"text": multilingual_text})
    assert response.status_code == 200
    assert response.json()["safe"] == True  # Assuming multilingual text is safe if it doesn't contain toxic content

def test_multilingual_toxic_input_is_flagged(client):
    multilingual_toxic_text = "Je te déteste!"
    response = client.post("/check", json={"text": multilingual_toxic_text})
    assert response.status_code == 200
    assert response.json()["safe"] == False  # Toxic content in another language should be flagged as unsafe

def test_html_input_is_handled(client):
    html_text = "<p>This is a paragraph.</p>"
    response = client.post("/check", json={"text": html_text})
    assert response.status_code == 200
    assert response.json()["safe"] == True  # Assuming HTML input is safe if it doesn't contain toxic content

def test_unicode_input_is_handled(client):
    unicode_text = "Hello, 世界"
    response = client.post("/check", json={"text": unicode_text})
    assert response.status_code == 200
    assert response.json()["safe"] == True  # Assuming Unicode text is safe if it doesn't contain toxic content

def test_input_with_emojis_is_handled(client):
    emoji_text = "Hello 😊"
    response = client.post("/check", json={"text": emoji_text})
    assert response.status_code == 200
    assert response.json()["safe"] == True  # Assuming text with emojis is safe if it doesn't contain toxic content

def test_input_with_newlines_is_handled(client):
    newline_text = "Hello,\nHow are you?"
    response = client.post("/check", json={"text": newline_text})
    assert response.status_code == 200
    assert response.json()["safe"] == True  # Assuming text with newlines is safe if it doesn't contain toxic content

def test_input_with_tabs_is_handled(client):
    tab_text = "Hello,\tHow are you?"
    response = client.post("/check", json={"text": tab_text})
    assert response.status_code == 200
    assert response.json()["safe"] == True  # Assuming text with tabs is safe if it doesn't contain toxic content

def test_input_with_whitespace_is_handled(client):
    whitespace_text = "   Hello, how are you?   "
    response = client.post("/check", json={"text": whitespace_text})
    assert response.status_code == 200
    assert response.json()["safe"] == True  # Assuming text with leading/trailing whitespace is safe if it doesn't contain toxic content

def test_clearly_toxic_input_is_flagged(client):
    toxic_text = "You are the worst person ever!"
    response = client.post("/check", json={"text": toxic_text})
    assert response.status_code == 200
    assert response.json()["safe"] == False  # Clearly toxic input should be flagged as unsafe

def test_clearly_safe_input_is_not_flagged(client):
    safe_text = "I hope you have a great day!"
    response = client.post("/check", json={"text": safe_text})
    assert response.status_code == 200
    assert response.json()["safe"] == True  # Clearly safe input should not be flagged as unsafe

def test_input_with_mixed_content_is_handled(client):
    mixed_text = "Hello, I hope you have a great day! But I hate you and people are rude."
    response = client.post("/check", json={"text": mixed_text})
    assert response.status_code == 200
    assert response.json()["safe"] == False  # Mixed content with toxic parts should be flagged as unsafe

def test_pii_present_toxic_absent_is_flagged(client):
    pii_text = "My email is john.doe@example.com"
    response = client.post("/check", json={"text": pii_text})
    assert response.status_code == 200
    assert response.json()["safe"] == False  # PII present should be flagged as unsafe
    assert "EMAIL_ADDRESS" in response.json()["flags"]

def test_pii_present_toxic_present_is_flagged(client):
    pii_toxic_text = "You are an idiot! My email is john.doe@example.com"
    response = client.post("/check", json={"text": pii_toxic_text})
    latency = response.json()["latency_ms"]
    assert latency >= 0  # Ensure latency is a non-negative value
    assert response.status_code == 200
    assert response.json()["safe"] == False  # Both PII and toxic content present should be flagged as unsafe
    assert "EMAIL_ADDRESS" in response.json()["flags"]

def test_email_address_detection(client):
    email_text = "Contact me at john.doe@example.com"
    response = client.post("/check", json={"text": email_text})
    latency = response.json()["latency_ms"]
    assert latency >= 0  # Ensure latency is a non-negative value
    assert response.status_code == 200
    assert response.json()["safe"] == False  # Email address present should be flagged as unsafe
    assert "EMAIL_ADDRESS" in response.json()["flags"]

def test_phone_number_detection(client):
    phone_text = "Call me at 212-555-5555"
    response = client.post("/check", json={"text": phone_text})
    latency = response.json()["latency_ms"]
    assert latency >= 0  # Ensure latency is a non-negative value
    assert response.status_code == 200
    assert response.json()["safe"] == False  # Phone number present should be flagged as unsafe
    assert "PHONE_NUMBER" in response.json()["flags"]

def test_credit_card_detection(client):
    credit_card_text = "My credit card number is 4111 1111 1111 1111"
    response = client.post("/check", json={"text": credit_card_text})
    latency = response.json()["latency_ms"]
    assert latency >= 0  # Ensure latency is a non-negative value
    assert response.status_code == 200
    assert response.json()["safe"] == False  # Credit card number present should be flagged as unsafe
    assert "CREDIT_CARD" in response.json()["flags"]

def test_us_ssn_detection(client):
    ssn_text = "My SSN is 234-56-7890"
    response = client.post("/check", json={"text": ssn_text})
    latency = response.json()["latency_ms"]
    assert latency >= 0  # Ensure latency is a non-negative value
    assert response.status_code == 200
    assert response.json()["safe"] == False  # US SSN present should be flagged as unsafe
    assert "US_SSN" in response.json()["flags"]

def test_person_name_detection(client):
    person_name_text = "My name is John Doe"
    response = client.post("/check", json={"text": person_name_text})
    latency = response.json()["latency_ms"]
    assert latency >= 0  # Ensure latency is a non-negative value
    assert response.status_code == 200
    assert response.json()["safe"] == False  # Person name present should be flagged as unsafe

def test_location_detection(client):
    location_text = "I live in New York City"
    response = client.post("/check", json={"text": location_text})
    latency = response.json()["latency_ms"]
    assert latency >= 0  # Ensure latency is a non-negative value
    assert response.status_code == 200
    assert response.json()["safe"] == True  # Location present should not be flagged as unsafe unless it's considered sensitive PII

def test_date_detection(client):
    date_text = "My birthday is on January 1, 1990"
    response = client.post("/check", json={"text": date_text})
    latency = response.json()["latency_ms"]
    assert latency >= 0  # Ensure latency is a non-negative value
    assert response.status_code == 200
    assert response.json()["safe"] == True  # Date present should not be flagged as unsafe unless it's considered sensitive PII

def test_two_email_addresses_detection(client):
    two_email_text = "Contact me at john.doe@example.com or jane.doe@example.com"
    response = client.post("/check", json={"text": two_email_text})
    latency = response.json()["latency_ms"]
    assert latency >= 0  # Ensure latency is a non-negative value
    assert response.status_code == 200
    assert response.json()["safe"] == False  # Two email addresses present should be flagged as unsafe

def test_score_exactly_on_threshold_is_flagged(client):
    
    with patch('app.services.verdict.llm_output_validation') as mock_predict:
        # Mock the predict method to return a score exactly equal to the threshold
        mock_predict.return_value = {'toxicity': app.state.toxicity_threshold}
        
        exact_threshold_text = "This is a borderline case."
        response = client.post("/check", json={"text": exact_threshold_text})
        latency = response.json()["latency_ms"]
        assert latency >= 0  # Ensure latency is a non-negative value
        assert response.status_code == 200
        # Assuming the model returns a score exactly equal to the threshold for this input
        assert response.json()["safe"] == False  # Input with score exactly on threshold should be flagged as unsafeS