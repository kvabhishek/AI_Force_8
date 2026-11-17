from __future__ import annotations

import csv
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DB_PATH = ROOT / "permit_work.db"
KUWAIT_TIMEZONE = timezone(timedelta(hours=3))


def kuwait_now_iso() -> str:
    return datetime.now(KUWAIT_TIMEZONE).isoformat(timespec="seconds")


def connect_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def load_csv_records(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def normalize_roles(raw: str | None) -> list[str]:
    if not raw:
        return []
    return [piece.strip().upper().replace(" ", "_") for piece in raw.split("|") if piece.strip()]


def normalize_sites(raw: str | None) -> list[str]:
    if not raw:
        return []
    return [piece.strip() for piece in raw.split("|") if piece.strip()]


def reset_database() -> None:
    with connect_db() as conn:
        conn.execute("DROP TRIGGER IF EXISTS permit_history_prevent_update")
        conn.execute("DROP TRIGGER IF EXISTS permit_history_prevent_delete")
        conn.execute("DELETE FROM permit_history")
        conn.execute("DELETE FROM permits")
        conn.execute("DELETE FROM sqlite_sequence WHERE name IN ('permits', 'permit_history')")
    initialize_database()


def initialize_database() -> None:
    with connect_db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS roles (
                role_id TEXT PRIMARY KEY,
                name TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sites (
                site_id TEXT PRIMARY KEY,
                site_name TEXT NOT NULL,
                area TEXT NOT NULL,
                hazardous_zone TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS permit_types (
                permit_type_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                risk_level TEXT NOT NULL,
                requires_hse_approval TEXT NOT NULL,
                requires_gas_test TEXT NOT NULL,
                max_validity_hours INTEGER NOT NULL,
                description TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                display_name TEXT NOT NULL,
                roles TEXT NOT NULL,
                sites TEXT NOT NULL,
                active TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS permits (
                permit_id INTEGER PRIMARY KEY AUTOINCREMENT,
                permit_ref TEXT UNIQUE NOT NULL,
                requested_by TEXT NOT NULL,
                site_id TEXT NOT NULL,
                permit_type_id TEXT NOT NULL,
                work_description TEXT NOT NULL,
                valid_from TEXT NOT NULL,
                valid_to TEXT NOT NULL,
                hazards TEXT NOT NULL,
                controls TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (requested_by) REFERENCES users(user_id),
                FOREIGN KEY (site_id) REFERENCES sites(site_id),
                FOREIGN KEY (permit_type_id) REFERENCES permit_types(permit_type_id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS permit_history (
                history_id INTEGER PRIMARY KEY AUTOINCREMENT,
                permit_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                from_state TEXT NOT NULL,
                to_state TEXT NOT NULL,
                user_id TEXT NOT NULL,
                actor_role TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                success INTEGER NOT NULL,
                check_id TEXT,
                comment TEXT NOT NULL,
                FOREIGN KEY (permit_id) REFERENCES permits(permit_id)
            )
            """
        )
        conn.execute(
            """
            CREATE TRIGGER IF NOT EXISTS permit_history_prevent_update
            BEFORE UPDATE ON permit_history
            BEGIN
                SELECT RAISE(ABORT, 'permit history is append-only');
            END
            """
        )
        conn.execute(
            """
            CREATE TRIGGER IF NOT EXISTS permit_history_prevent_delete
            BEFORE DELETE ON permit_history
            BEGIN
                SELECT RAISE(ABORT, 'permit history is append-only');
            END
            """
        )

        if conn.execute("SELECT COUNT(*) FROM roles").fetchone()[0] == 0:
            for row in load_csv_records(DATA_DIR / "roles.csv"):
                conn.execute(
                    "INSERT INTO roles (role_id, name) VALUES (?, ?)",
                    (row["role_id"].strip().upper(), row["name"].strip()),
                )

        if conn.execute("SELECT COUNT(*) FROM sites").fetchone()[0] == 0:
            for row in load_csv_records(DATA_DIR / "sites.csv"):
                conn.execute(
                    "INSERT INTO sites (site_id, site_name, area, hazardous_zone) VALUES (?, ?, ?, ?)",
                    (row["site_id"].strip(), row["site_name"].strip(), row["area"].strip(), row["hazardous_zone"].strip()),
                )

        if conn.execute("SELECT COUNT(*) FROM permit_types").fetchone()[0] == 0:
            for row in load_csv_records(DATA_DIR / "permit_types.csv"):
                conn.execute(
                    "INSERT INTO permit_types (permit_type_id, name, risk_level, requires_hse_approval, requires_gas_test, max_validity_hours, description) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (
                        row["permit_type_id"].strip(),
                        row["name"].strip(),
                        row["risk_level"].strip(),
                        row["requires_hse_approval"].strip(),
                        row["requires_gas_test"].strip(),
                        int(row["max_validity_hours"]),
                        row["description"].strip(),
                    ),
                )

        if conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
            for row in load_csv_records(DATA_DIR / "users.csv"):
                conn.execute(
                    "INSERT INTO users (user_id, display_name, roles, sites, active) VALUES (?, ?, ?, ?, ?)",
                    (
                        row["user_id"].strip(),
                        row["display_name"].strip(),
                        row["roles"].strip(),
                        row["sites"].strip(),
                        row["active"].strip(),
                    ),
                )

        if conn.execute("SELECT COUNT(*) FROM permits").fetchone()[0] == 0:
            seed_rows = [
                {
                    "permit_ref": "P-1001",
                    "requested_by": "U-001",
                    "site_id": "GC-01",
                    "permit_type_id": "HOT_WORK",
                    "work_description": "Weld a new pipe support on the inlet manifold",
                    "valid_from": "2026-11-15T07:30:00+03:00",
                    "valid_to": "2026-11-15T14:30:00+03:00",
                    "hazards": "Flammable gas; sparks; hot surfaces",
                    "controls": "Gas test; fire watch; fire blanket; extinguisher at the work area",
                    "status": "REQUESTED",
                },
                {
                    "permit_ref": "P-1002",
                    "requested_by": "U-020",
                    "site_id": "TF-01",
                    "permit_type_id": "CONFINED_SPACE",
                    "work_description": "Enter the oil-water separator pit to clear sludge",
                    "valid_from": "2026-11-15T08:00:00+03:00",
                    "valid_to": "2026-11-15T14:00:00+03:00",
                    "hazards": "Toxic gas (H2S); low oxygen; engulfment",
                    "controls": "Gas test; personal gas monitors; standby attendant; rescue plan",
                    "status": "REQUESTED",
                },
                {
                    "permit_ref": "P-1003",
                    "requested_by": "U-023",
                    "site_id": "GC-02",
                    "permit_type_id": "HOT_WORK",
                    "work_description": "Cut out and replace a corroded drain line spool",
                    "valid_from": "2026-11-16T07:00:00+03:00",
                    "valid_to": "2026-11-16T14:00:00+03:00",
                    "hazards": "Flammable gas; sparks; hot surfaces",
                    "controls": "Drain and purge the line; gas test; fire watch",
                    "status": "APPROVED",
                    "reviewed_by": "U-010",
                    "approved_by": "U-005",
                },
            ]
            for row in seed_rows:
                if conn.execute("SELECT 1 FROM permits WHERE permit_ref = ?", (row["permit_ref"],)).fetchone():
                    continue
                seeded_at = kuwait_now_iso()
                conn.execute(
                    """
                    INSERT INTO permits (
                        permit_ref, requested_by, site_id, permit_type_id, work_description,
                        valid_from, valid_to, hazards, controls, status, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        row["permit_ref"],
                        row["requested_by"],
                        row["site_id"],
                        row["permit_type_id"],
                        row["work_description"],
                        row["valid_from"],
                        row["valid_to"],
                        row["hazards"],
                        row["controls"],
                        row["status"],
                        seeded_at,
                        seeded_at,
                    ),
                )
                permit_id = conn.execute("SELECT permit_id FROM permits WHERE permit_ref = ?", (row["permit_ref"],)).fetchone()[0]
                history_events = [
                    ("REQUEST", "NEW", "REQUESTED", row["requested_by"], "REQUESTER", "Permit requested"),
                ]
                if row["status"] in {"REVIEWED", "APPROVED", "CLOSED", "REJECTED"}:
                    history_events.append(
                        ("REVIEW", "REQUESTED", "REVIEWED", row.get("reviewed_by", "U-010"), "HSE_OFFICER", "Permit reviewed by HSE")
                    )
                if row["status"] in {"APPROVED", "CLOSED"}:
                    history_events.append(
                        ("APPROVE", "REVIEWED", "APPROVED", row["approved_by"], "AREA_AUTHORITY", "Permit approved by area authority")
                    )
                if row["status"] == "REJECTED":
                    history_events.append(
                        ("REJECT", "REQUESTED", "REJECTED", row.get("reviewed_by", "U-010"), "HSE_OFFICER", row["rejection_reason"])
                    )
                if row["status"] == "CLOSED":
                    history_events.append(
                        ("CLOSE", "APPROVED", "CLOSED", row["closed_by"], "AREA_AUTHORITY", "Work completed and permit closed")
                    )
                for action, from_state, to_state, actor_user_id, actor_role, comment in history_events:
                    conn.execute(
                        """
                        INSERT INTO permit_history (
                            permit_id, action, from_state, to_state, user_id, actor_role, timestamp, success, check_id, comment
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, 1, 'WORKFLOW', ?)
                        """,
                        (permit_id, action, from_state, to_state, actor_user_id, actor_role, seeded_at, comment),
                    )


def fetch_all(query: str, params: Iterable[Any] = ()) -> list[sqlite3.Row]:
    with connect_db() as conn:
        return conn.execute(query, tuple(params)).fetchall()
