import abc
import json
from flask import Flask, make_response, request, jsonify
import yaml
from account_clients import AccountClient

# Создаем Flask приложение
app = Flask(__name__)


class BankProduct(abc.ABC):
    def __init__(self, client_id, percent, sum, term):
        self.client_id = client_id
        self._percent = percent
        self._sum = sum
        self._term = term

    @property
    def id(self):
        return self.client_id

    @property
    def percent(self):
        return self._percent

    @property
    def sum(self):
        return self._sum

    @property
    def term(self):
        return self._term

    @property
    def end_sum(self):
        return self._sum * (1 + self._percent / 100) ** self._term

    @abc.abstractmethod
    def process(self):
        pass


class Credit(BankProduct):
    def __init__(self, client_id, percent, sum, term, periods=-1):
        super().__init__(client_id, percent, sum, term)
        self._closed = False
        if periods == -1:
            self._periods = self.term * 12
        else:
            self._periods = periods

    @property
    def periods(self):
        return self._periods

    @periods.setter
    def periods(self, value):
        self._periods = value

    @property
    def closed(self):
        return self._closed

    @property
    def monthly_fee(self):
        return self.end_sum / (self.term * 12)

    def to_dict(self):
        return {
            "client_id": self.id,
            "percent": self.percent,
            "sum": self.sum,
            "term": self.term,
            "periods": self.periods,
        }

    def process(self):
        if not self.closed:
            client = AccountClient(self.client_id)
            bank = AccountClient(0)
            client.transaction(substract=self.monthly_fee)
            bank.transaction(add=self.monthly_fee)

        self._periods -= 1
        if self._periods == 0:
            self._closed = True


class Deposit(BankProduct):
    def __init__(self, client_id, percent, sum, term, periods=-1):
        super().__init__(client_id, percent, sum, term)
        self._closed = False
        if periods == -1:
            self._periods = self.term * 12
        else:
            self._periods = periods

        # При инициализации Deposit создаём объект AccountClient и меняем в нём withdraw на False
        client = AccountClient(self.client_id)
        client.withdraw = False
        # Добавляем логику для инициализации кредитов (первичное пополнение счёта клиента)
        if self.sum > 0:
            client.transaction(self.sum)

    @property
    def periods(self):
        return self._periods

    @periods.setter
    def periods(self, value):
        self._periods = value

    @property
    def closed(self):
        return self._closed

    @property
    def monthly_fee(self):
        return (self.end_sum - self.sum) / (self.term * 12)

    def to_dict(self):
        return {
            "client_id": self.id,
            "percent": self.percent,
            "sum": self.sum,
            "term": self.term,
            "periods": self.periods,
        }

    def process(self):
        if not self.closed:
            client = AccountClient(self.client_id)
            bank = AccountClient(0)
            client.transaction(add=self.monthly_fee)
            bank.transaction(substract=self.monthly_fee)

            self._periods -= 1
            if self._periods == 0:
                self._closed = True


#####################FLASK##########################################
# Получаем кредит клиента по его Id
@app.route("/api/v1/bank/health_check", methods=["GET"])
def health_check():
    return "", 200

@app.route("/api/v1/credits/<int:client_id>", methods=["GET"])
def get_credits(client_id):
    with open("credits_deposits.yaml", "r") as f:
        data = yaml.load(f, Loader=yaml.FullLoader)

    credits = [credit for credit in data.get("credit", [])]
    credits_of_client = [
        credit for credit in credits if credit["client_id"] == client_id
    ]
    if len(credits_of_client) == 0:
        error_massage = f"client {client_id} does not have active credits"
        return jsonify({"status": "error", "message": error_massage}), 404
    else:
        return jsonify(credits_of_client[0])


# Получаем депозит клиента по его id
@app.route("/api/v1/deposits/<int:client_id>", methods=["GET"])
def get_deposit(client_id):
    with open("credits_deposits.yaml", "r") as f:
        data = yaml.load(f, Loader=yaml.FullLoader)

    deposits = [deposit for deposit in data.get("deposit", [])]
    deposits_of_client = [
        deposit for deposit in deposits if deposit["client_id"] == client_id
    ]
    if len(deposits_of_client) == 0:
        error_message = f"Client {client_id} does not have active deposits"
        return jsonify({"status": "error", "message": error_message}), 404
    else:
        return jsonify(deposits_of_client[0])


# Получаем все депозиты
@app.route("/api/v1/deposits/all", methods=["GET"])
def get_all_deposits():
    with open("credits_deposits.yaml", "r") as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
    deposits = [deposit for deposit in data.get("deposit", [])]
    return jsonify(deposits)


# Получаем все кредиты
@app.route("/api/v1/credits/all", methods=["GET"])
def get_all_credits():
    with open("credits_deposits.yaml", "r") as f:
        data = yaml.load(f, Loader=yaml.FullLoader)

    credits = [credit for credit in data.get("credit", [])]
    return jsonify(credits)


# Создаем новый кредит с проверкой на существование до этого и пишем в файл
@app.route("/api/v1/credits", methods=["PUT"])
def create_credit():
    # Получаем данные из запроса в формате JSON
    
    if request.json:
        data = request.json
        client_id = data["client_id"]
        percent = data["percent"]
        sum = data["sum"]
        term = data["term"]
        periods = data["periods"]
    else:
        client_id = request.args.get('client_id')
        percent = request.args.get('percent')
        sum = request.args.get('sum')
        term = request.args.get('term')
        periods = request.args.get('periods')

    with open("credits_deposits.yaml", "r") as f:
        file_data = yaml.safe_load(f)
    credits1 = file_data["credit"]

    # Проверяем, существует ли уже кредит для данного клиента
    for credit in credits1:
        if credit["client_id"] == client_id:
            return make_response(
                jsonify(
                    {
                        "status": "error",
                        "message": f"Credit for client {client_id} already exists",
                    }
                ),
                400,
            )

    # Добавляем новый кредит в список credits
    new_credit = {
        "client_id": client_id,
        "percent": percent,
        "sum": sum,
        "term": term,
        "periods": periods,
    }
    credits1.append(new_credit)
    file_data["credit"] = credits1
    with open("credits_deposits.yaml", "w") as f:
        yaml.dump(file_data, f)

    return (
        jsonify({"status": "ok", "message": f"Credit added for client {client_id}"}),
        201,
    )


# Создаем новый депозит с проверкой существует ли он уже и записываем в файл
@app.route("/api/v1/deposits", methods=["PUT"])
def create_deposit():
    # Получаем данные из запроса в формате JSON
    data = request.json
    client_id = data["client_id"]
    percent = data["percent"]
    sum = data["sum"]
    term = data["term"]
    periods = data["periods"]

    with open("credits_deposits.yaml", "r") as f:
        file_data = yaml.safe_load(f)
    deposits1 = file_data["deposit"]

    for deposit in deposits1:
        if deposit["client_id"] == client_id:
            return make_response(
                jsonify(
                    {
                        "status": "error",
                        "message": f"Deposit for client {client_id} already exists",
                    }
                ),
                400,
            )

    new_deposit = {
        "client_id": client_id,
        "percent": percent,
        "sum": sum,
        "term": term,
        "periods": periods,
    }
    deposits1.append(new_deposit)
    file_data["deposit"] = deposits1
    with open("credits_deposits.yaml", "w") as f:
        yaml.dump(file_data, f)

    return (
        jsonify(
            {"status": "success", "message": f"Deposit for client {client_id} created"}
        ),
        201,
    )


#####################FLASK##########################################

import threading


def process_credits_and_deposits():

    import time

    # Вызываем метод process каждый месяц = 10 сек
    while True:

        with open("credits_deposits.yaml", "r") as f:
            data1 = yaml.load(f, Loader=yaml.FullLoader)

        # Создаем объекты кредитов и депозитов и добавляем их в соответствующие списки
        credits = [
            Credit(
                entity["client_id"],
                entity["percent"],
                entity["sum"],
                entity["term"],
                entity["periods"],
            )
            for entity in data1.get("credit", [])
        ]
        deposits = [
            Deposit(
                entity["client_id"],
                entity["percent"],
                entity["sum"],
                entity["term"],
                entity["periods"],
            )
            for entity in data1.get("deposit", [])
        ]

        # Обрабатываем кредиты и депозиты
        for credit in credits:
            credit.process()
        for deposit in deposits:
            deposit.process()

        # Удаляем закрытые кредиты и депозиты
        credits = [credit for credit in credits if not credit.closed]
        deposits = [deposit for deposit in deposits if not deposit.closed]

        # Записываем новые данные
        new_data = {
            "credit": [credit.to_dict() for credit in credits],
            "deposit": [deposit.to_dict() for deposit in deposits],
        }

        with open("credits_deposits.yaml", "w") as f:
            yaml.dump(new_data, f)

        time.sleep(10)


credit_deposit_thread = threading.Thread(target=process_credits_and_deposits)
credit_deposit_thread.start()

if __name__ == "__main__":
    app.run(host='0.0.0.0')
