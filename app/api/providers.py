from flask import Blueprint

bp = Blueprint("providers", __name__)


@bp.get("/")
def list_providers():
    return {"providers": []}
