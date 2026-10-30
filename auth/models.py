from sqlalchemy.orm import Mapped,mapped_column,relationship
from sqlalchemy import Integer,String,ForeignKey,PrimaryKeyConstraint,UniqueConstraint
from data import Base



class User(Base):

    __tablename__ = 'users'

    user_id: Mapped[int] = mapped_column(Integer)

    username: Mapped[str] = mapped_column(String(50),nullable=False)

    email: Mapped[str] = mapped_column(String(50),nullable=False)

    hashed_password: Mapped[str] = mapped_column(String(200),nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint('user_id',name='pk_users'),
        UniqueConstraint('username',name='uq_users_username'),
        UniqueConstraint('email',name='uq_users_email')
    )



class RefreshToken(Base):
    pass