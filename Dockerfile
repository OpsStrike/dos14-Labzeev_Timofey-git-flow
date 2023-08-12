FROM python:3.11-buster

ARG PG_GID=1003

RUN pip install poetry && \
    useradd -d /home/bank -U -m -u 1111 bank && \
    groupmod -g ${PG_GID} postgres && \
    mkdir /home/bank/git
    
RUN apt-get update\
    && apt-get install -y libpq-dev 
    
WORKDIR /home/bank/git

COPY --chown=bank:bank . .

USER root

RUN chmod 777 /home/bank/git

USER bank

RUN poetry install

CMD sh -c "while [ ! -f /app/secrets_decrypted.yml ]; do sleep 2; done && poetry run python main.py"
