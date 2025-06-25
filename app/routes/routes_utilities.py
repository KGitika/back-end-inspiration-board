from flask import abort, make_response
from ..db import db

def validate_model(cls, model_id):
    """Validate that a model exists in the database with the given ID."""
    
    try:
        model_id = int(model_id)
    except ValueError:
        invalid_response = {"message": f"The {cls.__name__} with ID {model_id} is invalid."}
        abort(make_response(invalid_response, 400))

    # Query the database for the model with the given ID
    query = db.select(cls).where(cls.id == model_id)
    model = db.session.scalar(query)

    # If the model is not found, return a 404 error
    if not model:
        invalid_response = {"message": f"The {cls.__name__} with ID {model_id} does not exist."}
        abort(make_response(invalid_response, 404))

    return model

def create_model(cls, model_data):
    """Create a new model instance from the provided data."""

    required_fields = {
        "Board": ["title", "owner"],
        "Card": ["message", "board_id"]
    }
    missing_fields = [field for field in required_fields if field not in model_data]
    if missing_fields:
        invalid_response = {
            "message": f"Missing required fields: {', '.join(missing_fields)}"
        }
        abort(make_response(invalid_response, 400))

    try:
        new_model = cls.from_dict(model_data)
    except KeyError as e:
        invalid_response = {
            "message": f"Missing required field(s): {e.args[0]}"
        }
        abort(make_response(invalid_response, 400))
    except Exception as e:
        invalid_response = {
            "message": f"An unexpected error occurred: {str(e)}"
        }
        abort(make_response(invalid_response, 500))

    db.session.add(new_model)
    db.session.commit()

    return {f"{cls.__name__.lower()}": new_model.to_dict()}, 201