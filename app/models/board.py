from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..db import db
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from .card import Card


class Board(db.Model):
    __tablename__ = "board"  # Table name in the database

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(nullable=False)
    owner: Mapped[str] = mapped_column(nullable=False)

    cards: Mapped[List["Card"]] = relationship(back_populates="board")

    def to_dict(self):
        board_as_dict = {
            "id": self.id,
            "title": self.title,
            "owner": self.owner
        }
        if self.cards:
            board_as_dict["cards"] = [card.to_dict() for card in self.cards]
        else:
            board_as_dict["cards"] = []
        return board_as_dict

    @classmethod
    def from_dict(cls, board_data):
        # return Board(title=board_data["title"], owner=board_data["owner"])
        return cls(title=board_data["title"], owner=board_data["owner"])
