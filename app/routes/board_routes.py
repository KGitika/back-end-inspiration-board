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
    request_body = request.get_json()
    return create_model(Board, request_body)

@bp.get("")
def get_boards():
    """
    Get all boards.
    """
    query = db.select(Board)

    title_param = request.args.get("title")
    if title_param:
        query = query.where(Board.title.ilike(f"%{title_param}%"))
    
    sort_param = request.args.get("sort")
    if sort_param == "asc":
        query = query.order_by(Board.title.asc())
    elif sort_param == "desc":
        query = query.order_by(Board.title.desc())
    else:
        query = query.order_by(Board.id)

    boards = db.session.scalars(query).all()

    return make_response({"boards": [board.to_dict() for board in boards]}, 200)

@bp.get("/<board_id>")
def get_board(board_id):
    """
    Get a board by ID.
    """
    board = validate_model(Board, board_id)

    return make_response({"board": board.to_dict()}, 200)

@bp.put("/<board_id>")
def update_board(board_id):
    """
    Update a board by ID.
    """
    board = validate_model(Board, board_id)
    request_body = request.get_json()

    if "title" in request_body:
        board.title = request_body["title"]
    if "owner" in request_body:
        board.owner = request_body["owner"]

    db.session.commit()
    return make_response({"board": board.to_dict()}, 204)

@bp.delete("/<board_id>")
def delete_board(board_id):
    """
    Delete a board by ID.
    """
    board = validate_model(Board, board_id)

    db.session.delete(board)
    db.session.commit()

    return make_response({"message": f"Board {board_id} deleted successfully."}, 204)

@bp.get("/<board_id>/cards")
def get_board_cards(board_id):
    """
    Get all cards for a specific board.
    """
    board = validate_model(Board, board_id)
    return {
        "id": board.id,
        "title": board.title,
        "cards": [card.to_dict() for card in board.cards]
    }

@bp.post("/<board_id>/cards")
def create_board_card(board_id):
    """
    Create a new card for a specific board.
    """
    board = validate_model(Board, board_id)
    request_body = request.get_json()
    
    # Ensure the board_id in the request matches the validated board
    request_body["board_id"] = board.id
    
    return create_model(Card, request_body)