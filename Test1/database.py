import sqlite3


class WorkbookDB:
    def __init__(self, db_name="logic_workbook.db"):
        self.db_name = db_name
        self.init_db()

    def get_connection(self):
        # В Streamlit важно открывать соединение в том же потоке, где идет запрос
        return sqlite3.connect(self.db_name, check_same_thread=False)

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    score INTEGER DEFAULT 0
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS progress (
                    username TEXT,
                    task_id INTEGER,
                    code TEXT,
                    solved INTEGER,
                    PRIMARY KEY (username, task_id)
                )
            """)
            conn.commit()

    def register_user(self, username):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO users (username, score) VALUES (?, 0)", (username,))
            conn.commit()

    def get_leaders(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT username, score FROM users ORDER BY score DESC")
            return cursor.fetchall()

    def get_task_progress(self, username, task_id, default_code=""):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT code, solved FROM progress WHERE username = ? AND task_id = ?", (username, task_id))
            res = cursor.fetchone()
            if res:
                # ВАЖНО: берем первый элемент [0] для кода и второй [1] для статуса решения
                return {"code": res[0], "solved": bool(res[1])}
            return {"code": default_code, "solved": False}

    def save_progress(self, username, task_id, code, is_solved):
        solved_int = 1 if is_solved else 0
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO progress (username, task_id, code, solved) 
                VALUES (?, ?, ?, ?)
                ON CONFLICT(username, task_id) DO UPDATE SET code=excluded.code, solved=excluded.solved
            """, (username, task_id, code, solved_int))

            # Пересчитываем очки (10 XP за каждую решенную задачу)
            cursor.execute("SELECT COUNT(*) FROM progress WHERE username = ? AND solved = 1", (username,))
            solved_count = cursor.fetchone()[0]
            cursor.execute("UPDATE users SET score = ? WHERE username = ?", (solved_count * 10, username))
            conn.commit()
