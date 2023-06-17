FROM python:3.11-buster

RUN apt-get update && apt-get install -y nginx

RUN pip install poetry && useradd -d /home/bank -U -m -u 1111 bank && mkdir /app

WORKDIR /home/bank/git

COPY --chown=bank:bank . .

USER bank

RUN poetry install

COPY nginx.conf /etc/nginx/conf.d/default.conf



CMD ["poetry", "run", "python", "main.py"]
