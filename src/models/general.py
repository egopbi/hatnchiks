from typing import Annotated
from sqlalchemy.orm import DeclarativeBase, relationship, Mapped, mapped_column
from sqlalchemy import DateTime, ForeignKey, String


str20 = Annotated[str, 20]

class Base(DeclarativeBase):
    repr_cols_num = 3
    repr_cols = tuple()
    def __repr__(self):
        cols = []
        
        for idx, col in enumerate(self.__table__.columns.keys()):
            if col in self.repr_cols or idx < self.repr_cols_num:
                cols.append(f"{col}={getattr(self, col)}")
                
        return f"<{self.__class__.__name__} {' | '.join(cols)}>"

    type_annotation_map = {
       str20: String(20)
    }


class User(Base):
    __tablename__ = "users"

    username: Mapped[str20] = mapped_column(primary_key=True)
    password: Mapped[bytes]
    