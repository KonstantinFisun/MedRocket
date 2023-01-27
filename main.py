import requests
import json
import os
import datetime


# Создание папки tasks
def check_exist_directory():
    path_tasks = os.getcwd() + r'\tasks'
    if not os.path.exists(path_tasks):
        os.makedirs(path_tasks)


# Если существует отчет, то переименовываем его
def check_exist_report(path, username):
    if os.path.exists(path):
        old_file = open(f'{path}', 'r')  # Открываем старый отчет
        old_file.readline()  # Пропускаем строку
        old_date = old_file.readline()[-17::].rstrip()  # Получаем дату отчета
        old_date = old_date.replace('.', '-')  # Меняем . на -
        old_date = old_date.replace(' ', 'T')  # Меняем _ на -
        old_date = old_date.replace(':', '-')  # Меняем : на -
        old_file.close()  # Закрываем файл
        new_path_user = "tasks\\old_" + username + "_" + old_date + ".txt"  # Новое имя отчета
        try:
            os.rename(path, new_path_user)  # Переименовываем
        except:
            print("Отчет уже создан с таким временем")

        return new_path_user


# Обрезка строки до 46 символов
def cropping_to_46(str):
    if len(str) > 46:
        return str[0:46] + "..."
    else:
        return str


# Проверка статуса подключения
def status_connect(response):
    if 200 > response.status_code > 300:
        print("Не удалось установить подключение")
        return False
    return True


def main():
    # Получение списка users
    response_users = requests.get("https://json.medrocket.ru/users")

    # Если не удалось установить подключения с users
    if not status_connect(response_users):
        return

    # Получение списка задач
    response_todos = requests.get("https://json.medrocket.ru/todos")

    # Если не удалось установить подключения с todos
    if not status_connect(response_todos):
        return

    # Извлекаем список users
    users = json.loads(response_users.text)

    # Извлекаем список задач
    todos = json.loads(response_todos.text)

    # Создание директории tasks
    check_exist_directory()

    # Обходим всех users
    for user in users:

        count_tasks = 0  # Общее количество задач
        count_current_tasks = 0  # Количество актуальных задач
        count_completed_tasks = 0  # Количество завершенных задач

        list_current_tasks = ""  # Список актуальных задач
        list_completed_tasks = ""  # Список завершенных задач

        # Обходим все задачи
        for task in todos:
            # Проверяем, что в задаче есть 4 пункта
            if len(task) != 4:
                continue

            if task["userId"] == user["id"]:
                count_tasks += 1
                if task["completed"]:
                    count_completed_tasks += 1
                    text_task = cropping_to_46(task["title"])
                    list_completed_tasks += "- " + text_task + "\n"
                else:
                    count_current_tasks += 1
                    text_task = cropping_to_46(task["title"])
                    list_current_tasks += "- " + text_task + "\n"

        path_user = "tasks\\" + user["username"] + ".txt"

        # Проверка существования актуального отчета
        new_path_user = check_exist_report(path_user, user["username"])
        try:
            # Создание txt файла юзера
            new_file = open(f'{path_user}', 'w')

            # Если у пользователя есть задачи
            if count_tasks > 0:
                new_file.write("# Отчёт для " + user["company"]["name"] + ".\n" + user["name"] + " <" + user["email"] + "> " + \
                           datetime.datetime.today().strftime("%d.%m.%Y %H:%M") + "\nВсего задач: " + str(count_tasks) + \
                           "\n\n" + "## Актуальные задачи (" + str(count_current_tasks) + "):\n" + list_current_tasks + \
                           "\n" + "## Завершённые задачи (" + str(count_completed_tasks) + "):\n" + list_completed_tasks)
            else:
                new_file.write(
                    "# Отчёт для " + user["company"]["name"] + ".\n" + user["name"] + " <" + user["email"] + "> " + \
                    datetime.datetime.today().strftime("%d.%m.%Y %H:%M") + "\nЗадачи отсутствуют")

            new_file.close()
        except OSError:
            os.rename(new_path_user, path_user)


if __name__ == '__main__':
    main()
