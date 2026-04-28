from __future__ import annotations

from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.api.routes.internal import verify_source_ip
from app.core.config import Settings
from app.main import create_app


def _test_settings(enable_demo_users: bool = True) -> Settings:
    return Settings(
        node_id="test-node",
        peer_urls=(),
        viewer_limit=100,
        editor_limit=100,
        admin_limit=100,
        gossip_secret_key="test-gossip-secret-key-that-is-long-enough",
        jwt_secret_key="test-jwt-secret-key-that-is-long-enough",
        enable_demo_users=enable_demo_users,
        viewer_password="viewer123",
        admin_password="admin123",
    )


def test_permission_guard_blocks_viewer_and_allows_admin() -> None:
    app = create_app(_test_settings())
    client = TestClient(app)

    viewer_login = client.post("/auth/token", data={"username": "viewer", "password": "viewer123"})
    admin_login = client.post("/auth/token", data={"username": "admin", "password": "admin123"})

    viewer_token = viewer_login.json()["access_token"]
    admin_token = admin_login.json()["access_token"]

    viewer_response = client.get("/protected/admin", headers={"Authorization": f"Bearer {viewer_token}"})
    admin_response = client.get("/protected/admin", headers={"Authorization": f"Bearer {admin_token}"})

    assert viewer_response.status_code == 403
    assert admin_response.status_code == 200
    assert admin_response.json()["message"] == "Admin access granted to admin-1"


def test_login_and_me_endpoint_return_jwt_user() -> None:
    app = create_app(_test_settings())
    client = TestClient(app)

    login_response = client.post("/auth/token", data={"username": "admin", "password": "admin123"})
    assert login_response.status_code == 200

    access_token = login_response.json()["access_token"]
    me_response = client.get("/auth/me", headers={"Authorization": f"Bearer {access_token}"})

    assert me_response.status_code == 200
    assert me_response.json()["role"] == "admin"


def test_health_endpoint_is_available() -> None:
    app = create_app(_test_settings(enable_demo_users=False))
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_verify_source_ip_accepts_hostname_peers() -> None:
    request = SimpleNamespace(client=SimpleNamespace(host="127.0.0.1"))
    assert verify_source_ip(request, ("http://localhost:8000",))


def test_internal_state_requires_authentication() -> None:
    app = create_app(_test_settings())
    client = TestClient(app)

    unauthorized = client.get("/internal/gossip/state")
    assert unauthorized.status_code == 401

    admin_login = client.post("/auth/token", data={"username": "admin", "password": "admin123"})
    access_token = admin_login.json()["access_token"]
    authorized = client.get("/internal/gossip/state", headers={"Authorization": f"Bearer {access_token}"})
    assert authorized.status_code == 200
