from uuid import UUID
from datetime import datetime,timezone
from sqlalchemy.orm import Mapped,mapped_column,relationship
from sqlalchemy import Integer,String,ForeignKey,PrimaryKeyConstraint,UniqueConstraint,Uuid,TIMESTAMP
from data import Base



class User(Base):

    __tablename__ = 'users'

    user_id: Mapped[int] = mapped_column(Integer)

    username: Mapped[str] = mapped_column(String(50),nullable=False)

    email: Mapped[str] = mapped_column(String(50),nullable=False)

    hashed_password: Mapped[str] = mapped_column(String(200),nullable=False)

    refresh_tokens = Mapped[list['RefreshToken']] = relationship('RefreshToken',back_populates='user')

    __table_args__ = (
        PrimaryKeyConstraint('user_id',name='pk_users'),
        UniqueConstraint('username',name='uq_users_username'),
        UniqueConstraint('email',name='uq_users_email')
    )



class RefreshToken(Base):

    __tablename__ = 'refresh_tokens'

    row_id: Mapped[int] = mapped_column(Integer)

    jti: Mapped[UUID] = mapped_column(Uuid(as_uuid=True),nullable=False)

    user_id: Mapped[int] = mapped_column(ForeignKey('users.user_id',ondelete="CASCADE"),nullable=False)

    expired_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True),nullable=False)

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True),nullable=False,default=lambda :datetime.now(timezone.utc))

    user: Mapped['User'] = relationship('User',back_populates='refresh_tokens')

    __table_args__ = (
        PrimaryKeyConstraint('row_id',name='pk_refresh_tokens'),
        UniqueConstraint('jti',name='uq_refresh_tokens_jti')
    )
