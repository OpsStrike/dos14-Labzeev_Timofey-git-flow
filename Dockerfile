FROM python:3.11-buster

ARG PG_UID=1002
ARG PG_GID=1003

RUN pip install poetry && \
    useradd -d /home/bank -U -m -u 1111 bank && \
    mkdir /home/bank/git
    
RUN apt-get update\
    && apt-get install -y libpq-dev 

RUN useradd -d /home/postgres -U -m -u ${PG_UID} postgres \
    && usermod -u ${PG_UID} postgres \
    && groupmod -g ${PG_GID} postgres \

RUN mkdir -p /home/postgres
    
USER postgres   

COPY /app/secrets_decrypted.yml /home/postgres/ \
     && chmod 777 /home/postgres/secrets_decrypted.yml
    
WORKDIR /home/bank/git

COPY --chown=bank:bank . .

USER root

RUN chmod 777 /home/bank/git

USER bank

RUN poetry install

CMD sh -c "while [ ! -f /app/secrets_decrypted.yml ]; do sleep 2; done && poetry run python main.py"
