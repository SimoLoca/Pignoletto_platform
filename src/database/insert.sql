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
	(2, 'CaCO3', 'g/kg', 'Carbonato di calcio. È il maggiore componente del calcare sospeso in acqua e il principale responsabile della sua durezza.'),
	(3, 'OC', '%', 'Carbonio Organico.", "Contribuisce al ricambio dei nutrienti, alla capacità di scambio cationico, alla struttura del suolo, alla ritenzione e alla disponibilità idrica, al degrado degli inquinanti, alle emissioni di gas a effetto serra e al potere tampone del suolo.'),
	(4, 'N', '%', 'Fondamentale per la crescita delle parti verdi della pianta, in particolare germogli e foglie.'),
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