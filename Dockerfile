FROM python:3.11-buster

RUN pip install poetry && useradd -d /home/bank -U -m -u 1111 bank && mkdir /app

WORKDIR /home/bank/git

COPY --chown=bank:bank . .

USER root

RUN chown -R bank:bank /home/bank/git

USER bank

RUN poetry install

ENTRYPOINT ["poetry", "run", "python", "main.py"]
