"""Интеграция с SaaS-проверкой заданий MongoDB."""

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
EVENT_TYPE = "mongodb_assignment_check"
ALLOWED_TASKS = {"01", "02", "03", "04", "06", "07"}


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
    """Получить токен из переменных окружения или Secrets Streamlit."""
    token = os.getenv("GITHUB_TOKEN")
    if token:
        return token

    try:
        import streamlit as st

        token = st.secrets.get("GITHUB_TOKEN")
        return str(token) if token else None
    except Exception:
        return None


def _headers(token: str) -> dict:
    return {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def generate_submission_id(task_number: str) -> str:
    """Создать уникальный идентификатор отправки."""
    return f"task{task_number}-{uuid.uuid4().hex}"


def validate_solution(
    task_number: str | None,
    solution: str | None,
    max_length: int,
) -> str | None:
    """Проверить решение до отправки в SaaS."""
    if not task_number:
        return "Сначала выберите задание."

    if solution is None or not solution.strip():
        return "Решение не должно быть пустым."

    if len(solution) > max_length:
        return f"Решение превышает лимит в {max_length} символов."

    try:
        number = int(task_number)
    except (TypeError, ValueError):
        return "Некорректный номер задания."

    if f"{number:02d}" not in ALLOWED_TASKS:
        return "Такого задания нет."

    return None


def submit_solution(
    task_number: str,
    solution: str,
    student_id: str = "local",
    max_length: int = 4000,
) -> CheckResult:
    """Отправить решение на автоматическую проверку."""
    error = validate_solution(task_number, solution, max_length)
    if error:
        return CheckResult(
            CheckStatus.SUBMIT_ERROR,
            message=error,
        )

    token = _token()
    if not token:
        return CheckResult(
            CheckStatus.NOT_CONNECTED,
            message=(
                "Не настроено подключение к SaaS-проверке. "
                "Проверьте настройку TOKEN в Secrets приложения."
            ),
        )

    number = f"{int(task_number):02d}"
    submission_id = generate_submission_id(number)
    solution_b64 = base64.b64encode(
        solution.encode("utf-8")
    ).decode("ascii")

    payload = {
        "event_type": EVENT_TYPE,
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
            return CheckResult(
                CheckStatus.SUBMIT_ERROR,
                submission_id=submission_id,
                message=(
                    "Не удалось отправить решение в SaaS-проверку "
                    f"(HTTP {response.status_code}). "
                    f"{response.text[:300]}"
                ),
            )

        return CheckResult(
            CheckStatus.CHECKING,
            submission_id=submission_id,
            message=(
                "Решение отправлено. Ожидаем результат "
                "автоматической проверки."
            ),
        )

    except requests.RequestException as exc:
        return CheckResult(
            CheckStatus.SUBMIT_ERROR,
            submission_id=submission_id,
            message=f"Не удалось отправить решение: {exc}",
        )


def poll_check(submission_id: str) -> CheckResult:
    """Получить статус проверки конкретной отправки."""
    token = _token()

    if not token:
        return CheckResult(
            CheckStatus.NOT_CONNECTED,
            submission_id=submission_id,
            message=(
                "Нет подключения к SaaS-проверке. "
                "Проверьте настройку TOKEN."
            ),
        )

    url = f"{API}/repos/{REPOSITORY}/actions/runs"

    try:
        response = requests.get(
            url,
            headers=_headers(token),
            params={
                "event": "repository_dispatch",
                "per_page": 100,
            },
            timeout=20,
        )

        if response.status_code != 200:
            return CheckResult(
                CheckStatus.CHECK_ERROR,
                submission_id=submission_id,
                message=(
                    "Не удалось получить статус проверки "
                    f"(HTTP {response.status_code}). "
                    f"{response.text[:300]}"
                ),
            )

        runs = response.json().get("workflow_runs", [])

        # Workflow должен включать submission_id в run-name.
        matching_run = next(
            (
                run
                for run in runs
                if submission_id in str(run.get("display_title", ""))
                or submission_id in str(run.get("name", ""))
            ),
            None,
        )

        if matching_run is None:
            return CheckResult(
                CheckStatus.CHECKING,
                submission_id=submission_id,
                message=(
                    "Отправка принята. Проверка ожидает запуска "
                    "или ещё не появилась в списке запусков."
                ),
            )

        run_status = matching_run.get("status")
        conclusion = matching_run.get("conclusion")
        run_url = matching_run.get("html_url", "")

        if run_status != "completed":
            return CheckResult(
                CheckStatus.CHECKING,
                submission_id=submission_id,
                message="Решение проверяется. Пожалуйста, подождите.",
                raw=matching_run,
            )

        if conclusion == "success":
            return CheckResult(
                CheckStatus.PASS,
                submission_id=submission_id,
                message=" Тест пройден.",
                raw=matching_run,
            )

        if conclusion == "failure":
            return CheckResult(
                CheckStatus.FAIL,
                submission_id=submission_id,
                message=(
                    "Проверка завершилась с ошибкой: "
                    "решение не прошло тесты или произошла ошибка "
                    "при их выполнении."
                ).strip(),
                raw=matching_run,
            )

        return CheckResult(
            CheckStatus.CHECK_ERROR,
            submission_id=submission_id,
            message=(
                "Не удалось подтвердить результат проверки. "
                f"Статус завершения: {conclusion}. "
            ).strip(),
            raw=matching_run,
        )

    except (requests.RequestException, ValueError) as exc:
        return CheckResult(
            CheckStatus.CHECK_ERROR,
            submission_id=submission_id,
            message=f"Не удалось получить результат проверки: {exc}",
        )
