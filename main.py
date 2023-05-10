import abc
import json
from account_clients import AccountClient

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

from flask import Flask, make_response, request, jsonify
import yaml

with open('credits_deposits.yaml', 'r') as f:
    data = yaml.load(f, Loader=yaml.FullLoader)

# Создаем переменные для кредитов и депозитов
credits = data['credit']
deposits = data['deposit']

# Создаем Flask приложение
app = Flask(__name__)

# GET /api/v1/credits/<client_id>
@app.route('/api/v1/credits/<client_id>', methods=['GET'])
def get_credits(client_id):
    if client_id in credits:
        return jsonify(credits[client_id])
    else:
        return jsonify({'status': 'error', 'message': f'Client {client_id} does not have active credits'}), 404

@app.route('/api/v1/deposits/<client_id>', methods=['GET'])
def get_deposit(client_id):
    if client_id not in deposits:
        return jsonify({"status": "error", "message": f"Client {client_id} does not have active deposits"}), 404
    else:
        return jsonify(deposits[client_id])

@app.route('/api/v1/deposits', methods=['GET'])
def get_all_deposits():
    return jsonify(deposits)

@app.route('/api/v1/credits', methods=['GET'])
def get_all_credits():
    return jsonify(credits)

# Создаем новый кредит с проверкой на существование до этого и пишем в файл
@app.route('/api/v1/credits', methods=['PUT'])
def create_credit():
    client_id = request.json.get('client_id')
    percent = request.json.get('percent')
    sum = request.json.get('sum')
    term = request.json.get('term')
    
    if client_id in credits:
        return make_response(jsonify({"status": "error", "message": f"Credit for client {client_id} already exists"}), 400)
    
    new_credit = {
        "client_id": client_id,
        "percent": percent,
        "sum": sum,
        "term": term
    }
    credits[client_id] = new_credit
    
    with open('credits_deposits.yaml', 'w') as f:
        yaml.dump({'credit': credits, 'deposit': deposits}, f)
    
    return make_response(jsonify({"status": "success", "message": f"Credit for client {client_id} created"}), 201)

#Создаем новый депозит с проверкой существует ли он уже и записываем в файл
@app.route('/api/v1/deposits', methods=['PUT'])
def create_deposit():
    client_id = request.json.get('client_id')
    percent = request.json.get('percent')
    sum = request.json.get('sum')
    term = request.json.get('term')
    
    if client_id in deposits:
        return make_response(jsonify({"status": "error", "message": f"Deposit for client {client_id} already exists"}), 400)
    
    new_deposit = {
        "client_id": client_id,
        "percent": percent,
        "sum": sum,
        "term": term
    }
    deposits[client_id] = new_deposit
    
    with open('credits_deposits.yaml', 'w') as f:
        yaml.dump({'credit': credits, 'deposit': deposits}, f)
    
    return make_response(jsonify({"status": "success", "message": f"Deposit for client {client_id} created"}), 201)


import threading

def process_credits_and_deposits():
    
    with open('credits_deposits.yaml', 'r') as file:
        data1 = json.load(file)
        
    # Создаем объекты кредитов и депозитов и добавляем их в соответствующие списки
    credits = [Credit(entity['client_id'], entity['percent'], entity['sum'], entity['term']) for entity in data1.get('credit', [])]
    deposits = [Deposit(entity['client_id'], entity['percent'], entity['sum'], entity['term']) for entity in data1.get('deposit', [])]

    import time

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
    
credit_deposit_thread = threading.Tread(target=process_credits_and_deposits)
credit_deposit_thread.start()
if __name__ == '__main__':
    app.run()  