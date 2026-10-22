"""Sanitized student-facing MongoDB task definitions.

Only task descriptions, collections and expected results are included here.
Reference solutions and example solutions from the checker repository are
intentionally excluded from the public frontend.
"""

TASKS: list[dict] = [
    {
        "number": "01",
        "title": "Найти всех студентов",
        "description": (
            "**Задача:** Найти все документы в коллекции students и вернуть все поля.\n\n"
            "**Коллекции:** `students`\n\n"
            "**Ожидаемый результат:** Вернуть все 5 документов студентов со всеми "
            "полями, включая `_id`, `name`, `age`, `major` и `address`."
        ),
    },
    {
        "number": "02",
        "title": "Найти студентов старше 21 года",
        "description": (
            "**Задача:** Найти всех студентов старше 21 года.\n\n"
            "**Коллекции:** `students`\n\n"
            "**Ожидаемый результат:** Должны быть возвращены 2 документа: "
            "Bob Smith (22 года) и David Brown (23 года)."
        ),
    },
    {
        "number": "03",
        "title": "Проекция: только имя и возраст",
        "description": (
            "**Задача:** Найти всех студентов, вернув только поля `name` и `age` "
            "(и поле `_id`, которое всегда включается, если не исключено).\n\n"
            "**Коллекции:** `students`\n\n"
            "**Ожидаемый результат:** Должны быть возвращены 5 документов, каждый "
            "содержит только поля `_id`, `name` и `age`."
        ),
    },
    {
        "number": "04",
        "title": "Обновить возраст студента",
        "description": (
            "**Задача:** Установить возраст студента по имени \"Alice Johnson\" = 21.\n\n"
            "**Коллекции:** `students`\n\n"
            "**Ожидаемый результат:** После обновления в документе студента "
            "Alice Johnson значение `age` должно быть 21."
        ),
    },
    {
        "number": "06",
        "title": "Удалить поле address",
        "description": (
            "**Задача:** Удалить поле `address` из документа студента по имени "
            "\"Alice Johnson\".\n\n"
            "**Коллекции:** `students`\n\n"
            "**Ожидаемый результат:** После обновления в документе Alice Johnson "
            "не должно быть поля `address`."
        ),
    },
    {
        "number": "07",
        "title": "Переименовать поле name в fullName",
        "description": (
            "**Задача:** Переименовать поле `name` в `fullName` в документе "
            "студента Alice Johnson.\n\n"
            "**Коллекции:** `students`\n\n"
            "**Ожидаемый результат:** После обновления документ Alice Johnson должен "
            "содержать поле `fullName` со значением \"Alice Johnson\" и не должен "
            "содержать поле `name`."
        ),
    },
]


def get_task_by_number(number: str):
    for task in TASKS:
        if task["number"] == number:
            return task
    return None