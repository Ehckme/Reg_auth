from sqlalchemy import select, create_engine
from sqlalchemy.orm import Session, session, sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import relationship, mapped_column
from sqlalchemy import ForeignKey, String, Integer, CHAR


class Base(DeclarativeBase):
    pass


class New_User_Database(Base):
    __tablename__ = 'Users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(30))
    email: Mapped[str] = mapped_column(String(30))
    password: Mapped[str] = mapped_column(CHAR(30))

    def __repr__(self) -> str:
        return f'Users(id={self.id!r}, username={self.username!r}, ' \
               f'email={self.email}, password={self.password}'


connection_string = 'mysql+pymysql://root:root@localhost/New_User_Database'
engine = create_engine(connection_string, echo=True)

Base.metadata.create_all(engine)

user_query = input('enter query ')
stmnt = select(New_User_Database).where(New_User_Database.username == user_query)

Session = sessionmaker(bind=engine)
session = Session()

result = session.execute(stmnt)

for user in result.scalars():
    if user_query != user.username:
        print('Invalid User')
    else:
        username = user.username
        email = user.email
        password = user.password
        print(f'{username} {email}')
        print(password)
"""
with engine.connect() as conn:
    for row in conn.execute(stmnt):
        print('Here are the new results', row)
"""
