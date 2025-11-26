from sqlalchemy import create_engine
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.exc import IntegrityError

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"


class OrmDb(object):
    
    def __init__(self, db_path="db/app.db"):
        self.__engine = create_engine(f"sqlite:///{db_path}", echo=True)
        Base.metadata.create_all(self.__engine)
        self.Session = sessionmaker(bind = self.__engine)

    def __del__(self):
        if self.__engine:
            self.__engine.dispose()
   
    def create_user(self, username, email):
        session = self.Session()
        try:
            user = User(username = username, email = email)
            session.add(user)
            session.commit()
            session.refresh(user)
            return user
        except IntegrityError:
            session.rollback()
            print(f"Error: Username or email already exists.")
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Database error during user creation: {e}")
        finally:
            session.close()

    def get_user_by_username(self, username):
        session = self.Session()
        try:
            return session.query(User).filter_by(username = username).first()
        except SQLAlchemyError as e:
            print(f"Database error during user retrieval: {e}")
        finally:
            session.close()

    def update_user_email(self, username, new_email):
        session = self.Session()
        try:
            user = session.query(User).filter_by(username = username).first()
            if user:
                user.email = new_email
                session.commit()
                session.refresh(user)
                return user
            else:
                print("User not found.")
        except IntegrityError:
            session.rollback()
            print("Error: Email already in use.")
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Database error during update: {e}")
        finally:
            session.close()

    def delete_user(self, username):
        session = self.Session()
        try:
            user = session.query(User).filter_by(username=username).first()
            if user:
                session.delete(user)
                session.commit()
                return True
            else:
                print("User not found.")
                return False
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Database error during deletion: {e}")
            return False
        finally:
            session.close()

# Example usage
if __name__ == "__main__":
    db = OrmDb("db/orm.db")

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
