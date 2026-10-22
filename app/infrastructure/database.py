import json
import sqlite3
from app.core.config import get_settings
from app.domain.schemas import InspectionResult

def connect() -> sqlite3.Connection:
    path = get_settings().database_path
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, timeout=10.0)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA busy_timeout = 5000")
    return connection

def initialize_database() -> None:
    with connect() as db:
        db.execute("PRAGMA journal_mode = WAL")
        db.executescript("""
            CREATE TABLE IF NOT EXISTS inspections (
                inspection_id TEXT PRIMARY KEY,
                product_type TEXT NOT NULL,
                camera_id TEXT NOT NULL,
                status TEXT NOT NULL,
                decision TEXT,
                model_name TEXT,
                model_version TEXT,
                captured_at TEXT NOT NULL,
                processing_ms REAL,
                error_code TEXT,
                payload_json TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS ix_inspections_captured_at ON inspections(captured_at);
            CREATE INDEX IF NOT EXISTS ix_inspections_camera_id ON inspections(camera_id);
        """)

def save_inspection(result: InspectionResult) -> None:
    payload = result.model_dump(mode="json")
    with connect() as db:
        db.execute("""
            INSERT INTO inspections (
                inspection_id, product_type, camera_id, status, decision, model_name,
                model_version, captured_at, processing_ms, error_code, payload_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            result.inspection_id, result.product_type, result.camera_id, result.status.value,
            result.decision.value if result.decision else None, result.model_name,
            result.model_version, result.captured_at.isoformat(), result.processing_ms,
            result.error_code, json.dumps(payload, ensure_ascii=False),
        ))

def get_inspection(inspection_id: str) -> InspectionResult | None:
    with connect() as db:
        row = db.execute("SELECT payload_json FROM inspections WHERE inspection_id = ?", (inspection_id,)).fetchone()
    if row is None:
        return None
    return InspectionResult.model_validate_json(row["payload_json"])
