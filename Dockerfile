FROM python:3.11-buster

RUN pip install poetry && useradd -d /home/bank -U -m -u 1111 bank && mkdir /app

WORKDIR /home/bank/git

RUN echo "bank ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

COPY --chown=bank:bank . .

USER bank

RUN apt update && apt install -y nginx

RUN poetry install

COPY nginx.conf /etc/nginx/conf.d/default.conf



CMD ["poetry", "run", "python", "main.py"]
