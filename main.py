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
        self._closed = False
        self._periods = self.sum * 12
        
    @property
    def periods(self):
        return self._periods

    @property
    def closed(self):
        return self._closed

    @property
    def monthly_fee(self):
        return self.end_sum / (self.sum * 12)

    def process(self):
        if not self.closed:
            with open('transactions.csv', mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([self.id, self.monthly_fee, 'subtract'])
                writer.writerow([0, self.monthly_fee, 'add'])
            self._periods -= 1
            if self._periods == 0:
                self._closed = True

class Deposit(BankProduct):
        
    def __init__(self, entity_id, percent, sum, term):
        super().__init__(entity_id, percent, sum, term)
        self._closed = False
        self._periods = self.sum * 12
        
    @property
    def periods(self):
        return self._periods
    
    @property
    def closed(self):
        return self._closed
    
    @property
    def monthly_fee(self):
        return self.end_sum / (self.sum * 12)
    
    def process(self):
        if not self.closed:
            with open('transactions.csv', mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([self.id, self.monthly_fee, 'subtract'])
                writer.writerow([0, self.monthly_fee, 'add'])
            self._periods -= 1
            if self._periods == 0:
                self._closed = True

import time
import json
with open('credits_deposits.json', 'r') as file:
    data = json.load(file) 
print(data)
# Создаем объеты кредита и депозита
credits = []
deposits = []
  
# Извлекаем список кредитов и депозитов из словаря data
credit_data = data.get('credit', [])
deposit_data = data.get('deposit', [])

# Создаем объекты кредитов и добавляем их в список credits
for entity in credit_data:
    credit = Credit(entity['entity_id'], entity['percent'], entity['sum'], entity['term'])
    credits.append(credit)

# Создаем объекты депозитов и добавляем их в список deposits
for entity in deposit_data:
    deposit = Deposit(entity['entity_id'], entity['percent'], entity['sum'], entity['term'])
    deposits.append(deposit)

# Вызываем метод process каждый месяц = 10 сек
while True:
    time.sleep(10)  
    for credit in credits:
        credit.process()
        if credit.closed:
            credits.remove(credit)
    for deposit in deposits:
        deposit.process()
        if deposit.closed:
            deposits.remove(deposit)

    # Записываем новые данные 
    data = [{'id': credit.id, 'percent': credit.percent, 'sum': credit.sum, 'term': credit.term, 'type': 'credit'} for credit in credits] + [{'id': deposit.id, 'percent': deposit.percent, 'sum': deposit.sum, 'term': deposit.term, 'type': 'deposit'} for deposit in deposits]
    with open('credits_deposits.json', 'w') as file:
        json.dump(data, file)

# with open('credits_deposits.json', 'r') as file:
#     data = json.load(file)

# credits = []
# deposits = []

# # Создаем объекты кредитов и добавляем их в список credits
# for entity in data['credit']:
#     credit = Credit(entity['entity_id'], entity['percent'], entity['sum'], entity['term'])
#     credits.append(credit)

# # Создаем объекты депозитов и добавляем их в список deposits
# for entity in data['deposit']:
#     deposit = Deposit(entity['entity_id'], entity['percent'], entity['sum'], entity['term'])
#     deposits.append(deposit)  
    
# while True:
#     # Обрабатываем кредиты и депозиты каждый месяц
#     while credits or deposits:
#         # Обрабатываем кредиты
#         for credit in credits:
#             credit.process()
#             if credit.closed:
#                 credits.remove(credit)
#         # Обрабатываем депозиты
#         for deposit in deposits:
#             deposit.process()
#             if deposit.closed:
#                 deposits.remove(deposit)

#     # Сохраняем данные в файл
#     data = {'credit': [], 'deposit': []}
#     for credit in credits:
#         credit_dict = {'entity_id': credit.id, 'percent': credit.percent, 'sum': credit.sum, 'term': credit.term}
#         data['credit'].append(credit_dict)
#     for deposit in deposits:
#         deposit_dict = {'entity_id': deposit.id, 'percent': deposit.percent, 'sum': deposit.sum, 'term': deposit.term}
#         data['deposit'].append(deposit_dict)
#     with open('credits_deposits.json', 'w') as file:
#         json.dump(data, file)

#     time.sleep(10)



    
        