from sqlalchemy import Table, Column, Index
from flask_login import UserMixin
from geoalchemy2 import Geometry

from pignoletto import meta, db, engine


# Define methods for views
from sqlalchemy.schema import DDLElement
from sqlalchemy.ext import compiler
class CreateView(DDLElement):
    def __init__(self, name, selectable, materialized=False):
        self.name = name
        self.selectable = selectable
        self.materialized = materialized
@compiler.compiles(CreateView)
def compile_create_materialized_view(element, compiler, **kw):
    return 'CREATE OR REPLACE {}VIEW {} AS {}'.format(
        'MATERIALIZED ' if element.materialized else '',
        compiler.dialect.identifier_preparer.quote(element.name),
        compiler.sql_compiler.process(element.selectable, literal_binds=True),
    )

class DropView(DDLElement):
    def __init__(self, name, materialized=False, cascade=False):
        self.name = name
        self.materialized = materialized
        self.cascade = cascade
@compiler.compiles(DropView)
def compile_drop_materialized_view(element, compiler, **kw):
    return 'DROP {}VIEW IF EXISTS {} {}'.format(
        'MATERIALIZED ' if element.materialized else '',
        compiler.dialect.identifier_preparer.quote(element.name),
        'CASCADE' if element.cascade else ''
    )


### Subclass of Geometry, otherwise when creating the view it will save 'coords' as bytea type instead of geometry
class new_Geometry(Geometry):
    from geoalchemy2.elements import WKBElement
    from_text = 'ST_GeomFromEWKB'
    as_binary = 'ST_GeomFromEWKB'
    ElementType = WKBElement
lab_acq = Table('lab_acquisition', meta, 
            Column('coords', new_Geometry('POINT', srid=4326)),
            # additional Column objects which require no change are reflected normally
            autoload_with=engine)
drone_acq = Table('drone_acquisition', meta, 
            Column('coords', new_Geometry('POINT', srid=4326)),
            autoload_with=engine)
estimated_value = Table("estimated_value", meta, autoload=True, autoload_with=engine)
estimation = Table("estimation", meta, autoload=True, autoload_with=engine)
measure = Table("measure", meta, autoload=True, autoload_with=engine)
model = Table("model", meta, autoload=True, autoload_with=engine)
#raster_c_flow = Table("raster_c_flow", meta, autoload=True, autoload_with=engine)
#raster_c_gen = Table("raster_c_gen", meta, autoload=True, autoload_with=engine)
#raster_c_long = Table("raster_c_long", meta, autoload=True, autoload_with=engine)
#raster_c_max = Table("raster_c_max", meta, autoload=True, autoload_with=engine)
#raster_c_min = Table("raster_c_min", meta, autoload=True, autoload_with=engine)
#raster_c_plane = Table("raster_c_plane", meta, autoload=True, autoload_with=engine)
#raster_c_prof = Table("raster_c_prof", meta, autoload=True, autoload_with=engine)
#raster_c_tang = Table("raster_c_tang", meta, autoload=True, autoload_with=engine)
#raster_c_tot = Table("raster_c_tot", meta, autoload=True, autoload_with=engine)
#raster_c_tran = Table("raster_c_tran", meta, autoload=True, autoload_with=engine)
#raster_exposition = Table("raster_exposition", meta, autoload=True, autoload_with=engine)
raster_master = Table("raster_master", meta, autoload=True, autoload_with=engine)
#raster_ridge = Table("raster_ridge", meta, autoload=True, autoload_with=engine)
#raster_slope = Table("raster_slope", meta, autoload=True, autoload_with=engine)
#raster_valley = Table("raster_valley", meta, autoload=True, autoload_with=engine)
#shape_landuse = Table("shape_landuse", meta, autoload=True, autoload_with=engine)
site = Table("site", meta, autoload=True, autoload_with=engine)
spatial_ref_sys = Table("spatial_ref_sys", meta, autoload=True, autoload_with=engine)
variable = Table("variable", meta, autoload=True, autoload_with=engine)
# use Index in order to apply the unique function for queries poiting this table
variable_unique = Index('variable_unique', variable.c.id, variable.c.name, unique=True)

images = Table("images", meta, autoload=True, autoload_with=engine)


User_Role_model = db.Table("user_role",
    db.Column('role_id', db.ForeignKey('role.id')),
    db.Column('user_id', db.ForeignKey('user.id'))
)

class Role_model(db.Model):
    __tablename__ = "role"
    # Define columns
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.String(30), nullable=False)
    user = db.relationship("User_model", secondary=User_Role_model, back_populates="role")
    
    def as_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "user": self.user
        }

class User_model(db.Model, UserMixin):
    __tablename__ = "user"
    # Define columns
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    verified = db.Column(db.Boolean, nullable=False)
    role = db.relationship("Role_model", secondary=User_Role_model, back_populates="user")

    def as_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "password": self.password,
            "verified": self.verified,
            "role": self.role
        }