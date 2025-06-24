from flask import Blueprint, Response, abort, make_response, request
from app.models.board import Board
from app.models.card import Card
from app.routes.routes_utilities import validate_model, create_model
from ..db import db

bp = Blueprint("boards_bp", __name__, url_prefix="/boards")

@bp.post("")
def create_board():
    """
    Create a new board.
    """
    data = request.get_json()
    if not data:
        abort(400, "No data provided")

    board = create_model(Board, data)
    db.session.add(board)
    db.session.commit()

    return make_response(board.to_dict(), 201)