from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from ..db import db
from .board import Board
from typing import Optional


class Card(db.Model):

    # The Card model represents a card that belongs to a specific board.
    # Each card contains a message and a count of likes.

    __tablename__ = "cards"  # Table name in the database

    # Primary key for each card, auto-incremented
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    message: Mapped[str] = mapped_column()  # The content/message of the card
    # Number of likes for the card (default is 0)
    likes_count: Mapped[int] = mapped_column(default=0)
    # Foreign key referencing the 'boards' table (must be linked to a board)
    board_id: Mapped[int] = mapped_column(
        ForeignKey("board.id"), nullable=False)

    # Relationship to the Board model (each card is linked to one board)
    board: Mapped["Board"] = relationship("Board", back_populates="cards")

# Helper method to convert the card object into a dictionary for JSON responses.


def to_dict(self):
    card_dict = {
        "card_id": self.id,
        "message": self.message,
        "likes_count": self.likes_count,
        "board_id": self.board_id
    }


@classmethod
def from_dict(cls, data):
    return cls(
        message=data.get("message"),
        likes_count=data.get("likes_count", 0),
        board_id=data.get("board_id")
    )
