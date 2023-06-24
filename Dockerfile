FROM python:3.11-buster

RUN pip install poetry && useradd -d /home/bank -U -m -u 1111 bank && mkdir /app

WORKDIR /home/bank/git

USER bank

COPY --chown=bank:bank . .

RUN find /home/bank/git -type d -exec chmod 755 {} \; && \
    find /home/bank/git -type f -exec chmod 644 {} \;

RUN poetry install

ENTRYPOINT ["poetry", "run", "python", "main.py"]
