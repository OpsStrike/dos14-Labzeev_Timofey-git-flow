import abc
import json
from flask import Flask, make_response, request, jsonify
import yaml
from account_clients import AccountClient
from sqlalchemy import Column, Integer, Float
from sqlalchemy.exc import IntegrityError
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker


with open("/app/secrets_decrypted.yml", "r") as f:
    password1 = f.read().replace(" ", "").strip()
    
engine = create_engine(
    f"postgresql://postgres:{password1}@postgres:5432/omegabank",
)
Base = declarative_base()

Session = sessionmaker(bind=engine)
session = Session()

# Создаем Flask приложение
app = Flask(__name__)

class CommonCredit(Base):
    __tablename__ = "Credits"

    client_id = Column(Integer, primary_key=True)
    percent = Column(Float)
    sum = Column(Float)
    term = Column(Integer)
    periods = Column(Integer)
    
class CommonDeposit(Base):
    __tablename__ = "Deposits"

    client_id = Column(Integer, primary_key=True)
    percent = Column(Float)
    sum = Column(Float)
    term = Column(Integer)
    periods = Column(Integer)

class BankProduct(abc.ABC):
    def __init__(self, client_id, percent, sum, term):
        self.client_id = client_id
        self.percent = percent
        self.sum = sum
        self.term = term

    def id(self):
        return self.client_id
 
    def percent(self):
        return self._percent
    
    def sum(self):
        return self._sum
    
    def term(self):
        return self._term
    
    def end_sum(self):
        return self._sum * (1 + self._percent / 100) ** self._term

    @abc.abstractmethod
    def process(self):
        pass


class Credit(BankProduct):
    def __init__(self, client_id, percent, sum, term, periods=-1):
        super().__init__(client_id, percent, sum, term)
        self.closed = False
        if periods == -1:
            self.periods = self.term * 12
        else:
            self.periods = periods

    def periods(self):
        return self._periods

    
    def periods(self, value):
        self._periods = value

    def closed(self):
        return self._closed

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

        self.periods -= 1
        if self.periods == 0:
            self.closed = True


class Deposit(BankProduct):
    def __init__(self, client_id, percent, sum, term, periods=-1):
        super().__init__(client_id, percent, sum, term)
        self.closed = False
        if periods == -1:
            self.periods = self.term * 12
        else:
            self.periods = periods

        # При инициализации Deposit создаём объект AccountClient и меняем в нём withdraw на False
        client = AccountClient(self.client_id)
        client.withdraw = False
        # Добавляем логику для инициализации кредитов (первичное пополнение счёта клиента)
        if int(self.sum) > 0:
            client.transaction(self.sum)

    
    def periods(self):
        return self._periods

    
    def periods(self, value):
        self.periods = value
  
    def closed(self):
        return self._closed

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

            self.periods -= 1
            if self.periods == 0:
                self.closed = True


#####################FLASK##########################################
# Получаем кредит клиента по его Id
@app.route("/api/v1/bank/health_check", methods=["GET"])
def health_check():
    return "", 200

@app.route("/api/v1/credits/<int:client_id>", methods=["GET"])
def get_credits(client_id):
    credits_of_client = session.query(CommonCredit).filter(CommonCredit.client_id == client_id).first()

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
    deposit_of_client = session.query(CommonDeposit).filter(CommonDeposit.client_id == client_id).first()

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
    deposits_all = session.query(CommonDeposit).all()

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
    credits_all = session.query(CommonCredit).all()

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
    # Получаем данные из запроса в формате JSON
    client_id = request.args.get('client_id')
    percent = request.args.get('percent')
    sum = request.args.get('sum')
    term = request.args.get('term')
    periods = request.args.get('periods')

    # Проверяем, существует ли уже кредит для данного клиента в базе
    existing_credit = session.query(CommonCredit).filter(CommonCredit.client_id == client_id).first()
    if existing_credit:
        return make_response(
            jsonify(
                {
                    "status": "error",
                    "message": f"Credit for client {client_id} already exists",
                }
            ),
            400,
        )

    # Создаем новый кредит объекта CommonCredit и добавляем его в базу
    new_credit = CommonCredit(
        client_id=client_id,
        percent=percent,
        sum=sum,
        term=term,
        periods=periods
    )
    session.add(new_credit)
    
    try:
        session.commit()
        return jsonify(
            {"status": "success", "message": f"Credit added for client {client_id}"},
        ), 201
        
    except IntegrityError as err:
        session.rollback()

# Создаем новый депозит с проверкой существует ли он уже и записываем в базу
@app.route("/api/v1/deposits", methods=["PUT"])
def create_deposit():
    # Получаем данные из запроса в формате JSON
    client_id = request.args.get('client_id')
    percent = request.args.get('percent')
    sum = request.args.get('sum')
    term = request.args.get('term')
    periods = request.args.get('periods')

    # Проверяем, существует ли уже депозит для данного клиента в базе
    existing_deposit = session.query(CommonDeposit).filter(CommonDeposit.client_id == client_id).first()
    if existing_deposit:
        return make_response(
            jsonify(
                {
                    "status": "error",
                    "message": f"Deposit for client {client_id} already exists",
                }
            ),
            400,
        )

    # Создаем новый объект CommonDeposit и добавляем его в базу
    new_deposit = CommonDeposit(
        client_id=client_id,
        percent=percent,
        sum=sum,
        term=term,
        periods=periods
    )
    session.add(new_deposit)
    
    try:
        session.commit()
        return jsonify(
            {"status": "success", "message": f"Deposit for client {client_id} created"},
        ), 201
        
    except IntegrityError as err:
        session.rollback()

#####################FLASK##########################################

import threading

def process_credits_and_deposits():

    import time

    # Вызываем метод process каждый месяц = 10 сек
    while True:
        
        
        
        clients_info = session.query(CommonCredit, CommonDeposit).all()
        if not clients_info:
            with open("credits_deposits.yaml", "r") as f:
                data1 = yaml.load(f, Loader=yaml.FullLoader)
        for CD in data1:
            if CD["type"] == "credit":
                credit = Credit(
                CD["client_id"],
                CD["percent"],
                CD["sum"],
                CD["term"],
                CD["periods"]
            )
                session.add(credit)
                
            elif CD["type"] == "deposit":
                deposit = Deposit(
                CD["client_id"],
                CD["percent"],
                CD["sum"],
                CD["term"],
                CD["periods"]
            )
                session.add(deposit)
                        
        try:
            session.commit()
        except IntegrityError as err:
            session.rollback()
        
        
        # Создаем объекты кредитов и депозитов и добавляем их в соответствующие списки
        credits_inf = session.query(CommonCredit).all()
        deposits_inf = session.query(CommonDeposit).all()

        # Обрабатываем кредиты и депозиты
        for credit in credits_inf:
            credit.process()
        for deposit in deposits_inf:
            deposit.process()

        # Удаляем закрытые кредиты и депозиты
        credits = [credit for credit in credits_inf if not credit.closed]
        deposits = [deposit for deposit in deposits_inf if not deposit.closed]

        # Записываем новые данные
        for credit in credits:
            session.add(credit)
        for deposit in deposits:
            session.add(deposit)

        try:
            session.commit()
        except IntegrityError as err:
            session.rollback()

        time.sleep(10)


credit_deposit_thread = threading.Thread(target=process_credits_and_deposits)
credit_deposit_thread.start()

if __name__ == "__main__":
    app.run(host='0.0.0.0')
