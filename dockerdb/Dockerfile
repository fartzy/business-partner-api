FROM postgres:14.5-alpine


COPY ./initdb.sh /docker-entrypoint-initdb.d/
COPY ./postgresql.conf /etc/postgresql/

RUN chmod a+r /docker-entrypoint-initdb.d/*