from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, List

import psycopg2
from psycopg2.extras import execute_values

from agents.role_selector import CandidateAssignment
from agents.resume_reader import Resume


class DBStoreAgent:
    def __init__(self) -> None:
        self.host = os.getenv("DB_HOST")
        self.port = int(os.getenv("DB_PORT", "5432"))
        self.dbname = os.getenv("DB_NAME")
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASS")
        self.schema = os.getenv("DB_SCHEMA", "public")
        self.enabled = bool(self.host and self.dbname and self.user and self.password)

        if self.enabled:
            self._ensure_tables()

    def _connect(self):
        if not self.enabled:
            raise RuntimeError("Postgres configuration is missing or incomplete.")
        return psycopg2.connect(
            host=self.host,
            port=self.port,
            dbname=self.dbname,
            user=self.user,
            password=self.password,
        )

    def _ensure_tables(self) -> None:
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"CREATE SCHEMA IF NOT EXISTS {self.schema};"
                )
                cur.execute(
                    f"CREATE TABLE IF NOT EXISTS {self.schema}.potential_candidates ("
                    "id TEXT PRIMARY KEY,"
                    "name TEXT,"
                    "email TEXT,"
                    "source TEXT,"
                    "score INTEGER,"
                    "role TEXT,"
                    "valid BOOLEAN,"
                    "validation_notes TEXT,"
                    "reasoning TEXT,"
                    "stored_at TIMESTAMPTZ,"
                    "metadata JSONB"
                    ");"
                )
                cur.execute(
                    f"CREATE TABLE IF NOT EXISTS {self.schema}.hired_candidates ("
                    "id TEXT PRIMARY KEY,"
                    "name TEXT,"
                    "email TEXT,"
                    "role TEXT,"
                    "score INTEGER,"
                    "reasoning TEXT,"
                    "source TEXT,"
                    "stored_at TIMESTAMPTZ,"
                    "metadata JSONB"
                    ");"
                )
            conn.commit()

    def store_potential_candidates(self, resumes: List[Resume]) -> None:
        if not self.enabled:
            return

        rows = [self._build_candidate_row(resume) for resume in resumes]
        self._upsert_rows(f"potential_candidates", rows)

    def store_hired_candidate(self, assignment: CandidateAssignment) -> None:
        if not self.enabled:
            return

        row = self._build_assignment_row(assignment)
        self._upsert_rows(f"hired_candidates", [row])

    def _build_candidate_row(self, resume: Resume) -> tuple:
        return (
            resume.id,
            resume.name,
            resume.email,
            resume.source,
            resume.score,
            resume.assigned_role,
            resume.valid,
            resume.validation_notes,
            resume.reasoning,
            datetime.utcnow(),
            json.dumps({"stored_by": "ai_resume_screener"}),
        )

    def _build_assignment_row(self, assignment: CandidateAssignment) -> tuple:
        return (
            assignment.resume.id,
            assignment.resume.name,
            assignment.resume.email,
            assignment.role,
            assignment.score,
            assignment.reasoning,
            assignment.resume.source,
            datetime.utcnow(),
            json.dumps({"stored_by": "ai_resume_screener"}),
        )

    def _upsert_rows(self, table: str, rows: Iterable[tuple]) -> None:
        if not rows:
            return

        columns = (
            "id, name, email, source, score, role, valid, validation_notes, reasoning, stored_at, metadata"
            if table == "potential_candidates"
            else "id, name, email, role, score, reasoning, source, stored_at, metadata"
        )
        update_cols = (
            "name = EXCLUDED.name, email = EXCLUDED.email, source = EXCLUDED.source, score = EXCLUDED.score,"
            " role = EXCLUDED.role, valid = EXCLUDED.valid, validation_notes = EXCLUDED.validation_notes, reasoning = EXCLUDED.reasoning,"
            " stored_at = EXCLUDED.stored_at, metadata = EXCLUDED.metadata"
            if table == "potential_candidates"
            else "name = EXCLUDED.name, email = EXCLUDED.email, role = EXCLUDED.role, score = EXCLUDED.score, reasoning = EXCLUDED.reasoning,"
            " source = EXCLUDED.source, stored_at = EXCLUDED.stored_at, metadata = EXCLUDED.metadata"
        )

        query = (
            f"INSERT INTO {self.schema}.{table} ({columns}) VALUES %s "
            f"ON CONFLICT (id) DO UPDATE SET {update_cols};"
        )

        with self._connect() as conn:
            with conn.cursor() as cur:
                execute_values(cur, query, rows)
            conn.commit()
