from flask import Blueprint, request, flash, render_template, redirect, url_for
import flask
from flask_restful import abort
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_user, login_required, logout_user, current_user
import sqlalchemy as sa
import zipfile
import os

from pignoletto import db, login_manager, app
from pignoletto.models import (
    User_model,
    Role_model,
    site,
    variable,
    drone_acq,
    images,
    model
)


def allowed_file(filename, file_type):
    """Checks that a given file name has a valid extension wrt file_type.

        Parameters
        ----------
        filename : A file name
        file_type: A string between: 'image', 'py', 'csv'

        Returns
        -------
        bool : Return true if the file name is allowed
        
        """
    ALLOWED_EXTENSIONS = None
    if file_type == "image":
        ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif','JPEG', 'tif', 'tiff'])
    elif file_type == "csv":
        ALLOWED_EXTENSIONS = set(["csv"])
    elif file_type == "py":
        ALLOWED_EXTENSIONS = set(["py"])
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


_frontend = Blueprint('_frontend', __name__,
                    template_folder='./templates',
                    static_folder='./static')


from pignoletto import db_manager


@login_manager.unauthorized_handler
def unauthorized_callback():
       return redirect(url_for('_frontend.login'))


@login_manager.user_loader
def load_user(id):
   return User_model.query.get(int(id))


@_frontend.post("/upload_model")
@login_required
def upload_model():
    if request.method == "POST":
        if "file" not in request.files:
            flash('File not valid.', category='error')
            return redirect(url_for("_frontend.laboratory_acquisitions"))
        file = request.files['file']
        if file and file.filename == '':
            flash('File not valid.', category='error')
            return redirect(url_for("_frontend.laboratory_acquisitions"))
        if not file or not file.filename.endswith("zip"):
            flash('File not valid.', category='error')
            return redirect(url_for("_frontend.laboratory_acquisitions"))
        if not zipfile.is_zipfile(file):
            flash('Not a valid zip file.', category='error')
            return redirect(url_for("_frontend.laboratory_acquisitions"))

        # Download any model if missing
        download_missing_models()

        name = file.filename.split(".")[-2]
        with zipfile.ZipFile(file) as myzip:
            if myzip.testzip() is not None:
                bad_file = myzip.testzip()
                flash(f'Error during file upload: {bad_file}', category='error')
                return redirect(url_for("_frontend.laboratory_acquisitions"))
            
            # Check if the files are already in DB and their extension
            for file_name in myzip.namelist():
                if db.session.query(model).filter(
                    model.c.name == file_name).first() is not None:
                    flash(f'Error: there is already a file named: {file_name}', category='warning')
                    return redirect(url_for("_frontend.laboratory_acquisitions"))
                if not allowed_file(file_name, file_type='py'):
                    flash(f'Error: file {file_name} has not a valid extension', category='warning')
                    return redirect(url_for("_frontend.laboratory_acquisitions"))

            model_path = "/srv/processing/algorithms/"
            bad_files = []
            for file_name in myzip.namelist():
                try:
                    myzip.extract(file_name, model_path)
                    with myzip.open(file_name) as myfile:
                        this_model = model.insert().values(
                                name = file_name,
                                path = os.path.abspath(os.path.join(model_path, file_name)),
                                file = myfile.read()
                            )
                        db.session.execute(this_model)
                except Exception as e:
                    flash(f'An error occur when extracting the model: {e}', category='warning')
                    bad_files.append(file_name)                
            

        if len(bad_files) > 0:
            # Delete files if exists
            for f in bad_files:
                if os.path.exists(os.path.abspath(os.path.join(model_path, f))):
                    os.remove(os.path.abspath(os.path.join(model_path, f)))
            db.session.rollback()
            flash(f'Error during upload for file: {bad_files}', category='warning')
        else:
            db.session.commit()
            flash('Model uploaded correctly.', category='success')        

    return redirect(url_for("_frontend.laboratory_acquisitions"))


@_frontend.post("/upload_zip")
@login_required
def upload_zip():
    if request.method == "POST":
        if "file" not in request.files:
            flash('File not valid.', category='error')
            return render_template("droneAcq_table.html", title=current_user.username, tipo=current_user.role[0].type, header=get_droneAcq_header())
        file = request.files['file']
        if file and file.filename == '':
            flash('File not valid.', category='error')
            return render_template("droneAcq_table.html", title=current_user.username, tipo=current_user.role[0].type, header=get_droneAcq_header())
        if not file or not file.filename.endswith("zip"):
            flash('File not valid.', category='error')
            return render_template("droneAcq_table.html", title=current_user.username, tipo=current_user.role[0].type, header=get_droneAcq_header())
        if not zipfile.is_zipfile(file):
            flash('Not a valid zip file.', category='error')
            return render_template("droneAcq_table.html", title=current_user.username, tipo=current_user.role[0].type, header=get_droneAcq_header())
        
        bad_files = []
        with zipfile.ZipFile(file) as myzip:
            if myzip.testzip() is not None:
                bad_file = myzip.testzip()
                flash(f'File {bad_file} is a bad file.', category='error')
                return render_template("droneAcq_table.html", title=current_user.username, tipo=current_user.role[0].type, header=get_droneAcq_header())
            for file_name in myzip.namelist():
                if allowed_file(file_name, file_type='image'):
                    with myzip.open(file_name) as myfile:
                        img = images.insert().values(
                            file=myfile.read(),
                            name=file_name
                            )
                        db.session.execute(img)
                else:
                    bad_files.append(file_name)

        if len(bad_files) > 0:
            db.session.rollback()
            flash(f'Error during upload for file: {bad_files}', category='warning')
        else:
            db.session.commit()
            flash('Zip file uploaded correctly.', category='success')
        return redirect(url_for("_frontend.drone_acquisitions"))


@_frontend.post("/upload_labAcq_csv")
@login_required
def upload_labAcq_csv():
    if request.method == "POST":
        if 'file' not in request.files:
            flash('File not valid.', category='error')
            return render_template("labAcq_table.html", title=current_user.username, tipo=current_user.role[0].type, header=get_labAcq_header())
        file = request.files['file']
        if file and file.filename == '':
            flash('File not valid.', category='error')
            return render_template("labAcq_table.html", title=current_user.username, tipo=current_user.role[0].type, header=get_labAcq_header())
        if not file or not allowed_file(file.filename, file_type='csv'):
            flash('File not valid.', category='error')
            return render_template("labAcq_table.html", title=current_user.username, tipo=current_user.role[0].type, header=get_labAcq_header())

        # Call the DBManager
        db_manager.insert_lab_acquisition(file)

        return render_template("labAcq_table.html", title=current_user.username, tipo=current_user.role[0].type, header=get_labAcq_header())


@_frontend.post("/upload_droneAcq_csv")
@login_required
def upload_droneAcq_csv():
    if request.method == "POST":
        if 'file' not in request.files:
            flash('File not valid.', category='error')
            return render_template("droneAcq_table.html", title=current_user.username, tipo=current_user.role[0].type, header=get_droneAcq_header())
        file = request.files['file']
        if file and file.filename == '':
            flash('File not valid.', category='error')
            return render_template("droneAcq_table.html", title=current_user.username, tipo=current_user.role[0].type, header=get_droneAcq_header())
        if not file or not allowed_file(file.filename, file_type='csv'):
            flash('File not valid.', category='error')
            return render_template("droneAcq_table.html", title=current_user.username, tipo=current_user.role[0].type, header=get_droneAcq_header())

        # Call the DBManager
        db_manager.insert_drone_acquisition(file)

        return render_template("droneAcq_table.html", title=current_user.username, tipo=current_user.role[0].type, header=get_droneAcq_header())


@_frontend.get("/get_lab_acquisitions")
@login_required
def get_lab_acquisitions():
    pivoting = get_labAcq_query()
    res_piv = db.session.execute(pivoting).all()

    result = {"data": list()}
    for r in res_piv:
        result["data"].append({k:r[k] for k in res_piv[0].keys()})

    return result


@_frontend.get("/get_drone_acquisitions")
@login_required
def get_drone_acquisitions():
    drones = db.session.query(site.c.name.label("sito"), drone_acq.c.lat.label("latitude"), drone_acq.c.lon.label("longitude"),\
        drone_acq.c.time, drone_acq.c.start_acq_time.label("start acq timestamp"), drone_acq.c.stop_acq_time.label("stop acq timestamp"),\
        drone_acq.c.mission, drone_acq.c.path, drone_acq.c.acquisition, drone_acq.c.z, drone_acq.c.start_band.label("bandaIniziale"),\
        drone_acq.c.stop_band.label("bandaFinale"), drone_acq.c.gamma).join(site).all()
    result = {"data": list()}
    for d in drones:
        result["data"].append({k:d[k] for k in drones[0].keys() if not k == "coords"})
    return result


@_frontend.get("/drone_acquisitions") 
@login_required
def drone_acquisitions():
    return render_template("droneAcq_table.html", title=current_user.username, tipo=current_user.role[0].type, header=get_droneAcq_header())


@_frontend.get("/laboratory_acquisitions") 
@login_required
def laboratory_acquisitions():
    return render_template("labAcq_table.html", title=current_user.username, tipo=current_user.role[0].type, header=get_labAcq_header())


@_frontend.route("/login", methods=["GET", "POST"]) 
def login():
    if request.method == "POST":
        username = request.form["username"]
        pwd = request.form["password"]
        if not username or not pwd:
            abort(401, message="Could not verify login")
        user = db.session.query(User_model).filter_by(username=username).first()
        if not user:
            flash('Email does not exist.', category='error')
            return render_template("login.html", user=current_user)
        if user.verified == False:
            flash('User not yet verified.', category='error')
        else:
            if check_password_hash(user.password, pwd):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=False)
                return render_template("labAcq_table.html", title=current_user.username, tipo=current_user.role[0].type, header=get_labAcq_header())
            else:
                flash('Incorrect password, try again.', category='error')

    return render_template("login.html", user=current_user)


@_frontend.get('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', category='success')
    return redirect(url_for('_frontend.login'))


@_frontend.post("/signup")
def signup():
    username = request.form["username"]
    email = request.form["email"]
    pwd = request.form["password"]
    if not username or not pwd:
        abort(401, message="Could not verify login")
    user = db.session.query(User_model).filter_by(username=username).one_or_none()
    if user:
        flash('Username already exist.', category='error')
    else:
        h_pwd = generate_password_hash(pwd, method="sha256")
        new_user = User_model(username=username, email=email, password=h_pwd, verified=False)
        db.session.add(new_user)

        # Set default role value to 'guest'
        r = db.session.query(Role_model).filter_by(type="guest").first()
        new_user.role.append(r)

        db.session.commit()
        flash('Sign up successfully!', category='success')

    return render_template("login.html", user=current_user)


@_frontend.get('/get_lab_acq_keys')
@login_required
def get_lab_acq_keys():
    return flask.jsonify(get_labAcq_header())


@_frontend.get('/get_drone_acq_keys')
@login_required
def get_drone_acq_keys():
    return flask.jsonify(get_droneAcq_header())


def get_droneAcq_header():
    header = db.session.query(site.c.name.label("sito"), drone_acq.c.lat.label("latitude"), drone_acq.c.lon.label("longitude"),\
        drone_acq.c.time, drone_acq.c.start_acq_time.label("start acq timestamp"), drone_acq.c.stop_acq_time.label("stop acq timestamp"),\
        drone_acq.c.mission, drone_acq.c.path, drone_acq.c.acquisition, drone_acq.c.z, drone_acq.c.start_band.label("bandaIniziale"),\
        drone_acq.c.stop_band.label("bandaFinale"), drone_acq.c.gamma).join(site).limit(1).first()
    if not header:
        header = {"No data available at the moment...":[]}
    return [elem for elem in header.keys() if not elem == "coords"]


def get_labAcq_header():
    query = get_labAcq_query(only_header=True)
    header = db.session.execute(query).first()

    if not header:
        header = {"No data available at the moment...":[]}

    return [elem for elem in header.keys()]


def get_labAcq_query(only_header=False):
    vars = [var[0] for var in db.session.query(variable.c.name).all()]

    query = """
    SELECT lab_acquisition.id, site.name AS sito, lab_acquisition.lat AS latitude, lab_acquisition.lon AS longitude, 
            lab_acquisition.time, lab_acquisition.nlab AS Nlab, lab_acquisition.nfield AS Ncampo, 
            lab_acquisition.depth AS depth_cm, lab_acquisition.gamma,
    """
    for var in vars:
        query += f"MAX(measure.value) FILTER (WHERE variable.name = '{var}') as {var},"
    query += """lab_acquisition.hyperspectral"""
    if only_header:
        query += """
        FROM lab_acquisition
                LEFT OUTER JOIN site ON site.id = lab_acquisition.site
                LEFT OUTER JOIN measure ON lab_acquisition.id = measure.id_lab_acquisition 
                LEFT OUTER JOIN variable ON variable.id = measure.id_variable
            GROUP BY lab_acquisition.id, sito
            ORDER BY lab_acquisition.id, sito
            LIMIT 1
        """
    else:
        query += """
        FROM lab_acquisition
                LEFT OUTER JOIN site ON site.id = lab_acquisition.site
                LEFT OUTER JOIN measure ON lab_acquisition.id = measure.id_lab_acquisition 
                LEFT OUTER JOIN variable ON variable.id = measure.id_variable
            GROUP BY lab_acquisition.id, sito
            ORDER BY lab_acquisition.id, sito
        """
    return sa.text(query)


def download_missing_models():
    """
    Download any models in DB which are not in local folder.
    """
    models_uploaded = db.session.query(model.c.name, model.c.path).all()

    for name, path in models_uploaded:
        if not os.path.isfile(path):
            to_download = db.session.query(model.c.file).filter(model.c.name == name).first()
            with open(path, mode='xb') as file:
                file.writelines(to_download)
    del models_uploaded