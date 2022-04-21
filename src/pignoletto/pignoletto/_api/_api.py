from flask import Blueprint, request, jsonify, current_app
import datetime
import jwt
from werkzeug.security import check_password_hash

from pignoletto import db
from pignoletto.models import User_model


_api = Blueprint("_api", __name__)


@_api.get("/login") 
def api_login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return jsonify({"Error": "Could not verify login"}, 400)
    user = db.session.query(User_model).filter_by(username=auth.username).first()
    if not user:
        return jsonify({"Error": "User not found"}, 400)
    if user.verified == False:
        return jsonify({"Error": "User not verified yet"}, 400)
    if not user.role[0].type == "admin":
        return jsonify({"Error": "Sorry, you don't have the rights to access"}, 400)
    if check_password_hash(user.password, auth.password):
        token = jwt.encode({"id": user.id, "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, current_app.config["SECRET_KEY"], algorithm="HS256")
        return jsonify({"token": token.decode('UTF-8')}, 200)
    return jsonify({"Error": "Invalid password"}, 400)
