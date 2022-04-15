import pandas as pd
import numpy as np
from collections import OrderedDict
from datetime import datetime
from tqdm import tqdm
import os

from .models import (
    CreateView, 
    variable, 
    measure, 
    lab_acq, 
    site, 
    model, 
    estimation, 
    estimated_value, 
    variable_unique,
    drone_acq,
    raster_master
)
from pignoletto import engine, db
import sqlalchemy as sa
from geoalchemy2 import func


def is_float(element):
    try:
        float(element)
        return True
    except ValueError:
        return False


class DBManager(object):
    def __init__(self):
        # initialize variable containing the views
        self.views = OrderedDict({'lab_acquisition':OrderedDict(), 'estimated':OrderedDict()})


    def get_views(self): 
        return self.views


    def delete_all_lab_acquisition(self):
        db.session.query(measure).delete()
        db.session.query(lab_acq).delete()
        db.session.commit()


    def delete_lab_acquisition(self, lab_id):
        # delete from measure
        db.session.query(measure).filter(measure.c.id_lab_acquisition == lab_id).delete()
        # delete from acquisition
        db.session.query(lab_acq).filter(lab_acq.c.id == lab_id).delete()
        db.session.commit()


    def delete_drone_acquisition(self, da_id):
        # delete from estimated value
        sub_q = db.session.query(estimation.c.id).filter(estimation.c.drone_acquisition == da_id)
        db.session.query(estimated_value).filter(estimated_value.c.id_estimation.in_(sub_q)).delete()
        # delete from estimation
        db.session.query(estimation).filter(estimation.c.id == da_id).delete()
        db.session.commit()

    
    def delete_from_drone_acquisition(self, da_id):
        db.session.query(drone_acq).filter(drone_acq.c.id == da_id).delete()
        db.session.commit()


    def insert_lab_acquisition(self, csv, sep=','):
        # define mapping between variables names
        header_mapping = {
            'ID': 'id',
            'Sito': 'site',
            'Est': 'lon',
            'Nord': 'lat',
            '#lab': 'nlab',
            '#campo': 'nfield',
            'prof. cm': 'depth',
            'pH H2O': 'pH_H2O',
            'CaCO3 g/kg': 'CaCO3',
            'C org %': 'OC',
            'N tot %': 'N',
            'Sabbia g/kg': 'Sabbia',
            'Limo g/kg': 'Limo',
            'Argilla g/kg': 'Argilla',
            'Torio Bq/kg': 'Torio',
            'Radio Bq/kg': 'Radio',
            'Potassio Bq/kg': 'Potassio',
            'Cesio Bq/kg': 'Cesio',
        }

        # read file
        df = pd.read_csv(csv, sep=sep)

        # check that the variables in the csv are contained in the dataset
        for key in header_mapping:
            if not key in df.columns:
                raise ValueError(f'Variable {key} not present in CSV file.')

        # convert headers
        new_cols = []
        for i in range(len(df.columns)):
            if df.columns[i] in header_mapping:
                new_cols.append(header_mapping[df.columns[i]])
            else:
                new_cols.append(df.columns[i])
        df.columns = new_cols

        # get headers of hyperspectral signal
        hyper_headers = [col for col in df.columns if is_float(col)]

        # get all sites
        cur_sites = list(df['site'].unique())

        # insert them if not present
        for cur_site in cur_sites:
            res = db.session.query(site).filter(site.c.name == cur_site).first()
            if res is None:
                s = site.insert().values(name=cur_site)
                db.session.execute(s)

        # get site ids
        site_mapping = dict(db.session.query(site.c.name, site.c.id).all())

        # get variables ids
        var_mapping = dict(db.session.query(variable.c.name, variable.c.id).all())

        # for each sample
        for i in range(len(df)):
            # get it
            cur_sample = df.iloc[i]
            # get hyperspectral signal
            cur_hyper = cur_sample[hyper_headers].tolist()
            # create acquisition
            cur_id, cur_lat, cur_lon, cur_nlab, cur_nfield, cur_depth, cur_site = \
                  cur_sample[['id','lat','lon','nlab','nfield','depth', 'site']]
            cur_site_id = site_mapping[cur_site]
            # define current time stamp
            cur_time = datetime.now()
            # delete acquisition from db
            self.delete_lab_acquisition(cur_id)
            
            # perform insert query
            q = lab_acq.insert().values(id=cur_id, lat=cur_lat, lon=cur_lon, time=cur_time, hyperspectral=cur_hyper,\
                        nlab=cur_nlab, nfield= cur_nfield, depth=cur_depth, site=cur_site_id,\
                        coords=func.ST_GeomFromText(f"POINT({cur_lon} {cur_lat})", 3003))
            db.session.execute(q)

            # for each var add its measure
            for cur_var in ['pH_H2O', 'CaCO3', 'OC', 'N', 'Sabbia', 'Limo', 'Argilla', 'Torio', 'Radio', 'Potassio', 'Cesio']:
                cur_var_id = var_mapping[cur_var]
                cur_var_val = cur_sample[cur_var]
                # TODO: in future do not accept nan or non-float values
                if cur_var_val == 'n.d.': continue
                cur_var_val = float(cur_var_val)
                q = measure.insert().values(id_lab_acquisition=cur_id, id_variable=cur_var_id, value=cur_var_val)
                if not is_float(cur_var_val) or np.isnan(cur_var_val): continue
                db.session.execute(q)
        db.session.commit()


    def insert_drone_acquisition(self, csv, sep=','):
        header_mapping = {
            'start acq timestamp': 'start_acq_time',
            'stop acq timestamp': 'stop_acq_time',
            'site': 'site',
            'mission': 'mission',
            'path': 'path',
            'acquisition': 'acquisition',
            'longitude': 'lon',
            'latitude': 'lat',
            'z': 'z',
            'bandaIniziale': 'start_band',
            'bandaFinale': 'stop_band',
            'gamma': "gamma"
        }

        # read file
        df = pd.read_csv(csv, sep=sep)

        # check that the variables in the csv are contained in the dataset
        for key in header_mapping:
            if not key in df.columns:
                raise ValueError(f'Variable {key} not present in CSV file.')

        # convert headers
        new_cols = []
        for i in range(len(df.columns)):
            if df.columns[i] in header_mapping:
                new_cols.append(header_mapping[df.columns[i]])
            else:
                new_cols.append(df.columns[i])
        df.columns = new_cols

        df['start_acq_time'] = pd.to_datetime(df['start_acq_time'])
        df['stop_acq_time'] = pd.to_datetime(df['stop_acq_time'])
        df['gamma'] = df['gamma'].apply(eval)

        # get all sites
        cur_sites = list(df['site'].unique())

        # insert them if not present
        for cur_site in cur_sites:
            res = db.session.query(site).filter(site.c.name == cur_site).first()
            if res is None:
                s = site.insert().values(name=cur_site)
                db.session.execute(s)

        # get site ids
        site_mapping = dict(db.session.query(site.c.name, site.c.id).all())

        # for each sample
        for i in range(len(df)):
            # get it
            cur_sample = df.iloc[i]
            # create acquisition
            cur_start_acq_time, cur_stop_acq_time, cur_site, cur_mission,\
                cur_path, cur_acquisition, cur_lat, cur_lon, cur_z,\
                cur_start_band, cur_stop_band, cur_gamma = \
                    cur_sample[
                        ['start_acq_time', 'stop_acq_time', 'site', 'mission',\
                        'path', 'acquisition', 'lat', 'lon', 'z', 'start_band',\
                        'stop_band', 'gamma']
                    ]
            # check timestamp consistency
            if cur_stop_acq_time < cur_start_acq_time:
                continue
            # check band consistency
            if cur_stop_band < cur_start_band:
                continue
            # define current time stamp
            cur_time = datetime.now()
            cur_site_id = site_mapping[cur_site]
            # perform insert query
            q = drone_acq.insert().values(
                start_acq_time = cur_start_acq_time,
                stop_acq_time= cur_stop_acq_time,
                site = cur_site_id,
                mission = cur_mission,
                path = cur_path,
                acquisition = cur_acquisition,
                lat = cur_lat,
                lon = cur_lon,
                coords = func.ST_GeomFromText(f"POINT({cur_lon} {cur_lat})", 3003),
                z = cur_z.item(),
                start_band = cur_start_band.item(),
                stop_band = cur_stop_band.item(),
                gamma = cur_gamma,
                time = cur_time
            )
            db.session.execute(q)
        db.session.commit()


    def point_sampling_raster_from_single_table(self, table, lat, lon, epsg=4326, nodata_val=-99999):
        qry = sa.text(f'''
        SELECT 
            ST_Value(rast, 1, 
                (ST_Dump(
                    ST_Multi(
                        ST_SetSRID(ST_Point({lon}, {lat}), {epsg})
                    )
                )).geom
            ) AS val
        FROM {table}
        WHERE ST_Intersects(rast, ST_SetSRID(ST_Point({lon}, {lat}), {epsg})::geometry, 1);
        ''')
        res = db.session.execute(qry).first()

        # check if it has at least one element
        if len(res) > 0:
            return res[0]
        return nodata_val


    def point_sampling_raster(self, tables, lat, lon, epsg=4326, nodata_val=-99999):
        # convert table to list if a single string is passed
        if not isinstance(tables, list):
            tables = [tables]
        # create output
        out = OrderedDict()
        # for each table/raster
        for cur_table in tables:
            # get the feature
            cur_feat = self.point_sampling_raster_from_single_table(cur_table, lat, lon, epsg=epsg, nodata_val=nodata_val)
            # append to output
            out[cur_table] = cur_feat
        # return the collected samples
        return out


    def point_sampling_raster_from_csv(self, csv, tables, epsg=4326, sep=',', lat_col='GPS_LAT', lon_col='GPS_LONG', nodata_val=-99999):
        # import pandarallel
        # from pandarallel import pandarallel
        # pandarallel.initialize(nb_workers=8, progress_bar=True)
        # read csv
        df = pd.read_csv(csv, sep=sep)
        # keep only coordinates
        df = df[[lat_col, lon_col]]
        # add empty cols
        for cur_table in tables: df[cur_table] = nodata_val
        # fill them
        for index, x in tqdm(df.iterrows(), total=len(df)):
            vals = self.point_sampling_raster(tables, x[lat_col], x[lon_col], epsg=epsg, nodata_val=nodata_val)
            for cur_table in tables:
                # x[cur_table] = vals[cur_table]
                df.loc[index, cur_table] = vals[cur_table]
        # return dataframe with retrieved info
        return df


    def create_views(self):
        # init variable containing views names
        self.views = OrderedDict({'lab_acquisition':OrderedDict(), 'estimated':OrderedDict()})

        # get variables involved in lab acquisition
        var_names = db.session.query(variable.c.id, variable.c.name).filter(
                    variable.c.id == measure.c.id_variable,
                    lab_acq.c.id == measure.c.id_lab_acquisition
                ).order_by(variable.c.name).distinct().all()

        # create views for lab acquisition
        for cur_var_id, cur_var_name in var_names:
            # define view name
            view_name = f'lab_{cur_var_name}'.lower()
            view = CreateView(view_name, sa.select([lab_acq.c.id, lab_acq.c.coords, measure.c.value])\
                    .where(lab_acq.c.id == measure.c.id_lab_acquisition)\
                    .where(lab_acq.c.site == site.c.id)\
                    .where(measure.c.id_variable == variable.c.id)\
                    .where(variable.c.id == cur_var_id))
            engine.execute(view)
            # append name of just-created view
            self.views['lab_acquisition'][cur_var_name] = view_name


        # get models involved in estimation
        models = db.session.query(model.c.id, model.c.name).filter(
                model.c.id == estimation.c.model,
            ).distinct().all()

        # for each model
        for cur_model_id, cur_model_name in models:
            # create placeholder
            self.views['estimated'][cur_model_name] = OrderedDict()
            
            # get the predicted variables
            cur_model_vars = db.session.query(variable_unique.c.id, variable_unique.c.name).filter(
                variable_unique.c.id == estimated_value.c.id_variable,
                estimation.c.id == estimated_value.c.id_estimation,
                model.c.id == estimation.c.model,
                model.c.id == cur_model_id
            ).order_by(variable_unique.c.name).all()

            # for each variable
            for cur_var_id, cur_var_name in cur_model_vars:
                # define view name
                view_name = f'est_{cur_model_name}_{cur_var_name}'.lower()
                # create view
                view = CreateView(view_name, 
                        sa.select([drone_acq.c.id, drone_acq.c.coords, estimated_value.c.value])\
                            .where(drone_acq.c.id == estimation.c.drone_acquisition)\
                            .where(estimation.c.model == model.c.id)\
                            .where(estimation.c.id == estimated_value.c.id_estimation)\
                            .where(estimated_value.c.id_variable == variable.c.id)\
                            .where(variable.c.id == cur_var_id)\
                            .where(model.c.id == cur_model_id))
                engine.execute(view)
                # append
                self.views['estimated'][cur_model_name][cur_var_name] = view_name

        db.session.commit()
        # return the views that need to be rendered
        return self.views


    def get_rasters(self):
        return db.session.query(raster_master.c.id, 
                                raster_master.c.layer_name,
                                raster_master.c.table_name)\
                                .filter(raster_master.c.visible == True).all()


    def insert_raster(self, raster_fn, table_name=None, target_epsg=4326, nodata_val=0):
        # get path of raster
        raster_path = os.path.dirname(raster_fn)
        # define temporary raster
        temp_raster = os.path.join(raster_path, 'tmp.tif')
        # convert to target epsg
        os.system(f"gdalwarp -t_srs EPSG:{target_epsg} -overwrite {raster_fn} {temp_raster}")
        # send to db
        os.system( \
            f"raster2pgsql -s {target_epsg} -N {nodata_val} -d -C -I -M {temp_raster} -t 256x256 public.raster_{table_name} | " + \
            f"psql -h {self.host} -p {self.port} -U {self.user} -d {self.database}" \
        )
        # remove temporary raster
        os.remove(temp_raster)


    def insert_gkpg(self, gpkg_path):
        cmd = f'ogr2ogr -f PostgreSQL "PG:user={self.user} password={self.password} ' + \
              f'dbname={self.database} host={self.host} port={self.port}" {gpkg_path}'
        os.system(cmd)