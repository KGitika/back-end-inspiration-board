from flask import Blueprint, Response, abort, make_response, request
from app.models.board import Board
from app.models.card import Card
from app.routes.routes_utilities import validate_model, create_model
from ..db import db

bp = Blueprint("cards_bp", __name__, url_prefix="/cards")

@bp.post("")
def create_card():
    """
    Create a new card.
    """
    request_body = request.get_json()
    return create_model(Card, request_body)

@bp.get("")
def get_cards():
    """
    Get all cards with optional filtering and sorting.
    Query parameters:
    - board_id: Filter cards by board ID.
    - sort: Sort cards by 'asc' or 'desc' based on the message field.
    - order: sort order (asc or desc, defaults to asc)
    If no sort parameter is provided, cards are sorted by card ID in ascending order.
    """
    query = db.select(Card)

    board_id_param = request.args.get("board_id")
    if board_id_param:
        try:
            board_id_int = int(board_id_param)
            query = query.where(Card.board_id == board_id_int)
        except ValueError:
            abort(make_response({"message": "Invalid board_id"}, 400))

    sort_by = request.args.get("sort_by", "id")
    order = request.args.get("order", "asc")
    
    valid_sort_fields = {"message", "likes_count", "id"}
    if sort_by not in valid_sort_fields:
        abort(make_response({"message": f"Invalid sort_by field. Must be one of: {', '.join(valid_sort_fields)}"}, 400))

    sort_column = {
        "message": Card.message,
        "likes_count": Card.likes_count,
        "id": Card.id
    }[sort_by]

    if order.lower() == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    cards = db.session.scalars(query).all()

    return make_response({"cards": [card.to_dict() for card in cards]}, 200)

@bp.get("/<card_id>")
def get_card(card_id):
    """
    Get a card by ID.
    """
    card = validate_model(Card, card_id)

    return make_response({"card": card.to_dict()}, 200)

@bp.put("/<card_id>")
def update_card(card_id):
    """
    Update a card by ID.
    Requires: { "message": string } in request body
    """
    card = validate_model(Card, card_id)
    request_body = request.get_json()

    if "message" in request_body:
        if len(request_body["message"]) > 500:
            abort(make_response({"message": "Message too long (max 500 characters)"}, 400))
        card.message = request_body["message"]
    else:
        abort(make_response({"message": "Missing required field: message"}, 400))

    db.session.commit()
    return make_response({"card": card.to_dict()}, 200)

@bp.post("/<card_id>/like")
def like_card(card_id):
    """
    Increment a card's like count.
    Like count has no upper limit.
    """
    card = validate_model(Card, card_id)
    card.likes_count += 1
    db.session.commit()
    return make_response({"card": card.to_dict()}, 200)

@bp.delete("/<card_id>/like")
def unlike_card(card_id):
    """
    Decrement a card's like count.
    Like count cannot go below 0.
    """
    card = validate_model(Card, card_id)
    card.likes_count = max(0, card.likes_count - 1)
    db.session.commit()
    return make_response({"card": card.to_dict()}, 200)

@bp.delete("/<card_id>")
def delete_card(card_id):
    """
    Delete a card by ID.
    """
    card = validate_model(Card, card_id)
    
    db.session.delete(card)
    db.session.commit()

    return make_response({"message": "Card deleted successfully"}, 204)

