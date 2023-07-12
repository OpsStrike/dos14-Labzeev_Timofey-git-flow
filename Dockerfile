FROM python:3.11-buster

RUN pip install poetry && useradd -d /home/bank -U -m -u bank && mkdir /home/bank/git

WORKDIR /home/bank/git

COPY --chown=bank:bank . .

USER root

RUN chmod 777 /home/bank/git

USER bank

RUN poetry install

ENTRYPOINT ["poetry", "run", "python", "main.py"]
