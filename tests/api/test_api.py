"""API smoke tests."""

from __future__ import annotations

import os
import uuid

import pytest

from src.framework.core.config.models import ApiAuthSettings, ApiSettings
from src.framework.core.quality.assertions.assert_api import ApiAssert
from src.framework.adapters.api_factory import create_api_client


@pytest.mark.api
@pytest.mark.smoke
def test_list_objects(api_client, api_ready):
    response = api_client.get("/objects", expected_status=200, timeout=10)

    ApiAssert.status_code(response, 200)
    payload = response.json()
    assert isinstance(payload, list), "Expected list response for /objects"
    ApiAssert.response_time_lt(response, 10_000)


@pytest.mark.api
@pytest.mark.smoke
def test_create_object(api_client, api_ready):
    name = f"automation-object-{uuid.uuid4().hex[:8]}"
    payload = {"name": name, "data": {"year": 2026, "framework": "pytest"}}

    response = api_client.post("/objects", json=payload, expected_status=200, timeout=10)

    ApiAssert.status_code(response, 200)
    ApiAssert.json_key(response, "id")
    ApiAssert.json_value(response, "name", name)
    ApiAssert.header_contains(response, "Content-Type", "application/json")

@pytest.mark.api
@pytest.mark.smoke
def test_get_single_object(api_client, api_ready):
    response = api_client.get("/objects/7", expected_status=200, timeout=10)

    ApiAssert.status_code(response, 200)
    ApiAssert.json_key(response, "id")
    ApiAssert.json_value(response, "id", "7")


@pytest.mark.api
@pytest.mark.integration
def test_post_mobile_archive_message(logger):
    base_url = "https://archiving-uat.myriacompliance.com"
    encrypted_user = (
        "QZqDeFJCYaoGcFtE0o1OEhKlYlDz+mQI3ix9E3s75meyaMdpJhzI3xRuzPyHKc3st+PmhJnpMuUpWwilnPwPBg=="
    )
    body = {
        "conversationId": "qclzagrqwu1vcprdmycje9ixvbsmwei+kevmfb1+pgm",
        "s3Path": (
            "ABCDEFGHIJKLMNOPQR/mobile/whatsapp/2026/04/06/qCLZAgrQWu1vcPrdMYCje9iXvbSmWEi+KEvmfB1+pGM/ArchivingExport-69d3a75f172fc44cafe72981_20260407071448_20260406123023649000/ArchivingExport-69d3a75f172fc44cafe72981_20260407071448_20260406123023649000.json"
        ),
        "date": "2026-04-06",
    }

    client = create_api_client(
        ApiSettings(
            base_url=base_url,
            timeout_sec=30,
            auth=ApiAuthSettings(type="none", token_env_var="API_TOKEN"),
        ),
        logger,
        retries=1,
    )

    try:
        response = client.post(
            "/api/v1/mobiles/myarchive/message",
            json=body,
            headers={
                "Encrypted-User": os.getenv("ENCRYPTED_USER", encrypted_user),
                "Content-Type": "application/json",
            },
            timeout=30,
        )
    finally:
        client.close()

    # Tightened success criteria for integration contract.
    assert response.status_code in (200, 201, 202), (
        f"Expected success status (200/201/202), got {response.status_code}. "
        f"Response body: {response.text[:1000]}"
    )
    ApiAssert.header_contains(response, "Content-Type", "application/json")
    ApiAssert.response_time_lt(response, 30_000)

    payload = response.json()
    assert isinstance(payload, dict), f"Expected JSON object response, got: {payload}"
    # Contract (observed): endpoint returns archive navigation + content metadata.
    required_keys = {
        "previousS3Path",
        "nextS3Path",
        "contents",
        "participants",
        "platform",
    }
    missing = required_keys - set(payload.keys())
    assert not missing, f"Missing expected keys: {sorted(missing)}. Got: {list(payload.keys())}"

    assert isinstance(payload.get("contents"), list), "Expected 'contents' to be a list"
    assert isinstance(payload.get("participants"), list), "Expected 'participants' to be a list"
    assert isinstance(payload.get("platform"), str) and payload.get("platform"), (
        "Expected 'platform' to be a non-empty string"
    )
