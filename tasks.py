import sys
import io


class Task:
    def __init__(self, task_id, title, desc, hint, setup, test_code):
        self.id = task_id
        self.title = title
        self.desc = desc
        self.hint = hint
        self.setup = setup
        self.test_code = test_code


class TaskChecker:
    @staticmethod
    def run_and_check(task: Task, user_code: str):
        """
        Запускает код пользователя, перехватывает вывод в консоль и проверяет тестами.
        Возвращает кортеж: (success: bool, output: str, error_message: str)
        """
        old_stdout = sys.stdout
        redirected_output = io.StringIO()
        sys.stdout = redirected_output

        error_msg = ""
        success = False
        captured_print = ""

        try:
            # 1. Запуск для живого вывода в консоль (как есть на экране)
            exec(user_code, {}, {})
            captured_print = redirected_output.getvalue().strip()

            # 2. Умное тестирование с подменой значений в тексте кода
            if task.id == 1:
                # Тест 1: на исходном коде (a = 7) -> должен выдать True
                buf1 = io.StringIO();
                sys.stdout = buf1
                exec(user_code, {}, {})
                res1 = buf1.getvalue().strip()

                # Тест 2: меняем в тексте a = 7 на a = 10 -> должен выдать False
                test_code2 = user_code.replace("a = 7", "a = 10").replace("a=7", "a=10")
                buf2 = io.StringIO();
                sys.stdout = buf2
                exec(test_code2, {}, {})
                res2 = buf2.getvalue().strip()

                assert "True" in res1 and "False" in res2

            elif task.id == 2:
                buf1 = io.StringIO();
                sys.stdout = buf1
                exec(user_code, {}, {})
                res1 = buf1.getvalue().strip()

                # Меняем значения на разную четность (3 и 8) -> False
                test_code2 = user_code.replace("a = 4", "a = 3").replace("b = 6", "b = 8")
                buf2 = io.StringIO();
                sys.stdout = buf2
                exec(test_code2, {}, {})
                res2 = buf2.getvalue().strip()

                assert "True" in res1 and "False" in res2

            elif task.id == 3:
                buf1 = io.StringIO();
                sys.stdout = buf1
                exec(user_code, {}, {})
                res1 = buf1.getvalue().strip()

                # Меняем все числа на отрицательные -> False
                test_code2 = user_code.replace("a = 5", "a = -1").replace("b = -2", "b = -2").replace("c = -7",
                                                                                                      "c = -3")
                buf2 = io.StringIO();
                sys.stdout = buf2
                exec(test_code2, {}, {})
                res2 = buf2.getvalue().strip()

                assert "True" in res1 and "False" in res2

            elif task.id == 4:
                buf1 = io.StringIO();
                sys.stdout = buf1
                exec(user_code, {}, {})
                res1 = buf1.getvalue().strip()

                # Меняем число на другое (105) -> должно вывести 5
                test_code2 = user_code.replace("num = 4837", "num = 105")
                buf2 = io.StringIO();
                sys.stdout = buf2
                exec(test_code2, {}, {})
                res2 = buf2.getvalue().strip()

                assert "7" in res1 and "5" in res2

            elif task.id == 5:
                buf1 = io.StringIO();
                sys.stdout = buf1
                exec(user_code, {}, {})
                res1 = buf1.getvalue().strip()

                # Меняем n = 6 на n = 2 (делится на 2, но меньше 4) -> False
                test_code2 = user_code.replace("n = 6", "n = 2")
                buf2 = io.StringIO();
                sys.stdout = buf2
                exec(test_code2, {}, {})
                res2 = buf2.getvalue().strip()

                assert "True" in res1 and "False" in res2

            elif task.id == 6:
                buf1 = io.StringIO();
                sys.stdout = buf1
                exec(user_code, {}, {})
                res1 = buf1.getvalue().strip()

                # Меняем щит на True (danger пропадет) -> False
                test_code2 = user_code.replace("has_shield = False", "has_shield = True")
                buf2 = io.StringIO();
                sys.stdout = buf2
                exec(test_code2, {}, {})
                res2 = buf2.getvalue().strip()

                assert "True" in res1 and "False" in res2

            success = True

        except SyntaxError as se:
            error_msg = f"Системная ошибка синтаксиса! Проверь скобки или двоеточия. Строка {se.lineno}."
        except AssertionError:
            error_msg = "Неверно! Ошибка в логике. Код выдает неправильный результат для некоторых тестов."
        except Exception as e:
            error_msg = f"Неверно! Ошибка во время выполнения: {str(e)}"
        finally:
            sys.stdout = old_stdout

        return success, captured_print, error_msg


# Список всех задач (теперь test_code пустые, так как проверки вынесены в чистый Python выше)
TASKS_REPOSITORY = [
    Task(
        task_id=1,
        title="🍏 Задание 1: Нечётное число",
        desc="Дано целое число `A`. Проверить высказывание: **«Число A является нечётным»**. Выведи `True` или `False`.",
        hint="Нечётное — это когда при делении на 2 остаётся 1 (`A % 2 == 1`). Или поставь перед проверкой чётного оператор `not`.",
        setup="a = 7\n# Напиши решение ниже\nprint(",
        test_code=""
    ),
    Task(
        task_id=2,
        title="🍏 Задание 2: Одинаковая чётность",
        desc="Даны два целых числа `A` и `B`. Проверить: **«Числа A и B имеют одинаковую чётность»**.",
        hint="Это значит «оба чётные» ИЛИ «оба нечётные». Собери каждую часть через `and`, а потом склей их через `or`: `(... and ...) or (... and ...)`",
        setup="a = 4\nb = 6\n# Напиши решение ниже\nprint(",
        test_code=""
    ),
    Task(
        task_id=3,
        title="🍏 Задание 3: Кто-то положительный?",
        desc="Даны три целых числа `A`, `B`, `C`. Проверить: **«Хотя бы одно из чисел A, B, C положительное»**.",
        hint="«Хотя бы одно» означает, что нам нужен оператор `or`. Сделай три маленькие проверки (`A > 0`, `B > 0`, `C > 0`) и соедини их.",
        setup="a = 5\nb = -2\nc = -7\n# Напиши решение ниже\nprint(",
        test_code=""
    ),
    Task(
        task_id=4,
        title="🍏 Задание 4: Последний герой",
        desc="Дано натуральное число. Выведи его **последнюю цифру**.",
        hint="Последняя цифра — это всегда остаток от деления числа на 10. Например, `275 % 10` даёт 5.",
        setup="num = 4837\n# Напиши решение ниже\nprint(",
        test_code=""
    ),
    Task(
        task_id=5,
        title="🍏 Задание 5: Делёжка яблок",
        desc="В корзине лежит `n` яблок. Проверить: **«Яблоки можно поровну поделить между двумя друзьями, И их не меньше 4»**.",
        hint="Нужно проверить два условия: делится на 2 без остатка (`n % 2 == 0`) и размер кучки (`n >= 4`). Соедини их через `and`!",
        setup="n = 6\n# Напиши решение ниже\nprint(",
        test_code=""
    ),
    Task(
        task_id=6,
        title="🍏 Задание 6: Опасность в игре!",
        desc="У героя есть здоровье `health` и щит `has_shield` (True или False). Проверить: **«Герой в опасности: здоровья меньше 20 И щита нет»**.",
        hint="«Щита нет» — это `not has_shield`. Вторая проверка: `health < 20`. Скрести их через `and`.",
        setup="health = 10\nhas_shield = False\n# Напиши решение ниже\nprint(",
        test_code=""
    )
]
