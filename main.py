import abc
import json
import yaml
from flask import Flask, make_response, request, jsonify
from datetime import datetime, date
from account_clients import AccountClient
from sqlalchemy import Column, Integer, Float
from sqlalchemy.exc import IntegrityError
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from flask_sqlalchemy import SQLAlchemy

with open("/app/secrets_decrypted.yml", "r") as f:
    password1 = f.read().replace(" ", "").strip()

app = Flask(__name__)
    
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = f"postgresql://postgres:{password1}@postgres:5432/omegabank"
db = SQLAlchemy(app)

# Создаем Flask приложение    
class BankProduct(db.Model):
    __abstract__ = True
    
    client_id = db.mapped_column(db.Integer, primary_key=True)
    percent = db.mapped_column(db.NUMERIC)
    sum = db.mapped_column(db.NUMERIC)
    term = db.mapped_column(db.Integer)
    periods = db.mapped_column(db.Integer)
    closed = db.Column(db.Boolean, default=False)
    
    def __init__(self, client_id, percent, sum, term):
        self.client_id = client_id
        self.percent = percent
        self.sum = sum
        self.term = term

    @property
    def id(self):
        return self.client_id
    
    @property
    def percent(self):
        return self._percent
    
    @percent.setter
    def percent(self, value):
        self._percent = value
    
    @property
    def sum(self):
        return self._sum
    
    @sum.setter
    def sum(self, value):
        self._sum = value
    
    @property
    def term(self):
        return self._term
    
    @term.setter
    def term(self, value):
        self._term = value
    
    @property
    def end_sum(self):
        return self._sum * (1 + self._percent / 100) ** self._term

    @abc.abstractmethod
    def process(self):
        pass

class Credit(BankProduct):
    __tablename__ = "credits"
    
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
            "periods": self.periods
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
    __tablename__ = "deposits"
    
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
        if int(self.sum) > 0:
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
    credits_of_client = db.session.query(Credit).filter(Credit.client_id == client_id, Credit.closed == False).first()

    if not credits_of_client:
        error_message = f"У клиента {client_id} нет активных кредитов"
        return jsonify({"status": "error", "message": error_message}), 404
    else:
        return jsonify({
            "client_id": credits_of_client.client_id,
            "percent": credits_of_client.percent,
            "sum": credits_of_client.sum,
            "term": credits_of_client.term,
            "periods": credits_of_client.periods,
        })



# Получаем депозит клиента по его id
@app.route("/api/v1/deposits/<int:client_id>", methods=["GET"])
def get_deposit(client_id):
    deposit_of_client = db.session.query(Deposit).filter(Deposit.client_id == client_id, Deposit.closed == False).first()

    if not deposit_of_client:
        error_message = f"Клиент {client_id} не имеет активных депозитов"
        return jsonify({"status": "error", "message": error_message}), 404
    else:
        return jsonify({
            "client_id": deposit_of_client.client_id,
            "percent": deposit_of_client.percent,
            "sum": deposit_of_client.sum,
            "term": deposit_of_client.term,
            "periods": deposit_of_client.periods,
        })


# Получаем все депозиты
@app.route("/api/v1/deposits/all", methods=["GET"])
def get_all_deposits():
    deposits_all = db.session.query(Deposit).filter(Deposit.closed == False).all()

    deposits_list = []
    for deposit in deposits_all:
        deposits_list.append({
            "client_id": deposit.client_id,
            "percent": deposit.percent,
            "sum": deposit.sum,
            "term": deposit.term,
            "periods": deposit.periods,
        })

    return jsonify(deposits_list)


# Получаем все кредиты
@app.route("/api/v1/credits/all", methods=["GET"])
def get_all_credits():
    credits_all = db.session.query(Credit).filter(Credit.closed == False).all()

    credits_list = []
    for credit in credits_all:
        credits_list.append({
            "client_id": credit.client_id,
            "percent": credit.percent,
            "sum": credit.sum,
            "term": credit.term,
            "periods": credit.periods,
        })

    return jsonify(credits_list)


# Создаем новый кредит с проверкой на существование до этого и пишем в файл
@app.route("/api/v1/credits", methods=["PUT"])
def create_credit():
    try:
        data = request.get_json()

        credit = Credit(**data)

        existing_credit = db.session.query(Credit).filter(client_id=credit.client_id, closed=False).first()
        if existing_credit:
            return make_response(
                jsonify(
                    {
                        "status": "error",
                        "message": f"Client {credit.client_id} already has an open credit",
                    }
                ),
                400,
            )
        
        db.session.add(credit)
        db.session.commit()
        return (
            jsonify({"status": "ok", "message": f"Credit added for client {credit.client_id}"}),
            201,
        )
    except KeyError as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 400


# Создаем новый депозит с проверкой существует ли он уже и записываем в базу
@app.route("/api/v1/deposits", methods=["PUT"])
def create_deposit():
    try:
        data = request.get_json()

        deposit = Deposit(**data)

        deposits = db.session.query(Deposit).filter(client_id=deposit.client_id, closed=False).first()
        if deposits:
            return make_response(
                jsonify(
                    {
                        "status": "error",
                        "message": f"Client {deposit.client_id} already has an open deposit",
                    }
                ),
                400,
            )
        db.session.add(deposit)
        db.session.commit()
        return (
            jsonify({"status": "ok", "message": f"Deposit added for client {deposit.client_id}"}),
            201,
        )
    except KeyError as e:
        return jsonify({"status": "error", "message": f"Missing attribute {str(e)}"}), 400
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 400

#####################FLASK##########################################

import threading

def process_credits_and_deposits():

    import time

    # Вызываем метод process каждый месяц = 10 сек
    while True:
        with app.app_context():                       
            # Создаем объекты кредитов и депозитов и добавляем их в соответствующие списки
            credits_inf = db.session.query(Credit).filter(Credit.closed == False).all()
            deposits_inf = db.session.query(Deposit).filter(Deposit.closed == False).all()

            # Обрабатываем кредиты и депозиты
            for credit in credits_inf:
                credit.process()
            for deposit in deposits_inf:
                deposit.process()


            db.session.add_all(credits_inf)
            db.session.add_all(deposits_inf)

            try:
                db.session.commit()
            except IntegrityError as err:
                db.session.rollback()

        time.sleep(10)
        
        
def read_data():
    credits_info = db.session.query(Credit).all()
    if not credits_info:
        with open("credits_deposits.yaml", "r") as f:
            data1 = yaml.load(f, Loader=yaml.FullLoader)
        for operation_type, items in data1.items():
            for item in items:
                if operation_type == "credit":
                    credit = Credit(
                        item["client_id"],
                        item["percent"],
                        item["sum"],
                        item["term"],
                        item["periods"]
                    )
                    db.session.add(credit)
    try:
        db.session.commit()
    except IntegrityError as err:
        db.session.rollback()
                        
    deposits_info = db.session.query(Deposit).all()
    if not deposits_info:  
        with open("credits_deposits.yaml", "r") as f:
            data2 = yaml.load(f, Loader=yaml.FullLoader)              
        for operation_type, items in data2.items():
            for item in items:
                if operation_type == "deposit":
                    deposit = Deposit(
                        item["client_id"],
                        item["percent"],
                        item["sum"],
                        item["term"],
                        item["periods"]
                    )
                    db.session.add(deposit)
    try:
        db.session.commit()
    except IntegrityError as err:
        db.session.rollback()
        
with app.app_context():
    db.create_all()
    read_data()

credit_deposit_thread = threading.Thread(target=process_credits_and_deposits)
credit_deposit_thread.start()

if __name__ == "__main__":
    app.run(host='0.0.0.0')
