from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from ..db import db
from typing import Optional

class Card(db.Model):

    # The Card model represents a card that belongs to a specific board.
    # Each card contains a message and a count of likes.
    
    __tablename__ = "cards"  # Table name in the database

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)  # Primary key for each card, auto-incremented
    message: Mapped[str] = mapped_column(nullable=False)   # The content/message of the card (cannot be null)
    likes_count: Mapped[int] = mapped_column(default=0)  # Number of likes for the card (default is 0)
    board_id: Mapped[int] = mapped_column(ForeignKey("boards.id"), nullable=False)  # Foreign key referencing the 'boards' table (must be linked to a board)

    board: Mapped["Board"] = relationship("Board", back_populates="cards")  # Relationship to the Board model (each card is linked to one board)

    

    