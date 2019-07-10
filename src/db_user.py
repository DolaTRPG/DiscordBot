import os
import time

from sqlalchemy import Column, BigInteger, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


DATABASE_URL = os.environ['DATABASE_URL']

Base = declarative_base()
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)


class User(Base):
    __tablename__ = 'user'

    id = Column(BigInteger, primary_key=True)
    name = Column(String(32))
    point = Column(Integer, default=0)
    activity_at = Column(Integer, default=int(time.time()))
    gm = Column(Integer, default=0)
    earn = Column(Integer, default=0)
    used = Column(Integer, default=0)

Base.metadata.create_all(engine)


def add(uid: int, name: str) -> User:
    if uid == 234835249094197250:
        # avoid adding bot into database
        return

    user = User(id=uid, name=name)
    session = Session()
    try:
        session.add(user)
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
    return user


def get(uids: [int]) -> User:
    session = Session()
    users = session.query(User).filter(User.id.in_(uids)).all()
    session.close()
    return users


def get_inactive(delta_seconds: int) -> [User]:
    session = Session()
    try:
        users = session.query(User).filter(User.activity_at < int(time.time()) - delta_seconds).all()
    except:
        session.rollback()
        raise
    finally:
        session.close()
    return users


def update(uid: int, **kwargs) -> User:
    session = Session()
    update_content = {}
    for key in kwargs:
        update_content[key] = kwargs[key]

    try:
        user = session.query(User).filter(User.id == uid).update(update_content)
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
    return user


def remove(uid: int) -> None:
    session = Session()
    try:
        user = session.query(User).filter(User.id == uid).first()
        session.delete(user)
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
