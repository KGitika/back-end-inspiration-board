from flask import Blueprint, abort, make_response, request
from app.models.card import Card
from app.routes.routes_utilities import validate_model
from ..db import db

bp = Blueprint("cards_bp", __name__, url_prefix="/cards")

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
            abort(make_response(
                {"message": "Message too long (max 500 characters)"}, 400))
        card.message = request_body["message"]
    else:
        abort(make_response(
            {"message": "Missing required field: message"}, 400))

    db.session.commit()
    return make_response({"card": card.to_dict()}, 200)


@bp.patch("/<card_id>/like")
def update_like_count(card_id):
    """
    Increment or decrement a card's like count.
    Use ?action=like or ?action=unlike in the query string.
    """
    card = validate_model(Card, card_id)
    action = "like" 

    if action == "like":
        card.likes_count += 1
    elif action == "unlike":
        card.likes_count = max(0, card.likes_count - 1)
    else:
        abort(make_response(
            {"message": "Invalid action. Use 'like' or 'unlike'."}, 400))

    db.session.commit()
    return {"card": card.to_dict()}, 200


@bp.delete("/<card_id>")
def delete_card(card_id):
    """
    Delete a card by ID.
    """
    card = validate_model(Card, card_id)

    db.session.delete(card)
    db.session.commit()

    return make_response({"message": "Card deleted successfully"}, 204)
