import abc
import json

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
    def __init__(self, client_id, percent, sum, term):
        super().__init__(client_id, percent, sum, term)
        self._periods = self.term * 12
        self._closed = False
    @property
    def periods(self):
        return self._periods
    
    @property
    def closed(self):
        return self._closed

    @property
    def monthly_fee(self):
        return self.end_sum / (self.term * 12)
    
    def to_dict(self):
        return {
            'client_id': self.id,
            'percent': self.percent,
            'sum': self.sum,
            'term': self.term
        }

    def process(self):
        if not self.closed:
            client = AccountClient(self.client_id)
            client.transaction(self.sum)
            client.transaction(-self.monthly_fee)
            client.transaction(self.monthly_fee, 0)
        
        self._periods -= 1
        if self._periods == 0:
            self._closed = True
                
                                     
class Deposit(BankProduct):
        
    def __init__(self, client_id, percent, sum, term):
        super().__init__(client_id, percent, sum, term)
        self._closed = False
        self._periods = self.term * 12
        
    
# При инициализации Deposit создаём объект AccountClient и меняем в нём withdraw на False
        client = AccountClient(self.client_id)
        client.withdraw = False
# Добавляем логику для инициализации кредитов (первичное пополнение счёта клиента)
        if self.sum > 0:
            client.transaction(self.sum)
        
    @property
    def periods(self):
        return self._periods
    
    @property
    def closed(self):
        return self._closed
    
    @property
    def monthly_fee(self):
        return (self.end_sum - self.sum) / (self.term * 12)
    
    def to_dict(self):
        return {
            'client_id': self.id,
            'percent': self.percent,
            'sum': self.sum,
            'term': self.term
        }
    
    def process(self):
        if not self.closed:
            client = AccountClient(self.client_id)
            client.transaction(self.monthly_fee)
            client.transaction(-self.monthly_fee, 0)
            
            self._periods -= 1
            if self._periods == 0:
                self._closed = True

from flask import Flask, abort, make_response, request, jsonify
from account_clients import AccountClient
import yaml

app = Flask(__name__)
@app.route('/api/v1/credits/<string:client_id>', methods=['GET'])
def credits(client_id):
    # Создаем объект AccountClient для доступа к данным клиентов
    client = AccountClient()
    
    # Получаем данные о кредите для данного клиента
    credit_info = client.get_client_credits(client_id)
    
    # Если кредит не найден, возвращаем ошибку 404
    if not credit_info:
        error_message = {"status": "error", "message": f"Client {client_id} does not have active credits"}
        return make_response(jsonify(error_message), 404)
    # Если данные о кредите найдены, возвращаем их в формате JSON
    return jsonify(credit_info)

@app.route('/api/v1/deposits/<client_id>', methods=['GET'])
def get_client_deposit(client_id):
    client = AccountClient()
    
    client_deposit = client.get_client_deposits(client_id)
    if client_deposit is not None:
        client_deposit['withdraw'] = False
    
    if not client_deposit:
        return make_response(jsonify({
            "status": "error",
            "message": f"Client {client_id} does not have active deposits"
        }), 404)
    

@app.route('/api/v1/deposits', methods=['GET'])
def get_all_deposits():
    client = AccountClient()
    all_deposits = client.get_all_deposits()
   
    if not all_deposits:
        return make_response(jsonify({
            "status": "error",
            "message": "No active deposits found"
        }), 404)
    
    return jsonify(all_deposits)

@app.route('/api/v1/credits', methods=['GET'])
def get_all_credits():
    client = AccountClient()
    all_credits = client.get_all_credits()
    
    if not all_credits:
        return make_response(jsonify({
            "status": "error",
            "message": "No active credits found"
        }), 404)
    
    return jsonify(all_credits)

@app.route('/api/v1/credits', methods=['PUT'])
def create_new_credit():
    client_id = request.json.get('client_id')
    percent = request.json.get('percent')
    sum = request.json.get('sum')
    term = request.json.get('term')
    
    if not all((client_id, percent, sum, term)):
        return make_response(jsonify({
            "status": "error",
            "message": "Отсутствуют обязательные параметры"
        }), 400)
    
    client = AccountClient()
    client.add_new_credit(client_id, percent, sum, term)
    
    return make_response(jsonify({
        "status": "success",
        "message": "Кредит успешно создан"
    }), 201)
    
    
    
with open('credits_deposits.json', 'r') as file:
    data1 = json.load(file)
    
# Создаем объекты кредитов и депозитов и добавляем их в соответствующие списки
credits = [Credit(entity['client_id'], entity['percent'], entity['sum'], entity['term']) for entity in data1.get('credit', [])]
deposits = [Deposit(entity['client_id'], entity['percent'], entity['sum'], entity['term']) for entity in data1.get('deposit', [])]

import time
import json
# Вызываем метод process каждый месяц = 10 сек
while True:

    # Обрабатываем кредиты и депозиты
    for credit in credits:
        credit.process()
    for deposit in deposits:
        deposit.process()

    # Удаляем закрытые кредиты и депозиты
    credits = [credit for credit in credits if not credit.closed]
    deposits = [deposit for deposit in deposits if not deposit.closed]

    #Записываем новые данные 
    new_data = {"credit": [credit.to_dict() for credit in credits], 
            "deposit": [deposit.to_dict() for deposit in deposits]}
    
    time.sleep(1)
    

        