# Run Pignoletto Platform with docker-compose

## Before, how to set the IP:
In order to set the IP for Pignoletto Platform, go to [this line of code](./Makefile#L17) and set your desired IP with the port on which the service is deployed.

<hr>

## How to run the docker stack
* Create environment variables:

```
make env
```

* Create and run the containers:
```
docker-compose up [-d]
```



Open your browser at `http://<YOUR_IP>:<YOUR_PORT>` for Lizmap Map management (default is: *http://127.0.0.1:8080*).

Open your browser at `http://<YOUR_IP>:<YOUR_PORT>/pignoletto/login` for Pignoletto's platform (default is: *http://127.0.0.1:8080/pignoletto/login*).

<hr>

## Project structure

```
├── database               <- Database configuration
│   └── insert.sql            <- Database creation script
│
├── lizmap                 <- Lizmap plugin
│   ├── etc                   <- Folder containing configuration files
│   │   ├── nginx.conf           <- Nginx configuration file
│   │   └── ...
│   ├── instances             <- Folder which will contain the configuration files for the web-map application
│   ├── processing            <- Folder that contains the algorithms to be exploited in the web-map application
│   └── ...
│
├── pignoletto             <- Pignoletto Platform source code
│   ├── pignoletto            <- Main Python package
│   │   ├── _api                 <- API package
│   │   │   └── _api.py             <- Script managing API login and eventually other routes
│   │   ├── _frontend            <- Frontend package, manage the UI of the Web-App
│   │   │   ├── static              <- Folder containing Javascript, CSS and images of the Web-app
│   │   │   ├── templates           <- Folder containing Jinja2 templates of the Web-app
│   │   │   └── _frontend.py        <- Script managing the frontend routes
│   │   ├── QGISManager          <- QGISManager package, contains the classes that manage the QGIS project and the Lizmap configuration file
│   │   │   ├── media               <- Style template for the Web-map application
│   │   │   ├── lizmap_API.py       <- Class handling the generation of the Lizmap configuration file
│   │   │   ├── pignoletto.qgs      <- Template for the QGIS project
│   │   │   └── QGISManager.py      <- Class that exploit PyQGIS to generate the QGIS project
│   │   ├── __init__.py          <- Core script which initialize all classes, links blueprints, expose resources on the API and creates web-map configuration files
│   │   ├── config.json          <- Configuration parameters about Database connection and sensitive variables
│   │   ├── DBManager.py         <- Python class that manage the interaction between web-app and database
│   │   ├── models.py            <- through SQLAlchemy (Python SQL toolkit and Object Relational Mapper) maps the tables present in the DB in the application
│   │   └── resources.py         <- Defines the resources that can be exposed via API
│   ├── Dockerfile            <- It creates the Pignoletto's image 
│   ├── requirements.txt      <- Contains all the necessary Python libraries to run the application
│   ├── run.ini               <- uWSGI configuration file
│   ├── run.py                <- Python script that runs the application
│   └── wait-for-db.sh        <- Bash script waiting for database container to start before starting the pignoletto one
│
├── wps                    <- Lizmap WPS Web Client module
│
├── docker-compose.yml        <- Compose file that generates the Docker stack
├── Makefile                  <- It creates all the necessary environment variables
└── README.md
```