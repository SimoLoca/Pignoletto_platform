from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import json
from flask_restful import Api
from flask_login import LoginManager
from sqlalchemy import create_engine, MetaData
import os


app = Flask(__name__)
app.config.from_file("./config.json", json.load)

engine = create_engine(app.config.get("SQLALCHEMY_DATABASE_URI"), pool_recycle=3600)
meta = MetaData()

db = SQLAlchemy(app, metadata=meta)
api = Api(app)
login_manager = LoginManager(app)


from .DBManager import DBManager
db_manager = DBManager()


from pignoletto._frontend._frontend import _frontend
login_manager.login_view = 'login'

from pignoletto._api._api import _api
BASE = "/api/v0.1/"

app.register_blueprint(_frontend, url_prefix="/pignoletto")
app.register_blueprint(_api, url_prefix=BASE)

from pignoletto.resources import (
	DroneAcquisition,
	DroneAcquisitions
)
api.add_resource(DroneAcquisition, BASE + "/drone")
api.add_resource(DroneAcquisitions, BASE + "/drones")

def create_views():
	from .QGISManager import QGISManager
	lizmap_path = "./lizmap/instances/"
	if os.path.isdir(os.path.join(lizmap_path, "pignoletto")):
		final_path = os.path.join(lizmap_path, "pignoletto/pignoletto.qgs")
	else:
		os.makedirs(os.path.join(lizmap_path, "pignoletto"))
		final_path = os.path.join(lizmap_path, "pignoletto/pignoletto.qgs")
	qgis_manager = QGISManager(final_path)
	views = db_manager.create_views()
	# generate layers corresponding to created views
	for cur_group in views.keys():
		# create group
		qgis_manager.create_group(cur_group)
		# for each element
		for cur_element in views[cur_group]:
			# TODO: check if it's a layer to add or a subgroup
			qgis_manager.add_PostGIS_vector_layer(
						host_name = app.config.get("IP"), 
						port = app.config.get("PORT"), 
						db_name = app.config.get("DB_NAME"), 
						username = app.config.get("USERNAME"),
						password = app.config.get("PASSWORD"), 
						schema = app.config.get("SCHEMA"),
						table_name = views[cur_group][cur_element],
						geomColumn = "coords",
						layer_name = cur_element,
						pk='id', filter=None, group=None)
			# move in group
			qgis_manager.move_layer_in_group(cur_group, cur_element)

	# view all rasters
	qgis_manager.create_group('rasters')
	rasters = db_manager.get_rasters()
	# for each raster
	for cur_raster_id, cur_raster_name, cur_raster_table in rasters:
		# create layer
		qgis_manager.add_PostGIS_raster_layer(
			host_name = app.config.get("IP"), 
			port = app.config.get("PORT"), 
			db_name = app.config.get("DB_NAME"), 
			username = app.config.get("USERNAME"),
			password = app.config.get("PASSWORD"), 
			schema = app.config.get("SCHEMA"),
			table_name = cur_raster_table,
			num_classes=100, color="Viridis",
			layer_name=cur_raster_name, pk=None, filter=None, group=None
		)
		# move in subgroup
		qgis_manager.move_layer_in_group('rasters', cur_raster_name) 

	# Set WFS in order to use lizmap plugins
	qgis_manager.set_WFSCapabilities()

	# create lizmap configuration
	qgis_manager.create_Lizmap_configuration(tooltip=True, formfilter=True, attributeTable=True)

create_views()
