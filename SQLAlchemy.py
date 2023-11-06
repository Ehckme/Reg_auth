"""
The following below code is for connecting  to an existing
database and creating new table using SQLAlchemy 2.22 version
It inherits from sqlalchemy.orm DeclarativeBase

Please check for latest version updates and update when necessary!

"""

# import SQLAlchemy
from sqlalchemy import ForeignKey, String, Integer, CHAR
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import relationship, mapped_column
from sqlalchemy import select, create_engine
from sqlalchemy.orm import Session

# create an inheritance class from declarativeBase
class Base(DeclarativeBase):
    pass

# Create a Table class
class New_User_Database(Base):
    __tablename__ = 'Users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(30))
    email: Mapped[str] = mapped_column(String(30))
    password: Mapped[str] = mapped_column(CHAR(80))

    def __repr__(self) -> str:
        return f'Users(id={self.id!r}, username={self.username!r}, ' \
               f'email={self.email}, password={self.password}'

connection_string = 'mysql+pymysql://root:root@localhost/New_User_Database'
engine = create_engine(connection_string, echo=True)

Base.metadata.create_all(engine)

with Session(engine) as session:
    motchello  = New_User_Database(
        username='motchello',
        email='motchello@gmail.com',
        password='#BlackJew'
    )
    lerato = New_User_Database(
        username='Lerato',
        email='lerato@yahoo.com',
        password='FuckMe#!'
    )

    # Add
    session.add_all([motchello, lerato])
    session.commit()