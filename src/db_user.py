from datetime import datetime, timedelta
import os
import time

from sqlalchemy import Column, BigInteger, Integer, String, DateTime, create_engine
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
    activity_at = Column(DateTime, default=datetime.utcnow)
    gm = Column(Integer, default=0)
    earn = Column(Integer, default=0)
    use = Column(Integer, default=0)

Base.metadata.create_all(engine)


def add(**kwargs) -> User:
    if kwargs.get('id') == 234835249094197250:
        # avoid adding bot into database
        return
    params = dict((k, v) for k, v in kwargs.items())
    user = User(**params)
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


def get(id: int) -> User:
    session = Session()
    user = session.query(User).filter_by(id=id).first()
    return user


def get_inactive(**kwargs) -> [User]:
    session = Session()
    try:
        inactive_period = timedelta(**kwargs)
        users = session.query(User).filter(User.activity_at < datetime.utcnow() - inactive_period).all()
    except:
        session.rollback()
        raise
    finally:
        session.close()
    return users


def update(id: int, **kwargs) -> User:
    session = Session()
    try:
        user = session.query(User).filter(User.id == id).update(kwargs)
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
    return user


def remove(id: int) -> None:
    session = Session()
    try:
        user = session.query(User).filter(User.id == id).first()
        session.delete(user)
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
