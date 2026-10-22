"""GitHub Actions integration for MongoDB practice."""

import base64
import os
import uuid
from dataclasses import dataclass
from enum import Enum

import requests

from config import (
    STATUS_READY,
    STATUS_SUBMITTING,
    STATUS_SENT,
    STATUS_CHECKING,
    STATUS_PASS,
    STATUS_FAIL,
    STATUS_SUBMIT_ERROR,
    STATUS_CHECK_ERROR,
    STATUS_NOT_CONNECTED,
    STATUS_CLEARED,
)

API = "https://api.github.com"
REPOSITORY = os.getenv("GITHUB_REPOSITORY", "ninachekalina/data_course")


class CheckStatus(Enum):
    READY = STATUS_READY
    SUBMITTING = STATUS_SUBMITTING
    SENT = STATUS_SENT
    CHECKING = STATUS_CHECKING
    PASS = STATUS_PASS
    FAIL = STATUS_FAIL
    SUBMIT_ERROR = STATUS_SUBMIT_ERROR
    CHECK_ERROR = STATUS_CHECK_ERROR
    NOT_CONNECTED = STATUS_NOT_CONNECTED
    CLEARED = STATUS_CLEARED


@dataclass
class CheckResult:
    status: CheckStatus
    submission_id: str | None = None
    message: str | None = None
    raw: dict | None = None
    checks: list[dict] | None = None


def _token() -> str | None:
    token = os.getenv("GITHUB_TOKEN")
    if token:
        return token

    try:
        import streamlit as st
        return st.secrets.get("GITHUB_TOKEN")
    except Exception:
        return None


def _headers(token: str) -> dict:
    return {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def generate_submission_id(task_number: str) -> str:
    return f"task{task_number}-{uuid.uuid4().hex}"


def validate_solution(
    task_number: str | None,
    solution: str | None,
    max_length: int,
) -> str | None:
    if not task_number:
        return "Сначала выберите задание."
    if solution is None or not solution.strip():
        return "ешение не должно быть пустым."
    if len(solution) > max_length:
        return f"ешение превышает лимит в {max_length} символов."

    try:
        number = int(task_number)
    except (TypeError, ValueError):
        return "екорректный номер задания."

    if number not in {1, 2, 3, 4, 6, 7}:
        return "Такого задания нет."

    return None


def submit_solution(
    task_number: str,
    solution: str,
    student_id: str = "local",
    max_length: int = 4000,
) -> CheckResult:
    error = validate_solution(task_number, solution, max_length)
    if error:
        return CheckResult(CheckStatus.SUBMIT_ERROR, message=error)

    token = _token()
    if not token:
        return CheckResult(
            CheckStatus.NOT_CONNECTED,
            message=(
                "е настроен GITHUB_TOKEN. обавьте токен в Secrets "
                "приложения Streamlit."
            ),
        )

    number = f"{int(task_number):02d}"
    submission_id = generate_submission_id(number)
    solution_b64 = base64.b64encode(solution.encode("utf-8")).decode("ascii")

    payload = {
        "event_type": "mongodb_assignment_check",
        "client_payload": {
            "submission_id": submission_id,
            "task_number": number,
            "solution_b64": solution_b64,
        },
    }

    url = f"{API}/repos/{REPOSITORY}/dispatches"

    try:
        response = requests.post(
            url,
            headers=_headers(token),
            json=payload,
            timeout=20,
        )

        if response.status_code != 204:
            detail = response.text[:500]
            return CheckResult(
                CheckStatus.SUBMIT_ERROR,
                submission_id=submission_id,
                message=(
                    f"GitHub не принял отправку "
                    f"(HTTP {response.status_code}). {detail}"
                ),
            )

        return CheckResult(
            CheckStatus.CHECKING,
            submission_id=submission_id,
            message="ешение отправлено. жидаем завершения тестов GitHub Actions.",
        )

    except requests.RequestException as exc:
        return CheckResult(
            CheckStatus.SUBMIT_ERROR,
            submission_id=submission_id,
            message=f"е удалось связаться с GitHub: {exc}",
        )


def poll_check(submission_id: str) -> CheckResult:
    token = _token()
    if not token:
        return CheckResult(
            CheckStatus.NOT_CONNECTED,
            submission_id=submission_id,
            message="е настроен GITHUB_TOKEN.",
        )

    url = f"{API}/repos/{REPOSITORY}/actions/runs"

    try:
        response = requests.get(
            url,
            headers=_headers(token),
            params={"event": "repository_dispatch", "per_page": 100},
            timeout=20,
        )

        if response.status_code != 200:
            return CheckResult(
                CheckStatus.CHECK_ERROR,
                submission_id=submission_id,
                message=f"GitHub вернул HTTP {response.status_code}: {response.text[:300]}",
            )

        runs = response.json().get("workflow_runs", [])
        matching_run = next(
            (
                run for run in runs
                if submission_id in str(run.get("display_title", ""))
                or submission_id in str(run.get("name", ""))
            ),
            None,
        )

        if matching_run is None:
            return CheckResult(
                CheckStatus.CHECKING,
                submission_id=submission_id,
                message="GitHub получил отправку или ставит проверку в очередь.",
            )

        status = matching_run.get("status")
        conclusion = matching_run.get("conclusion")
        run_url = matching_run.get("html_url", "")

        if status != "completed":
            return CheckResult(
                CheckStatus.CHECKING,
                submission_id=submission_id,
                message=f"Тесты выполняются. {run_url}",
                raw=matching_run,
            )

        if conclusion == "success":
            return CheckResult(
                CheckStatus.PASS,
                submission_id=submission_id,
                message=f"се тесты пройдены. {run_url}",
                raw=matching_run,
            )

        if conclusion == "failure":
            return CheckResult(
                CheckStatus.FAIL,
                submission_id=submission_id,
                message=f"ешение не прошло тесты или произошла ошибка запуска. {run_url}",
                raw=matching_run,
            )

        return CheckResult(
            CheckStatus.CHECK_ERROR,
            submission_id=submission_id,
            message=f"роверка завершилась со статусом {conclusion}. {run_url}",
            raw=matching_run,
        )

    except (requests.RequestException, ValueError) as exc:
        return CheckResult(
            CheckStatus.CHECK_ERROR,
            submission_id=submission_id,
            message=f"е удалось получить результат проверки: {exc}",
        )
