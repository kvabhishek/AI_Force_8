import sqlite3

import pytest
from fastapi.testclient import TestClient

from app.db import connect_db, reset_database
from app.main import app

client = TestClient(app)


def setup_function() -> None:
    reset_database()


def test_request_approve_and_close_permit():
    response = client.post(
        "/api/permits/request",
        json={
            "requested_by": "U-001",
            "site_id": "GC-01",
            "permit_type_id": "HOT_WORK",
            "work_description": "Weld a new pipe support on the inlet manifold",
            "valid_from": "2026-11-15T07:30",
            "valid_to": "2026-11-15T14:30",
            "hazards": "Flammable gas; sparks; hot surfaces",
            "controls": "Gas test; fire watch; fire blanket",
        },
    )
    assert response.status_code == 200, response.text
    permit = response.json()["permit"]
    assert permit["status"] == "REQUESTED"

    approve = client.post(
        f"/api/permits/{permit['permit_id']}/approve",
        json={"user_id": "U-004", "comment": "Approved by area authority"},
    )
    assert approve.status_code == 200, approve.text
    permit = approve.json()["permit"]
    assert permit["status"] == "APPROVED"

    close = client.post(
        f"/api/permits/{permit['permit_id']}/close",
        json={"user_id": "U-004", "comment": "Closed after work is complete"},
    )
    assert close.status_code == 200, close.text
    assert close.json()["permit"]["status"] == "CLOSED"

    history = client.get(f"/api/permits/{permit['permit_id']}/history")
    assert history.status_code == 200
    assert any(item["action"] == "APPROVE" and item["success"] for item in history.json()["history"])


def test_self_approval_is_refused_and_recorded_in_history():
    response = client.post(
        "/api/permits/request",
        json={
            "requested_by": "U-007",
            "site_id": "GC-01",
            "permit_type_id": "HOT_WORK",
            "work_description": "Repair a valve flange",
            "valid_from": "2026-11-15T07:00",
            "valid_to": "2026-11-15T12:00",
            "hazards": "Residual pressure",
            "controls": "Isolation and venting",
        },
    )
    permit = response.json()["permit"]
    reject = client.post(
        f"/api/permits/{permit['permit_id']}/approve",
        json={"user_id": "U-007", "comment": "Self-approval attempt"},
    )
    assert reject.status_code == 400, reject.text
    payload = reject.json()
    assert payload["error"]["code"] == "SEPARATION_OF_DUTIES"

    history = client.get(f"/api/permits/{permit['permit_id']}/history")
    refused = [item for item in history.json()["history"] if item["action"] == "APPROVE" and not item["success"]]
    assert refused and "can't approve" in refused[0]["comment"]


def test_unknown_permit_type_and_invalid_date_are_rejected():
    bad_type = client.post(
        "/api/permits/request",
        json={
            "requested_by": "U-001",
            "site_id": "GC-01",
            "permit_type_id": "NO_SUCH_TYPE",
            "work_description": "Invalid permit type",
            "valid_from": "2026-11-15T07:00",
            "valid_to": "2026-11-15T12:00",
            "hazards": "None",
            "controls": "None",
        },
    )
    assert bad_type.status_code == 400
    assert bad_type.json()["error"]["code"] == "INVALID_REQUEST"

    bad_dates = client.post(
        "/api/permits/request",
        json={
            "requested_by": "U-001",
            "site_id": "GC-01",
            "permit_type_id": "HOT_WORK",
            "work_description": "Invalid date range",
            "valid_from": "2026-11-15T18:00",
            "valid_to": "2026-11-15T17:00",
            "hazards": "Residual pressure",
            "controls": "Controlled shutdown",
        },
    )
    assert bad_dates.status_code == 400
    assert bad_dates.json()["error"]["code"] == "INVALID_REQUEST"


def test_site_without_active_area_authority_is_rejected():
    request = client.post(
        "/api/permits/request",
        json={
            "requested_by": "U-008",
            "site_id": "BS-01",
            "permit_type_id": "HOT_WORK",
            "work_description": "Weld a support at the booster station",
            "valid_from": "2026-11-17T07:00",
            "valid_to": "2026-11-17T11:00",
            "hazards": "Flammable gas; hot surfaces",
            "controls": "Gas test; fire watch",
        },
    )
    assert request.status_code == 200, request.text
    permit = request.json()["permit"]

    reject = client.post(
        f"/api/permits/{permit['permit_id']}/approve",
        json={"user_id": "U-004", "comment": "Attempt to approve at an unsupported site"},
    )
    assert reject.status_code == 400, reject.text
    assert reject.json()["error"]["code"] == "ROLE_REQUIRED"


def test_user_with_multiple_roles_can_act_in_the_required_role():
    request = client.post(
        "/api/permits/request",
        json={
            "requested_by": "U-013",
            "site_id": "WS-01",
            "permit_type_id": "HOT_WORK",
            "work_description": "Repair a fabrication bay frame",
            "valid_from": "2026-11-16T08:00",
            "valid_to": "2026-11-16T12:00",
            "hazards": "Sparks; hot surfaces",
            "controls": "Fire watch; screens",
        },
    )
    permit = request.json()["permit"]
    approve = client.post(
        f"/api/permits/{permit['permit_id']}/approve",
        json={"user_id": "U-015", "comment": "Area authority with combined roles"},
    )
    assert approve.status_code == 200, approve.text
    assert approve.json()["permit"]["status"] == "APPROVED"


def test_request_requires_requester_role_and_site_assignment():
    base_payload = {
        "site_id": "GC-01",
        "permit_type_id": "HOT_WORK",
        "work_description": "Inspect a pipe support",
        "valid_from": "2026-11-17T07:00",
        "valid_to": "2026-11-17T10:00",
        "hazards": "Hot surfaces",
        "controls": "Wear protective equipment",
    }

    non_requester = client.post(
        "/api/permits/request",
        json={**base_payload, "requested_by": "U-024"},
    )
    assert non_requester.status_code == 400
    assert non_requester.json()["error"]["code"] == "ROLE_REQUIRED"

    wrong_site = client.post(
        "/api/permits/request",
        json={**base_payload, "requested_by": "U-001", "site_id": "WI-01"},
    )
    assert wrong_site.status_code == 400
    assert wrong_site.json()["error"]["code"] == "SITE_ASSIGNMENT"


def test_requester_with_all_site_access_can_request_any_site():
    with connect_db() as conn:
        conn.execute("UPDATE users SET sites = 'ALL' WHERE user_id = 'U-001'")

    response = client.post(
        "/api/permits/request",
        json={
            "requested_by": "U-001",
            "site_id": "BS-01",
            "permit_type_id": "HOT_WORK",
            "work_description": "Inspect the booster station",
            "valid_from": "2026-11-17T07:00",
            "valid_to": "2026-11-17T10:00",
            "hazards": "Hot surfaces",
            "controls": "Wear protective equipment",
        },
    )
    assert response.status_code == 200, response.text
    assert response.json()["permit"]["site_id"] == "BS-01"


def test_approval_checks_site_assignment_and_normalizes_role_formatting():
    wrong_role = client.post(
        "/api/permits/2/approve",
        json={"user_id": "U-001", "comment": "Requester approval attempt"},
    )
    assert wrong_role.status_code == 400
    assert wrong_role.json()["error"]["code"] == "ROLE_REQUIRED"
    wrong_role_history = client.get("/api/permits/2/history").json()["history"][-1]
    assert wrong_role_history["actor_role"] == "REQUESTER"

    denied = client.post(
        "/api/permits/2/approve",
        json={"user_id": "U-004", "comment": "Wrong-site approval attempt"},
    )
    assert denied.status_code == 400
    assert denied.json()["error"]["code"] == "SITE_ASSIGNMENT"

    approved = client.post(
        "/api/permits/2/approve",
        json={"user_id": "U-014", "comment": "Normalized area authority role"},
    )
    assert approved.status_code == 200, approved.text
    assert approved.json()["permit"]["status"] == "APPROVED"


def test_inactive_users_cannot_request_or_close_permits():
    inactive_request = client.post(
        "/api/permits/request",
        json={
            "requested_by": "U-019",
            "site_id": "GC-01",
            "permit_type_id": "HOT_WORK",
            "work_description": "Inspect the pipe support",
            "valid_from": "2026-11-17T07:00",
            "valid_to": "2026-11-17T10:00",
            "hazards": "Hot surfaces",
            "controls": "Wear protective equipment",
        },
    )
    assert inactive_request.status_code == 400
    assert inactive_request.json()["error"]["code"] == "ROLE_REQUIRED"

    inactive_close = client.post(
        "/api/permits/3/close",
        json={"user_id": "U-011", "comment": "Inactive authority attempt"},
    )
    assert inactive_close.status_code == 400
    assert inactive_close.json()["error"]["code"] == "ROLE_REQUIRED"


def test_invalid_transition_is_refused_and_recorded_in_history():
    response = client.post(
        "/api/permits/1/close",
        json={"user_id": "U-004", "comment": "Close before approval"},
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_TRANSITION"

    history = client.get("/api/permits/1/history")
    refused = [
        item for item in history.json()["history"]
        if item["action"] == "CLOSE" and not item["success"]
    ]
    assert len(refused) == 1
    assert refused[0]["check_id"] == "INVALID_TRANSITION"


def test_read_endpoints_return_users_permits_and_history():
    users = client.get("/api/users")
    permits = client.get("/api/permits")
    permit = client.get("/api/permits/1")
    history = client.get("/api/permits/1/history")

    assert users.status_code == 200
    assert len(users.json()) == 24
    assert permits.status_code == 200
    assert permits.json()["count"] == 3
    assert permit.status_code == 200
    assert permit.json()["permit_ref"] == "P-1001"
    assert history.status_code == 200
    assert history.json()["history"]
    assert client.get("/api/permits/999/history").status_code == 404


def test_permit_history_cannot_be_updated_or_deleted():
    with connect_db() as conn:
        history_id = conn.execute("SELECT history_id FROM permit_history LIMIT 1").fetchone()[0]
        with pytest.raises(sqlite3.IntegrityError, match="append-only"):
            conn.execute(
                "UPDATE permit_history SET comment = 'edited' WHERE history_id = ?",
                (history_id,),
            )
        with pytest.raises(sqlite3.IntegrityError, match="append-only"):
            conn.execute("DELETE FROM permit_history WHERE history_id = ?", (history_id,))
