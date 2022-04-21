CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_raster;



CREATE TABLE IF NOT EXISTS public.site (
	id serial not null,
	name varchar(60) not null,
	description varchar(100),

	PRIMARY KEY (id)
);


CREATE TABLE IF NOT EXISTS public.drone_acquisition (
	id serial not null,
	lat float not null,
	lon float not null,
	time timestamp not null,
	site int,
	coords public.geometry,
	gamma float[],
	start_acq_time timestamp not null,
	stop_acq_time timestamp not null,
	mission varchar(30),
	path varchar(30),
	acquisition varchar(30),
	z int,
	start_band int not null,
	stop_band int not null,

	CONSTRAINT fk_da1
	FOREIGN KEY (site)
	REFERENCES public.site (id)
	ON UPDATE CASCADE
	ON DELETE RESTRICT,
	
	CONSTRAINT enforce_dims_coords CHECK ((public.st_ndims(coords) = 2)),
	CONSTRAINT enforce_geotype_geom CHECK (((public.geometrytype(coords) = 'POINT'::text) OR (coords IS NULL))),
	PRIMARY KEY (id)
);


CREATE TABLE IF NOT EXISTS public.images (
    id serial NOT NULL,
    file bytea NOT NULL,
    name character varying(30) NOT NULL,

	PRIMARY KEY (id)
);


CREATE TABLE IF NOT EXISTS public.variable (
	id serial not null,
	name varchar(50) not null,
	unit_of_measure varchar(50) not null,
	description varchar(2000),

	PRIMARY KEY (id)
);



CREATE TABLE IF NOT EXISTS public.model (
	id serial not null,
	name varchar(60) not null,
	path varchar(200) not null,
    file bytea NOT NULL,

	PRIMARY KEY (id)
);


CREATE TABLE IF NOT EXISTS public.estimation (
	id serial not null,
	time timestamp not null,
	drone_acquisition int not null,
	model int not null,
	site int,

	PRIMARY KEY (id),

	CONSTRAINT fk_estim1
	FOREIGN KEY (drone_acquisition)
	REFERENCES public.drone_acquisition (id)
	ON UPDATE CASCADE
	ON DELETE RESTRICT,

	CONSTRAINT fk_estim2
	FOREIGN KEY (model)
	REFERENCES public.model (id)
	ON UPDATE CASCADE
	ON DELETE RESTRICT,


	CONSTRAINT fk_estim3
	FOREIGN KEY (site)
	REFERENCES public.site (id)
	ON UPDATE CASCADE
	ON DELETE RESTRICT
);


CREATE TABLE IF NOT EXISTS public.estimated_value (
	id_estimation int not null,
	id_variable int not null,
	value float not null,

	PRIMARY KEY (id_estimation, id_variable),

	CONSTRAINT fk_estval1
	FOREIGN KEY (id_estimation)
	REFERENCES public.estimation (id)
	ON UPDATE CASCADE
	ON DELETE RESTRICT,

	CONSTRAINT fk_estval2
	FOREIGN KEY (id_variable)
	REFERENCES public.variable (id)
	ON UPDATE CASCADE
	ON DELETE RESTRICT
);


CREATE TABLE IF NOT EXISTS public.lab_acquisition (
	id varchar(20) not null,
	
	lat float not null,
	lon float not null,
	time timestamp not null,
	nlab varchar(50) not null,
	nfield varchar(50) not null,
	depth varchar(50) not null,
	site int,
	coords public.geometry,
	hyperspectral float[] not null,
	gamma float[],

	CONSTRAINT fk_da1
	FOREIGN KEY (site)
	REFERENCES public.site (id)
	ON UPDATE CASCADE
	ON DELETE RESTRICT,
	
	CONSTRAINT enforce_dims_coords CHECK ((public.st_ndims(coords) = 2)),
	CONSTRAINT enforce_geotype_geom CHECK (((public.geometrytype(coords) = 'POINT'::text) OR (coords IS NULL))),
	PRIMARY KEY (id)
);



CREATE TABLE IF NOT EXISTS public.measure (
	id_lab_acquisition varchar(20) not null,
	id_variable int not null,
	value float not null,

	PRIMARY KEY (id_lab_acquisition, id_variable),

	CONSTRAINT fk_measure1
	FOREIGN KEY (id_lab_acquisition)
	REFERENCES public.lab_acquisition (id)
	ON UPDATE CASCADE
	ON DELETE RESTRICT,

	CONSTRAINT fk_measure2
	FOREIGN KEY (id_variable)
	REFERENCES public.variable (id)
	ON UPDATE CASCADE
	ON DELETE RESTRICT
);



CREATE TABLE IF NOT EXISTS public.raster_master (
	id serial not null,
	layer_name varchar(60) not null,
	table_name varchar(60) not null,
	description varchar(100),
	visible boolean DEFAULT true,

	PRIMARY KEY (id)
);



CREATE TABLE IF NOT EXISTS public.role (
	id serial NOT NULL,
	type varchar(30) NOT NULL,
	PRIMARY KEY (id)
);


CREATE TABLE IF NOT EXISTS public."user"(
    id serial NOT NULL,
    username character varying COLLATE pg_catalog."default" NOT NULL,
    password character varying COLLATE pg_catalog."default" NOT NULL,
    email character varying COLLATE pg_catalog."default" NOT NULL,
    verified boolean NOT NULL,
    CONSTRAINT user_pkey PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public.user_role(
	user_id int,
	role_id int,
	PRIMARY KEY (user_id, role_id),
	CONSTRAINT fk_user_id FOREIGN KEY(user_id) REFERENCES public.user(id) ON UPDATE CASCADE ON DELETE RESTRICT,
	CONSTRAINT fk_role_id FOREIGN KEY(role_id) REFERENCES public.role(id) ON UPDATE CASCADE ON DELETE RESTRICT
);



INSERT INTO public.variable 
    (id, name, unit_of_measure, description)
VALUES
	(1, 'pH_H2O', '', 'pH in H2O'),
	(2, 'CaCO3', 'g/kg', ''),
	(3, 'OC', '%', ''),
	(4, 'N', '%', ''),
	(5, 'Sabbia', 'g/kg', ''),
	(6, 'Limo', 'g/kg', ''),
	(7, 'Argilla', 'g/kg', ''),
	(8, 'Torio', 'Bq/kg', ''),
	(9, 'Radio', 'Bq/kg', ''),
	(10, 'Potassio', 'Bq/kg', ''),
	(11, 'Cesio', 'Bq/kg', '');



INSERT INTO public.role
	(id, type)
VALUES
	(1, 'admin'),
	(2, 'guest');



INSERT INTO public.site
	(id, name, description)
VALUES 
	(1, 'sito1', ''),
	(2, 'sito2', ''),
	(3, 'sito3', ''),
	(4, 'sito4', ''),
	(5, 'sito5', '');



INSERT INTO public.lab_acquisition
	(id, lat, lon, "time", nlab, nfield, depth, site, coords, hyperspectral, gamma)
VALUES 
	('DL-TEST-0', 1596243.4, 4958955.14, CURRENT_TIMESTAMP, 'test-lab-1', 'test-field-1', 'test-depth-1', 1, ST_GeomFromText('POINT(1596243.4 4958955.14)', 3003), '{0.9707,0.9685}', '{0.332,0.712}'),
	('DL-TEST-1', 1596244.45, 4958955.132, CURRENT_TIMESTAMP, 'test-lab-1', 'test-field-2', 'test-depth-1', 2, ST_GeomFromText('POINT(1596244.45 4958955.132)', 3003), '{0.7668,0.345}', '{0.5455,0.8478}'),
	('DL-TEST-2', 1596245.421, 4958955.543, CURRENT_TIMESTAMP, 'test-lab-2', 'test-field-3', 'test-depth-2', 3, ST_GeomFromText('POINT(1596245.421 4958955.543)', 3003), '{0.668,0.9683}', '{0.836,0.3367}'),
	('DL-TEST-3', 1596246.143, 4958955.165, CURRENT_TIMESTAMP, 'test-lab-2', 'test-field-1', 'test-depth-2', 4, ST_GeomFromText('POINT(1596246.143 4958955.165)', 3003), '{0.9702,0.968}', '{0.9393,0.885}'),
	('DL-TEST-4', 1596247.234, 4958955.77, CURRENT_TIMESTAMP, 'test-lab-2', 'test-field-1', 'test-depth-3', 5, ST_GeomFromText('POINT(1596247.234 4958955.77)', 3003), '{0.65432,0.4231}', '{0.6635,0.85639}');



INSERT INTO public.drone_acquisition
	(id, lat, lon, "time", site, coords, gamma, start_acq_time, stop_acq_time, mission, path, acquisition, z, start_band, stop_band)
VALUES 
	(1, 1596295.98, 4958966.88, CURRENT_TIMESTAMP, 1, ST_GeomFromText('POINT(1596295.98 4958966.88)', 3003), '{0.36442,0.7666}', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'TEST-MISSION-1', 'TEST-PATH-1', 'TEST-ACQ-1', 4, 1, 6),
	(2, 1596299.954, 4958965.12, CURRENT_TIMESTAMP, 2, ST_GeomFromText('POINT(1596299.954 4958965.12)', 3003), '{0.12122,0.1126}', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'TEST-MISSION-1', 'TEST-PATH-2', 'TEST-ACQ-2', 9, 2, 4),
	(3, 1596298.33, 4958964.54, CURRENT_TIMESTAMP, 3, ST_GeomFromText('POINT(1596298.33 4958964.54)', 3003), '{0.36453242,0.5446}', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'TEST-MISSION-2', 'TEST-PATH-3', 'TEST-ACQ-3', 5, 1, 3),
	(4, 1596299.75, 4958967.77, CURRENT_TIMESTAMP, 4, ST_GeomFromText('POINT(1596299.75 4958967.77)', 3003), '{0.76542,0.7345}', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'TEST-MISSION-2', 'TEST-PATH-3', 'TEST-ACQ-4', 7, 1, 7),
	(5, 1596294.11, 4958968.432, CURRENT_TIMESTAMP, 5, ST_GeomFromText('POINT(1596294.11 4958968.432)', 3003), '{0.88442,0.77996}', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'TEST-MISSION-3', 'TEST-PATH-4', 'TEST-ACQ-4', 1, 3, 5);


INSERT INTO public.measure
	(id_lab_acquisition, id_variable, value)
VALUES
	('DL-TEST-0',	1,	68.9),
	('DL-TEST-0',	2,	0),
	('DL-TEST-0',	3,	17.51),
	('DL-TEST-0',	4,	0.318),
	('DL-TEST-0',	5,	23),
	('DL-TEST-0',	6,	94),
	('DL-TEST-0',	7,	83),
	('DL-TEST-0',	8,	239.5),
	('DL-TEST-0',	9,	25.9),
	('DL-TEST-0',	10,	367),
	('DL-TEST-0',	11,	4.69),
	('DL-TEST-1',	1,	64.8),
	('DL-TEST-1',	2,	0),
	('DL-TEST-1',	3,	31.16),
	('DL-TEST-1',	4,	0.536),
	('DL-TEST-1',	5,	37),
	('DL-TEST-1',	6,	79),
	('DL-TEST-1',	7,	84),
	('DL-TEST-1',	8,	218.9),
	('DL-TEST-1',	9,	311.2),
	('DL-TEST-1',	10,	40),
	('DL-TEST-1',	11,	81.8),
	('DL-TEST-2',	1,	61.9),
	('DL-TEST-2',	2,	0),
	('DL-TEST-2',	3,	22.13),
	('DL-TEST-2',	4,	0.27),
	('DL-TEST-2',	5,	35),
	('DL-TEST-2',	6,	56),
	('DL-TEST-2',	7,	329),
	('DL-TEST-2',	8,	282.7),
	('DL-TEST-2',	9,	4.9),
	('DL-TEST-2',	10,	246),
	('DL-TEST-2',	11,	22.8),
	('DL-TEST-3',	1,	2.6),
	('DL-TEST-3',	2,	347),
	('DL-TEST-3',	3,	0.591),
	('DL-TEST-3',	4,	0.19),
	('DL-TEST-3',	5,	235),
	('DL-TEST-3',	6,	414),
	('DL-TEST-3',	7,	252),
	('DL-TEST-3',	8,	24.92),
	('DL-TEST-3',	9,	29.7),
	('DL-TEST-3',	10,	31),
	('DL-TEST-3',	11,	99.1),
	('DL-TEST-4',	1,	69.7),
	('DL-TEST-4',	2,	0),
	('DL-TEST-4',	3,	18.72),
	('DL-TEST-4',	4,	0.821),
	('DL-TEST-4',	5,	18),
	('DL-TEST-4',	6,	481),
	('DL-TEST-4',	7,	11),
	('DL-TEST-4',	8,	3.5),
	('DL-TEST-4',	9,	2.4),
	('DL-TEST-4',	10,	38),
	('DL-TEST-4',	11,	3.95);	