import streamlit as st
from database import WorkbookDB
from tasks import TASKS_REPOSITORY, TaskChecker


class StreamlitWorkbookApp:
    def __init__(self):
        self.db = WorkbookDB()
        self.tasks = TASKS_REPOSITORY
        self.init_styles()

    def init_styles(self):
        st.set_page_config(page_title="Логика на Яблоках 🍎", page_icon="🍏", layout="centered")
        st.markdown("""
            <style>
            .stApp { background-color: #1E352F; color: #F4F9F4; }
            h1, h2, h3 { color: #FF6B6B !important; font-family: 'Comic Sans MS', sans-serif; }
            .stButton>button { background-color: #4E9F3D; color: white; border-radius: 12px; font-weight: bold; padding: 10px 24px; }
            .stButton>button:hover { background-color: #D8E9A8; color: #1E352F; }
            .task-card { background-color: #2E4C43; padding: 20px; border-radius: 15px; border-left: 5px solid #FF6B6B; margin-bottom: 20px; }
            .hint-card { background-color: #3E6358; padding: 12px; border-radius: 8px; border-left: 4px solid #D8E9A8; }
            </style>
        """, unsafe_allow_html=True)

    def render_sidebar(self, username):
        st.sidebar.header(f"👾 Игрок: {username}")
        if st.sidebar.button("Выйти / Сменить игрока 🔄"):
            st.session_state["username"] = ""
            st.rerun()

        st.sidebar.markdown("""
        ### 📜 Шпаргалка по яблокам:
        * **`and` (И)** — Съем, если **красное И сладкое**. (Нужны ОБА «да»)
        * **`or` (ИЛИ)** — Положу в корзину, если **красное ИЛИ зелёное**. (Хватит ОДНОГО «да»)
        * **`not` (НЕ)** — Съем, если **НЕ червивое**. (Переворачивает ответ)
        """)

        st.sidebar.markdown("---")
        st.sidebar.subheader("🏆 Таблица Лидеров")

        # Получаем данные рейтинга через объект базы данных
        leaders = self.db.get_leaders()
        for idx, leader in enumerate(leaders, 1):
            l_name, l_score = leader
            prefix = "⭐ " if l_name == username else f"{idx}. "
            st.sidebar.markdown(f"**{prefix}{l_name}** — `{l_score} XP` 🍏")

    def run(self):
        st.title("🍎 Рабочая тетрадь: Логические операторы")
        st.caption("Прокачай своего героя знаниями Python! Изучаем: **and, or, not**")

        if "username" not in st.session_state:
            st.session_state["username"] = ""

        # Окно авторизации
        if not st.session_state["username"]:
            st.subheader("🎮 Вход в игру")
            name_input = st.text_input("Введи своё имя или игровой ник:", placeholder="Например, PythonPro_13")
            if st.button("Начать приключение 🚀"):
                if name_input.strip():
                    username = name_input.strip()
                    st.session_state["username"] = username
                    self.db.register_user(username)
                    st.rerun()
                else:
                    st.warning("Имя не может быть кем-то пустым!")
            return

        username = st.session_state["username"]
        self.render_sidebar(username)

        # Выбор режима работы
        menu = ["📚 Теория на яблоках", "📝 Решать задания"]
        choice = st.radio("Куда отправимся?", menu, horizontal=True)

        if choice == "📚 Теория на яблоках":
            self.render_theory()
        elif choice == "📝 Решать задания":
            self.render_tasks_interface(username)

    def render_theory(self):
        st.subheader("🍏 Как работают операторы?")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.error("**and (И)**")
            st.write("Нужны оба условия. Дверь в данж откроется, если есть ключ И герой жив.")
        with col2:
            st.success("**or (ИЛИ)**")
            st.write("Хватит одного любого «да». Выдержишь удар, если есть щит ИЛИ здоровья больше 50.")
        with col3:
            st.warning("**not (НЕ)**")
            st.write("Делает наоборот. `not has_shield` превратит отсутствие защиты в истину.")

    def render_tasks_interface(self, username):
        if "current_task_index" not in st.session_state:
            st.session_state["current_task_index"] = 0

        # Память для сохранения результатов проверки текущей задачи
        if "check_results" not in st.session_state:
            st.session_state["check_results"] = {}

        task_titles = [t.title for t in self.tasks]
        selected_title = st.selectbox(
            "Выбери задание для взлома:",
            task_titles,
            index=st.session_state["current_task_index"]
        )

        # Обработка ручного переключения выпадающего списка
        task_id_changed = task_titles.index(selected_title)
        if task_id_changed != st.session_state["current_task_index"]:
            st.session_state["current_task_index"] = task_id_changed
            st.rerun()

        task = self.tasks[st.session_state["current_task_index"]]

        # 💾 Загрузка прогресса из ООП-модели БД
        progress = self.db.get_task_progress(username, task.id, default_code=task.setup)
        user_code = st.text_area("Напиши код на Python:", value=progress["code"], height=150, key=f"editor_{task.id}")

        is_solved = progress["solved"]

        st.markdown(f"<div class='task-card'><h3>{task.title}</h3><p>{task.desc}</p></div>", unsafe_allow_html=True)
        with st.expander("💡 Взять подсказку-помощник"):
            st.markdown(f"<div class='hint-card'>{task.hint}</div>", unsafe_allow_html=True)

        # Кнопка проверки
        if st.button("🚀 Проверить код"):
            # Запускаем проверку кода через TaskChecker
            success, console_out, error_msg = TaskChecker.run_and_check(task, user_code)

            # Сохраняем результаты в память сессии, чтобы они не стерлись при обновлении страницы
            st.session_state["check_results"][task.id] = {
                "success": success,
                "console_out": console_out,
                "error_msg": error_msg
            }

            # Если решено верно, сохраняем в базу данных
            if success:
                self.db.save_progress(username, task.id, user_code, is_solved=True)
                st.balloons()
            else:
                self.db.save_progress(username, task.id, user_code, is_solved=False)

            # Мягко обновляем страницу для перерисовки рейтинга в сайдбаре
            st.rerun()

        # --- ОТРИСОВКА КОНСОЛИ И ВЕРДИКТОВ (Вынесено из-за кнопки, теперь не исчезает!) ---
        if task.id in st.session_state["check_results"]:
            result = st.session_state["check_results"][task.id]

            st.markdown("### 💻 Консоль вывода:")
            if result["console_out"]:
                st.code(result["console_out"], language="python")
            else:
                st.caption("*Консоль пуста (нет вывода команды print)*")

            if result["success"]:
                st.success("🎉 ВЕРНО! Задание выполнено на отлично!")
                is_solved = True
            else:
                st.error(result["error_msg"])
                is_solved = False

        # Кнопка перехода к следующему шагу (появляется строго под консолью и вердиктом)
        if is_solved and st.session_state["current_task_index"] < len(self.tasks) - 1:
            st.markdown("---")
            if st.button("➡️ Следующее задание"):
                st.session_state["current_task_index"] += 1
                st.rerun()

# Точка входа в программу
if __name__ == "__main__":
    app = StreamlitWorkbookApp()
    app.run()
