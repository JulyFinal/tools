from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


class Base(DeclarativeBase):
    pass


class Actor(Base):
    __tablename__ = "actor_table"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    photo: Mapped[bytes] = mapped_column(nullable=True)
    favorites: Mapped[bool] = mapped_column(nullable=True)

    def __repr__(self) -> str:
        return f"Actor(id={self.id!r}, name:{self.name!r})"


class AVMeta(Base):
    __tablename__ = "av_table"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    av_id: Mapped[str] = mapped_column(nullable=False)
    title: Mapped[str] = mapped_column(nullable=True)
    actors: Mapped[str] = mapped_column(nullable=True)
    cover: Mapped[bytes] = mapped_column(nullable=True)
    tags: Mapped[str] = mapped_column(nullable=True)
    publish_time: Mapped[str] = mapped_column(nullable=True)
    favorites: Mapped[bool] = mapped_column(nullable=True)
    origin_url: Mapped[str] = mapped_column(nullable=True)

    def __repr__(self) -> str:
        return f"AVMeta(id:{self.id!r}, av_id:{self.av_id!r}, title:{self.title}), actors:{self.actors!r}, tags:{self.tags!r}, publish_time:{self.publish_time!r}"


# create table
from sqlalchemy import create_engine

# engine = create_engine("sqlite:///final.db", echo=True)
# AVMeta.metadata.create_all(engine)
# Actor.metadata.create_all(engine)
