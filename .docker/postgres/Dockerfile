FROM postgres:9.6-alpine

ADD init-db.sh /docker-entrypoint-initdb.d/init-db.sh

#ENV VAULT_PASS ${VAULT_PASS}
#ENV REDCAP_PASS ${REDCAP_PASS}

RUN chmod a+x /docker-entrypoint-initdb.d/init-db.sh 
