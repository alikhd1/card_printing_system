import hashlib
import random
from copy import deepcopy

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Date
from sqlalchemy.ext.declarative import declarative_base

from dialog import show_dialog

Base = declarative_base()


class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    almas_id = Column(String, unique=True)
    asemoon_id = Column(String, unique=True)
    hashed_id = Column(String, unique=True)

    @classmethod
    def generate_number(cls, session):
        # Generate a random 8-digit number
        number = random.randint(10000000, 99999999)

        # Check if the number already exists in the DataFrame
        if cls.exists_by_asemoon_id(session, number):
            number = cls.generate_number(session)
        return number

    @classmethod
    def exists_by_almas_id(cls, session, value):
        return session.query(cls).filter_by(almas_id=value).first() is not None

    @classmethod
    def exists_by_asemoon_id(cls, session, value):
        return session.query(cls).filter_by(asemoon_id=value).first() is not None

    @classmethod
    def exists_by_hashed_id(cls, session, value):
        return session.query(cls).filter_by(hashed_id=value).first() is not None

    @classmethod
    def save_number(cls, session, id):
        if cls.exists_by_almas_id(session, id):
            user = session.query(Users).filter_by(almas_id=id).first()
            return user.asemoon_id, user.hashed_id, False

        generated_number = cls.generate_number(session=session)
        hashed_code = hashlib.md5(str(generated_number).encode()).hexdigest()[:16]

        new_user = Users(almas_id=id, asemoon_id=generated_number, hashed_id=hashed_code)
        session.add(new_user)
        session.commit()

        return generated_number, hashed_code, True

    @classmethod
    def delete_numbers(cls, codes: list):
        from sqlalchemy.orm import sessionmaker
        from forms.windows import engine
        session = sessionmaker(bind=engine)
        session = session()
        for code in codes:
            if cls.exists_by_asemoon_id(session, code):
                user_to_delete = session.query(Users).filter_by(asemoon_id=code).first()
                session.delete(user_to_delete)
        session.commit()
        session.close()


    @classmethod
    def assign_subscription_code(cls, users: list, signal):
        from sqlalchemy.orm import sessionmaker
        from forms.windows import engine
        session = sessionmaker(bind=engine)
        session = session()

        try:
            for i, user in enumerate(users):
                user['code'], user['hashed_code'], user['created'] = cls.save_number(session, user['id'])
                if signal:
                    signal.emit((i + 1) * 100 / (len(users)))
        except ValueError as e:
            show_dialog(error=e)

        user = deepcopy(users)
        users = []
        for u in user:
            if u['created']:
                users.append(u)

        session.close()
        return users

    @classmethod
    def resolve_url(cls, users: list, base_url, signal=None):
        for i, user in enumerate(users):
            user['url'] = f"{base_url}/{str(user['hashed_code'])}"
            if signal:
                signal.emit((i + 1) * 100 / (len(users)))
        return users
