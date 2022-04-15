FROM postgis/postgis:14-3.2
#FROM postgres:latest

COPY ./init.sql /docker-entrypoint-initdb.d/
COPY ./insert.sql /docker-entrypoint-initdb.d/

ENTRYPOINT ["docker-entrypoint.sh"]

EXPOSE 54320

CMD ["postgres"]