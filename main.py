import abc
import json

class BankProduct(abc.ABC):
    def __init__(self, entity_id, percent, sum, term):
        self._id = entity_id
        self._percent = percent
        self._sum = sum
        self._term = term

    @property
    def id(self):
        return self._id

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
    
import csv

class Credit(BankProduct):
    def __init__(self, entity_id, percent, sum, term):
        super().__init__(entity_id, percent, sum, term)
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
            'entity_id': self.id,
            'percent': self.percent,
            'sum': self.sum,
            'term': self.term
        }

    def process(self):
        if not self.closed:
            with open('transactions.csv', mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([self.id, self.monthly_fee, 'substract'])
                writer.writerow([0, self.monthly_fee, 'add'])
            self._periods -= 1
            print(self.periods)
            if self._periods == 0:
                self._closed = True
                
with open('credits_deposits.json', 'r') as file:
    data1 = json.load(file)
                                     
class Deposit(BankProduct):
        
    def __init__(self, entity_id, percent, sum, term):
        super().__init__(entity_id, percent, sum, term)
        self._closed = False
        self._periods = self.term * 12
        
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
            'entity_id': self.id,
            'percent': self.percent,
            'sum': self.sum,
            'term': self.term
        }
    
    def process(self):
        if not self.closed:
            with open('transactions.csv', mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([self.id, self.monthly_fee, 'add'])
                writer.writerow([0, self.monthly_fee, 'substract'])
            self._periods -= 1
            if self._periods == 0:
                self._closed = True
                
with open('credits_deposits.json', 'r') as file:
    data1 = json.load(file)
    
# Создаем объекты кредитов и депозитов и добавляем их в соответствующие списки
credits = [Credit(entity['entity_id'], entity['percent'], entity['sum'], entity['term']) for entity in data1.get('credit', [])]
deposits = [Deposit(entity['entity_id'], entity['percent'], entity['sum'], entity['term']) for entity in data1.get('deposit', [])]

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
    
    with open('credits_deposits.json', 'w') as file:
        json.dump(new_data, file)

    time.sleep(10)
        