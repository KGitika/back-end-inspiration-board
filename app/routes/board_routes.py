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
    Get all boards with optional filtering and sorting.
    Query parameters:
    - title: filter by title (case-insensitive partial match)
    - sort_by: field to sort by (title, id, or other valid Board field)
    - order: sort order (asc or desc, defaults to asc)
    """
    query = db.select(Board)

    title_param = request.args.get("title")
    if title_param:
        query = query.where(Board.title.ilike(f"%{title_param}%"))

    sort_by = request.args.get("sort_by", "id")
    order = request.args.get("order", "asc") 

    valid_sort_fields = {"title", "id"}
    if sort_by not in valid_sort_fields:
        abort(make_response({"message": f"Invalid sort_by field. Must be one of: {', '.join(valid_sort_fields)}"}, 400))

    sort_column = {
        "title": Board.title,
        "id": Board.id
    }[sort_by]

    if order.lower() == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

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
    Get all cards for a specific board, with optional sorting.
    Query parameters:
    - sort_by: message, likes_count, or id
    - order: asc (default) or desc
    """
    board = validate_model(Board, board_id)

    sort_by = request.args.get("sort_by", "id")
    order = request.args.get("order", "asc")

    valid_sort_fields = {"message", "likes_count", "id"}
    if sort_by not in valid_sort_fields:
        abort(make_response({"message": f"Invalid sort_by. Must be one of: {', '.join(valid_sort_fields)}"}, 400))

    sort_column = {
        "message": Card.message,
        "likes_count": Card.likes_count,
        "id": Card.card_id 
    }[sort_by]

    if order.lower() == "desc":
        sort_column = sort_column.desc()
    else:
        sort_column = sort_column.asc()

    query = db.select(Card).where(Card.board_id == board.id).order_by(sort_column)
    cards = db.session.scalars(query).all()

    return {"cards": [card.to_dict() for card in cards]}, 200

@bp.post("/<board_id>/cards")
def create_card_for_board(board_id):
    """
    Create a new card for a specific board.
    Requires 'message' in the request body.
    """
    board = validate_model(Board, board_id)
    request_body = request.get_json()

    if "message" not in request_body:
        abort(make_response({"message": "Missing required field: 'message'"}, 400))

    new_card = Card(
        message=request_body["message"],
        board_id=board.id,
        likes_count=0
    )

    db.session.add(new_card)
    db.session.commit()

    return {"card": new_card.to_dict()}, 201

# @bp.get("/<board_id>/cards")
# def get_board_cards(board_id):
#     """
#     Get all cards for a specific board.
#     """
#     board = validate_model(Board, board_id)
#     return {
#         "id": board.id,
#         "title": board.title,
#         "cards": [card.to_dict() for card in board.cards]
#     }

# @bp.get("/<board_id>/cards")
# def get_cards_from_board(board_id):
#     """
#     Get all cards with optional filtering and sorting.
#     Query parameters:
#     - board_id: Filter cards by board ID.
#     - sort: Sort cards by 'asc' or 'desc' based on the message field.
#     - order: sort order (asc or desc, defaults to asc)
#     If no sort parameter is provided, cards are sorted by card ID in ascending order.
#     """
#     query = db.select(Card)

#     board_id_param = request.args.get("board_id")
#     if board_id_param:
#         try:
#             board_id_int = int(board_id_param)
#             query = query.where(Card.board_id == board_id_int)
#         except ValueError:
#             abort(make_response({"message": "Invalid board_id"}, 400))

#     sort_by = request.args.get("sort_by", "id")
#     order = request.args.get("order", "asc")
    
#     valid_sort_fields = {"message", "likes_count", "id"}
#     if sort_by not in valid_sort_fields:
#         abort(make_response({"message": f"Invalid sort_by field. Must be one of: {', '.join(valid_sort_fields)}"}, 400))

#     sort_column = {
#         "message": Card.message,
#         "likes_count": Card.likes_count,
#         "id": Card.id
#     }[sort_by]

#     if order.lower() == "desc":
#         query = query.order_by(sort_column.desc())
#     else:
#         query = query.order_by(sort_column.asc())

#     cards = db.session.scalars(query).all()

#     return make_response({"cards": [card.to_dict() for card in cards]}, 200)


# @bp.post("/<board_id>/cards")
# def create_card(board_id):
#     """
#     Create a new card for a specific board.
#     """
#     board = validate_model(Board, board_id)
#     request_body = request.get_json()

#     if "message" not in request_body or "board_id" not in request_body:
#         abort(make_response({"message": "Missing required fields: 'message' and 'board_id'"}, 400))

#     if request_body["board_id"] != board.id:
#         abort(make_response({"message": f"Board ID mismatch. Expected {board.id}, got {request_body['board_id']}"}, 400))

#     return create_model(Card, request_body)



# need to add this endpoint if we have effectively the same one in card_routes.py?
# in card routes:
# @bp.post("<board_id>/cards")
# def create_card():
#     """
#     Create a new card.
#     """
#     request_body = request.get_json()
#     return create_model(Card, request_body)