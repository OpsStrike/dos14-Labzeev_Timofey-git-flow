FROM python:3.11-buster

RUN pip install poetry && useradd -d /home/bank -U -m -u 1111 bank && mkdir /app

WORKDIR /home/bank/git

COPY --chown=bank:bank . .

USER bank

RUN poetry install

EXPOSE 5001

ENTRYPOINT ["poetry", "run", "python", "main.py"]
