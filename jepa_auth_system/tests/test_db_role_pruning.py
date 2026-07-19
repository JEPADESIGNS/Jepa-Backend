import sqlite3
import unittest

import database.db as db_module


class DbRolePruningTests(unittest.TestCase):
    def test_prune_disallowed_roles_removes_project_references_too(self):
        conn = sqlite3.connect(':memory:')
        conn.execute('PRAGMA foreign_keys = ON')
        conn.executescript('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                role TEXT NOT NULL DEFAULT 'client'
            );

            CREATE TABLE projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_name TEXT NOT NULL,
                created_by INTEGER,
                FOREIGN KEY (created_by) REFERENCES users(id)
            );
        ''')
        conn.execute("INSERT INTO users (username, role) VALUES (?, ?)", ('legacy', 'manager'))
        user_id = conn.execute("SELECT id FROM users WHERE username = ?", ('legacy',)).fetchone()[0]
        conn.execute("INSERT INTO projects (project_name, created_by) VALUES (?, ?)", ('Legacy Project', user_id))

        deleted = db_module._prune_disallowed_roles(conn)

        self.assertEqual(deleted, 1)
        self.assertEqual(conn.execute("SELECT COUNT(*) FROM users").fetchone()[0], 0)
        self.assertEqual(conn.execute("SELECT COUNT(*) FROM projects").fetchone()[0], 0)

        conn.close()

    def test_prune_disallowed_roles_removes_orphaned_logs(self):
        conn = sqlite3.connect(':memory:')
        conn.execute('PRAGMA foreign_keys = ON')
        conn.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                role TEXT NOT NULL DEFAULT 'client'
            )
        ''')
        conn.execute('''
            CREATE TABLE logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        conn.execute('''
            CREATE TABLE notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                is_read INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        conn.execute('''
            CREATE TABLE otp_codes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                code TEXT NOT NULL,
                expires_at DATETIME NOT NULL,
                used INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        conn.execute("INSERT INTO users (username, role) VALUES (?, ?)", ('legacy', 'manager'))
        user_id = conn.execute("SELECT id FROM users WHERE username = ?", ('legacy',)).fetchone()[0]
        conn.execute("INSERT INTO logs (user_id, action) VALUES (?, ?)", (user_id, 'legacy action'))
        conn.execute("INSERT INTO notifications (user_id, title, message) VALUES (?, ?, ?)", (user_id, 'Notice', 'legacy'))
        conn.execute("INSERT INTO otp_codes (user_id, code, expires_at, used) VALUES (?, ?, ?, ?)", (user_id, '123456', '2026-01-01', 0))

        deleted = db_module._prune_disallowed_roles(conn)

        self.assertEqual(deleted, 1)
        self.assertEqual(conn.execute("SELECT COUNT(*) FROM users").fetchone()[0], 0)
        self.assertEqual(conn.execute("SELECT COUNT(*) FROM logs").fetchone()[0], 0)
        self.assertEqual(conn.execute("SELECT COUNT(*) FROM notifications").fetchone()[0], 0)
        self.assertEqual(conn.execute("SELECT COUNT(*) FROM otp_codes").fetchone()[0], 0)

        conn.close()


if __name__ == '__main__':
    unittest.main()
