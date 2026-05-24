import sqlite3

class SqlDb(object):

    def __init__(self, db_path="db/app.db"):
        self.db_path = db_path
        self._create_tables()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _create_tables(self):
        conn = None
        cursor = None
        try:
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute("""BEGIN""")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL)
            """)
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error creating table: {e}")
        finally:
            if cursor: 
                cursor.close()
            if conn: 
                conn.close()

    def create_user(self, username, email):
        conn = None
        try:
            conn = self._connect()
            cursor = conn.cursor()
            password_hash = generate_password_hash(password)
            cursor.execute(
                "INSERT INTO users (username, email, password) VALUES (?, ?)",
                (username, email, password_hash)
            )
            conn.commit()
            user_id = cursor.lastrowid
            return {"id": user_id, "username": username, "email": email}
        except sqlite3.IntegrityError:
            print("Error: Username or email already exists.")
            return None
        except sqlite3.Error as e:
            print(f"Database error during user creation: {e}")
            return None
        finally:
            if cursor: 
                cursor.close()
            if conn: 
                conn.close()

    def get_user_by_username(self, username):
        """Look up a user by username."""
        conn = None
        cursor = None
        try:
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, username, email FROM users WHERE username = ?",
                (username,)
            )
            row = cursor.fetchone()
            if row:
                return {"id": row[0], "username": row[1], "email": row[2]}
        except sqlite3.Error as e:
            print(f"Database error during user retrieval: {e}")
        finally:
            if cursor: 
                cursor.close()
            if conn: 
                conn.close()
    
    def get_user_by_email(self,email):
        """Look up a user by email address."""
        conn = None
        cursor = None
        try: 
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, username, email, password FROM users WHERE email = ?",
                (email,)
            )
            row = cursor.fetchone()
            if row:
                return {"id": row[0], "username": row[1], "email": row[2], "password": row[3]}
        except sqlite3.Error as e:
            print(f"Database error during user retrieval: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def verify_login(self, email, password):
        """
        Check login credentials.
        Returns the user dict if correct, or None if email/password is wrong.
        """
        user = self.get_user_by_email(email)
        if user and check_password_hash(user["password"], password):
            # Return user without the password hash
            return {"id": user["id"], "username": user["username"], "email": user["email"]}
        return None    

    def update_user_email(self, username, new_email):
        conn = None
        cursor = None
        try:
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET email = ? WHERE username = ?",
                (new_email, username)
            )
            conn.commit()
            if cursor.rowcount:
                return self.get_user_by_username(username)
            else:
                print("User not found.")
        except sqlite3.IntegrityError:
            print("Error: Email already in use.")
        except sqlite3.Error as e:
            print(f"Database error during update: {e}")
        finally:
            if cursor: 
                cursor.close()
            if conn: 
                conn.close()

    def delete_user(self, username):
        conn = None
        cursor = None
        try:
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM users WHERE username = ?",
                (username,)
            )
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Database error during deletion: {e}")
            return False
        finally:
            if cursor: 
                cursor.close()
            if conn: 
                conn.close()

# Example usage
if __name__ == "__main__":
    db = SqlDb("db/sql.db")

    # Create
    user = db.create_user("emiltech", "emil@example.com")
    print("Created:", user)

    # Read
    user = db.get_user_by_username("emiltech")
    print("Retrieved:", user)

    # Update
    updated_user = db.update_user_email("emiltech", "emil_updated@example.com")
    print("Updated:", updated_user)

    # Delete
    success = db.delete_user("emiltech")
    print("Deleted:", success)
    
