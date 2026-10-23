"""Локальный MVP интерфейса MongoDB Практикума."""

from config import (
    APP_TITLE,
    APP_SUBTITLE,
    MAX_SOLUTION_LENGTH,
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
from services.checker import submit_solution, CheckStatus, poll_check
from tasks.task_descriptions import TASKS, get_task_by_number

import streamlit as st

st.set_page_config(page_title=APP_TITLE, layout="wide")

# --- Инициализация состояния интерфейса ---
if "selected_task_number" not in st.session_state:
    st.session_state.selected_task_number = TASKS[0]["number"]
if "status" not in st.session_state:
    st.session_state.status = STATUS_READY
if "result_message" not in st.session_state:
    st.session_state.result_message = None
if "submission_id" not in st.session_state:
    st.session_state.submission_id = None

# --- Шапка ---
st.title(APP_TITLE)
st.caption(APP_SUBTITLE)


# --- Выбор задания ---
task_numbers = [task["number"] for task in TASKS]
task_labels = {
    task["number"]: f"Task {task['number']} — {task['title']}" for task in TASKS
}
selected_index = task_numbers.index(st.session_state.selected_task_number)
selected_label = st.selectbox(
    "Выберите задание",
    options=[task_labels[number] for number in task_numbers],
    index=selected_index,
    key="task_selector",
)
selected_task_number = [
    number for number in task_numbers if task_labels[number] == selected_label
][0]

if selected_task_number != st.session_state.selected_task_number:
    st.session_state.selected_task_number = selected_task_number
    st.session_state.status = STATUS_READY
    st.session_state.result_message = None
    st.session_state.submission_id = None

task = get_task_by_number(st.session_state.selected_task_number)
if task is None:
    st.error("Выбранное задание не найдено. Обновите страницу.")
    st.stop()

st.subheader(f"Task {task['number']} — {task['title']}")
st.markdown(task["description"])
st.caption(f"Лимит длины решения: {MAX_SOLUTION_LENGTH} символов.")

# --- Поле решения ---
solution = st.text_area(
    "Введите решение в синтаксисе MongoDB Shell",
    key="solution_text",
    height=220,
    placeholder="db.students.find({}, { name: 1, age: 1 })",
)

def clear_solution():
    st.session_state.solution_text = ""
    st.session_state.status = STATUS_CLEARED
    st.session_state.result_message = "Решение очищено. Предыдущий результат больше не относится к текущей отправке."
    st.session_state.submission_id = None


# --- Действия ---
col_check, col_clear = st.columns(2)
check_clicked = col_check.button("Проверить решение", type="primary", use_container_width=True)
col_clear.button("Очистить решение", use_container_width=True, on_click=clear_solution)


def show_status(status: str, message: str | None) -> None:
    """Отобразить статус и безопасное сообщение."""
    if status in (STATUS_PASS,):
        st.success(status)
    elif status in (STATUS_FAIL,):
        st.error(status)
    elif status in (STATUS_SUBMIT_ERROR, STATUS_CHECK_ERROR):
        st.warning(status)
    else:
        st.info(status)
    if message:
        st.write(message)


if check_clicked:
    st.session_state.status = STATUS_SUBMITTING
    result = submit_solution(
        task_number=st.session_state.selected_task_number,
        solution=solution,
        student_id="local",
        max_length=MAX_SOLUTION_LENGTH,
    )
    st.session_state.status = result.status.value
    st.session_state.result_message = result.message
    st.session_state.submission_id = result.submission_id

# --- Статус и результат ---
st.divider()



if st.session_state.submission_id:
    st.caption(f"Идентификатор текущей отправки: {st.session_state.submission_id}")

# --- Явный индикатор рынка проверки; запрещаем локальный PASS ---
#if st.session_state.status == STATUS_PASS and not st.session_state.get("real_check_confirmed", False):
    #st.session_state.status = STATUS_NOT_CONNECTED
    #st.session_state.result_message = (
        #"Локальное PASS невозможно: автоматическая проверка не подключена. "
        #"Отправленное решение получит реальный результат только после настройки "
        #"GitHub Actions."
    #)
   # st.rerun()


# --- Автоматическое обновление результата SaaS-проверки ---
@st.fragment(run_every="3s")
def render_check_status():
    submission_id = st.session_state.submission_id
    current_status = st.session_state.status

    if submission_id and current_status == STATUS_CHECKING:
        polled = poll_check(submission_id)

        # Сохраняем актуальный статус, в том числе ошибки подключения.
        st.session_state.status = polled.status.value
        st.session_state.result_message = polled.message
        st.session_state.submission_id = (
            polled.submission_id or submission_id
        )

    st.subheader("Текущее состояние")
    show_status(
        st.session_state.status,
        st.session_state.result_message,
    )

    if st.session_state.submission_id:
        st.caption(
            f"Идентификатор текущей отправки: "
            f"{st.session_state.submission_id}"
        )


render_check_status()