from datetime import datetime
from flask_restful import Resource, reqparse, abort
from flask import request, jsonify, current_app
from functools import wraps
import jwt
from pignoletto import db, db_manager
from .models import (
    User_model,
    drone_acq,
    site
)
from geoalchemy2 import func
import numpy as np


ALLOWED_EXTENSIONS = set(["csv"])
def allowed_file(filename):
    """Checks that a given file name has a valid extension.

        Parameters
        ----------
        filename : A file name

        Returns
        -------
        bool : Return true if the file name is allowed
        
        """
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


### Wrapper function
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "x-access-token" in request.headers:
            token = request.headers["x-access-token"]
        if not token:
            abort(401, message="Token missing")
        try:
            data = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms="HS256")
            current_user = db.session.query(User_model).filter_by(id=data["id"]).first()
        except Exception as e:
            abort(401, message="Token invalid")
        return f(current_user, *args, **kwargs)
    return decorated


class DroneAcquisition(Resource):
    drone_parser = reqparse.RequestParser()
    drone_parser.add_argument("start acq timestamp", type=str, help="Starting timestamp required", required=True)
    drone_parser.add_argument("stop acq timestamp", type=str, help="Ending timestamp required", required=True)
    drone_parser.add_argument("site", type=str)
    drone_parser.add_argument("mission", type=str)
    drone_parser.add_argument("path", type=str)
    drone_parser.add_argument("acquisition", type=str)
    drone_parser.add_argument("latitude", type=float, help="Measurement's latitude required", required=True)
    drone_parser.add_argument("longitude", type=float, help="Measurement's longitude required", required=True)
    drone_parser.add_argument("z", type=int)
    drone_parser.add_argument("bandaIniziale", type=int, help="Starting band required", required=True)
    drone_parser.add_argument("bandaFinale", type=int, help="Ending band required", required=True)
    drone_parser.add_argument("gamma", type=str, help="Measurement's gamma required", required=True)

    @token_required
    def post(self, current_user):
        args = DroneAcquisition.drone_parser.parse_args()
        try:
            start_acq = datetime.strptime(args["start acq timestamp"], '%Y-%m-%d %H:%M:%S')
            stop_acq = datetime.strptime(args["stop acq timestamp"], '%Y-%m-%d %H:%M:%S')
        except Exception as e:
            abort(400, message=f"{e}")
        if stop_acq < start_acq:
            abort(400, message="Timestamps not consistent.")
        if args["bandaFinale"] < args["bandaIniziale"]:
            abort(400, message="Bands not consistent.")
        
        try:
            gamma = args["gamma"].replace('[', '').replace(']', '')
            gamma = np.fromstring(gamma, sep=',')
            if not len(gamma)>0:
                abort(400, message="Gamma values not in a valid format.")
        except Exception as e:
            abort(400, message=f"{e}")

        res = db.session.query(site).filter(site.c.name == args["site"]).first()
        if res is None:
            s = site.insert().values(name=args["site"])
            db.session.execute(s)
        # get site ids
        site_mapping = dict(db.session.query(site.c.name, site.c.id).all())
        site_id = site_mapping[args["site"]]

        add = drone_acq.insert().values(
            start_acq_time = start_acq,
            stop_acq_time= stop_acq,
            site = site_id,
            mission = args["mission"],
            path = args["path"],
            acquisition = args["acquisition"],
            lat = args["latitude"],
            lon = args["longitude"],
            z = args["z"],
            start_band = args["bandaIniziale"],
            stop_band = args["bandaFinale"],
            coords = func.ST_GeomFromText(f"POINT({args['longitude']} {args['latitude']})", 3003),
            gamma = gamma,
            time = datetime.now()
        )
        db.session.execute(add)
        db.session.commit()
        return jsonify({'message' : "Drone acquisition uploaded successfully"}, 201)


class DroneAcquisitions(Resource):
    @token_required
    def post(self, current_user):
        if 'file' not in request.files:
            abort(404, message="File not found.")
        file = request.files["file"]
        if file and file.filename == '':
            abort(400, message="File not valid.")
        if file and allowed_file(file.filename):
            # Call to the DBManager
            db_manager.insert_drone_acquisition(file)
        return jsonify({'message' : "Drone acquisitions uploaded successfully"}, 201)