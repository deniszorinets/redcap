FROM vault:latest 

ADD vault-conf.sh /vault-conf.sh
ADD vault-unseal.sh /vault-unseal.sh

RUN chmod a+x /vault-conf.sh && chmod a+x /vault-unseal.sh 

CMD /vault-conf.sh && vault server -config /vault/config/vault.json 
