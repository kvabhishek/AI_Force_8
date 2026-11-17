from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta, timezone
from typing import Any

from app.db import connect_db, kuwait_now_iso, normalize_roles, normalize_sites

VALID_ACTIONS = {"REQUEST", "APPROVE", "CLOSE"}
STATE_SEQUENCE = {"NEW": "REQUESTED", "REQUESTED": "APPROVED", "APPROVED": "CLOSED"}


def _normalize_role(raw: str | None) -> str:
    return (raw or "").strip().upper().replace(" ", "_")


def _is_active_user(user_row: sqlite3.Row | None) -> bool:
    return bool(user_row and user_row["active"] == "Y")


def _has_role(user_row: sqlite3.Row | None, required_role: str) -> bool:
    if not user_row:
        return False
    roles = normalize_roles(user_row["roles"])
    return required_role in roles


def _actor_role(user_row: sqlite3.Row | None, required_role: str) -> str:
    if not user_row:
        return "UNKNOWN"
    roles = normalize_roles(user_row["roles"])
    return required_role if required_role in roles else (roles[0] if roles else "UNKNOWN")


def _is_user_for_site(user_row: sqlite3.Row | None, site_id: str) -> bool:
    if not user_row:
        return False
    sites = normalize_sites(user_row["sites"])
    return "ALL" in sites or site_id in sites


def _site_has_active_area_authority(conn: sqlite3.Connection, site_id: str) -> bool:
    authorities = conn.execute("SELECT * FROM users WHERE active = 'Y'").fetchall()
    return any(
        _has_role(user, "AREA_AUTHORITY") and _is_user_for_site(user, site_id)
        for user in authorities
    )


def _permit_exists(conn: sqlite3.Connection, permit_id: int) -> sqlite3.Row | None:
    return conn.execute("SELECT * FROM permits WHERE permit_id = ?", (permit_id,)).fetchone()


def _record_history(conn: sqlite3.Connection, permit_id: int, action: str, from_state: str, to_state: str, user_id: str, actor_role: str, success: bool, check_id: str | None, comment: str) -> None:
    conn.execute(
        """
        INSERT INTO permit_history (
            permit_id, action, from_state, to_state, user_id, actor_role, timestamp, success, check_id, comment
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (permit_id, action, from_state, to_state, user_id, actor_role, kuwait_now_iso(), 1 if success else 0, check_id, comment),
    )


def _serialize_permit(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "permit_id": row["permit_id"],
        "permit_ref": row["permit_ref"],
        "requested_by": row["requested_by"],
        "site_id": row["site_id"],
        "permit_type_id": row["permit_type_id"],
        "work_description": row["work_description"],
        "valid_from": row["valid_from"],
        "valid_to": row["valid_to"],
        "hazards": row["hazards"],
        "controls": row["controls"],
        "status": row["status"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def _serialize_history(rows: list[sqlite3.Row]) -> list[dict[str, Any]]:
    out = []
    for row in rows:
        out.append(
            {
                "history_id": row["history_id"],
                "permit_id": row["permit_id"],
                "action": row["action"],
                "from_state": row["from_state"],
                "to_state": row["to_state"],
                "user_id": row["user_id"],
                "actor_role": row["actor_role"],
                "timestamp": row["timestamp"],
                "success": bool(row["success"]),
                "check_id": row["check_id"],
                "comment": row["comment"],
            }
        )
    return out


def _normalize_datetime(value: str) -> str:
    if not value:
        return value
    try:
        dt = datetime.fromisoformat(value)
    except ValueError:
        return value
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone(timedelta(hours=3)))
    return dt.isoformat()


def list_users() -> list[dict[str, Any]]:
    with connect_db() as conn:
        rows = conn.execute("SELECT * FROM users ORDER BY user_id").fetchall()
        return [dict(row) for row in rows]


def list_permits(site: str | None = None, status: str | None = None) -> list[dict[str, Any]]:
    with connect_db() as conn:
        query = "SELECT * FROM permits"
        clauses = []
        params: list[Any] = []
        if site:
            clauses.append("site_id = ?")
            params.append(site)
        if status:
            clauses.append("status = ?")
            params.append(status)
        if clauses:
            query += " WHERE " + " AND ".join(clauses)
        query += " ORDER BY created_at DESC"
        rows = conn.execute(query, tuple(params)).fetchall()
        return [_serialize_permit(row) for row in rows]


def get_permit(permit_id: int) -> dict[str, Any] | None:
    with connect_db() as conn:
        row = _permit_exists(conn, permit_id)
        return _serialize_permit(row) if row else None


def get_permit_history(permit_id: int) -> list[dict[str, Any]]:
    with connect_db() as conn:
        rows = conn.execute(
            "SELECT * FROM permit_history WHERE permit_id = ? ORDER BY history_id ASC",
            (permit_id,),
        ).fetchall()
        return _serialize_history(rows)


def create_request(payload: dict[str, Any]) -> dict[str, Any]:
    requested_by = str(payload.get("requested_by", "")).strip()
    site_id = str(payload.get("site_id", "")).strip()
    permit_type_id = str(payload.get("permit_type_id", "")).strip()
    work_description = str(payload.get("work_description", "")).strip()
    valid_from = str(payload.get("valid_from", "")).strip()
    valid_to = str(payload.get("valid_to", "")).strip()
    hazards = str(payload.get("hazards", "")).strip()
    controls = str(payload.get("controls", "")).strip()

    if not requested_by or not site_id or not permit_type_id or not work_description:
        return {"success": False, "error": {"code": "INVALID_REQUEST", "message": "Missing required request fields."}}

    with connect_db() as conn:
        user = conn.execute("SELECT * FROM users WHERE user_id = ?", (requested_by,)).fetchone()
        if not _is_active_user(user):
            return {"success": False, "error": {"code": "ROLE_REQUIRED", "message": f"{requested_by} is not an active user."}}
        if not _has_role(user, "REQUESTER"):
            return {"success": False, "error": {"code": "ROLE_REQUIRED", "message": f"{requested_by} does not hold the REQUESTER role."}}
        if not _is_user_for_site(user, site_id):
            return {"success": False, "error": {"code": "SITE_ASSIGNMENT", "message": f"{requested_by} is not assigned to site {site_id}."}}

        permit_type = conn.execute("SELECT * FROM permit_types WHERE permit_type_id = ?", (permit_type_id,)).fetchone()
        if permit_type is None:
            return {"success": False, "error": {"code": "INVALID_REQUEST", "message": f"Unknown permit type {permit_type_id}."}}

        valid_from = _normalize_datetime(valid_from)
        valid_to = _normalize_datetime(valid_to)
        try:
            from_dt = datetime.fromisoformat(valid_from)
            to_dt = datetime.fromisoformat(valid_to)
        except ValueError:
            return {"success": False, "error": {"code": "INVALID_REQUEST", "message": "valid_from and valid_to must be valid ISO-8601 timestamps."}}
        if to_dt < from_dt:
            return {"success": False, "error": {"code": "INVALID_REQUEST", "message": f"valid_to {valid_to} is before valid_from {valid_from}."}}

        permit_ref = f"P-{int(conn.execute('SELECT COALESCE(MAX(permit_id),0) + 1 FROM permits').fetchone()[0]):04d}"
        requested_at = kuwait_now_iso()
        conn.execute(
            """
            INSERT INTO permits (
                permit_ref, requested_by, site_id, permit_type_id, work_description,
                valid_from, valid_to, hazards, controls, status, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'REQUESTED', ?, ?)
            """,
            (
                permit_ref,
                requested_by,
                site_id,
                permit_type_id,
                work_description,
                valid_from,
                valid_to,
                hazards,
                controls,
                requested_at,
                requested_at,
            ),
        )
        permit_id = conn.execute("SELECT permit_id FROM permits WHERE permit_ref = ?", (permit_ref,)).fetchone()[0]
        _record_history(conn, permit_id, "REQUEST", "NEW", "REQUESTED", requested_by, "REQUESTER", True, "WORKFLOW", "Permit requested")
        row = conn.execute("SELECT * FROM permits WHERE permit_id = ?", (permit_id,)).fetchone()
        return {"success": True, "permit": _serialize_permit(row)}


def attempt_action(permit_id: int, action: str, user_id: str, comment: str = "") -> dict[str, Any]:
    action_name = action.upper()
    if action_name not in {"APPROVE", "CLOSE"}:
        return {"success": False, "error": {"code": "INVALID_TRANSITION", "message": f"Unsupported action {action_name}."}}

    with connect_db() as conn:
        permit = _permit_exists(conn, permit_id)
        if permit is None:
            return {"success": False, "error": {"code": "INVALID_REQUEST", "message": f"Permit {permit_id} does not exist."}}

        user = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
        actor_role = _actor_role(user, "AREA_AUTHORITY")
        current_status = permit["status"]
        if action_name == "APPROVE" and current_status != "REQUESTED":
            message = f"Permit {permit_id} is in {current_status}, so it cannot be approved."
            _record_history(conn, permit_id, action_name, current_status, current_status, user_id, actor_role, False, "INVALID_TRANSITION", message)
            return {"success": False, "error": {"code": "INVALID_TRANSITION", "message": message}}
        if action_name == "CLOSE" and current_status != "APPROVED":
            message = f"Permit {permit_id} is in {current_status}, so it cannot be closed."
            _record_history(conn, permit_id, action_name, current_status, current_status, user_id, actor_role, False, "INVALID_TRANSITION", message)
            return {"success": False, "error": {"code": "INVALID_TRANSITION", "message": message}}

        if not _is_active_user(user):
            message = f"{user_id} is not an active user."
            _record_history(conn, permit_id, action_name, current_status, current_status, user_id, actor_role, False, "ROLE_REQUIRED", message)
            return {"success": False, "error": {"code": "ROLE_REQUIRED", "message": message}}
        if not _has_role(user, "AREA_AUTHORITY"):
            message = f"{user_id} does not hold the AREA_AUTHORITY role."
            _record_history(conn, permit_id, action_name, current_status, current_status, user_id, actor_role, False, "ROLE_REQUIRED", message)
            return {"success": False, "error": {"code": "ROLE_REQUIRED", "message": message}}
        if not _site_has_active_area_authority(conn, permit["site_id"]):
            message = f"No active AREA_AUTHORITY is assigned to site {permit['site_id']}."
            _record_history(conn, permit_id, action_name, current_status, current_status, user_id, actor_role, False, "ROLE_REQUIRED", message)
            return {"success": False, "error": {"code": "ROLE_REQUIRED", "message": message}}
        if not _is_user_for_site(user, permit["site_id"]):
            message = f"{user_id} is not assigned to site {permit['site_id']}."
            _record_history(conn, permit_id, action_name, current_status, current_status, user_id, actor_role, False, "SITE_ASSIGNMENT", message)
            return {"success": False, "error": {"code": "SITE_ASSIGNMENT", "message": message}}
        if permit["requested_by"] == user_id:
            message = f"{user_id} requested this permit, so {user_id} can't {action_name.lower()} it."
            _record_history(conn, permit_id, action_name, current_status, current_status, user_id, actor_role, False, "SEPARATION_OF_DUTIES", message)
            return {"success": False, "error": {"code": "SEPARATION_OF_DUTIES", "message": message}}

        target_status = "APPROVED" if action_name == "APPROVE" else "CLOSED"
        conn.execute(
            "UPDATE permits SET status = ?, updated_at = ? WHERE permit_id = ?",
            (target_status, kuwait_now_iso(), permit_id),
        )
        _record_history(conn, permit_id, action_name, current_status, target_status, user_id, actor_role, True, "WORKFLOW", comment or f"Permit {action_name.lower()}d")
        row = conn.execute("SELECT * FROM permits WHERE permit_id = ?", (permit_id,)).fetchone()
        return {"success": True, "permit": _serialize_permit(row)}
