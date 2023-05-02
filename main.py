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
            if self._periods == 0:
                self._closed = True
                
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

import time
import json

# Вызываем метод process каждый месяц = 10 сек
while True:
    with open('credits_deposits.json', 'r') as file:
        data1 = json.load(file)
    print(data1)
    # Создаем объекты кредитов и депозитов и добавляем их в соответствующие списки
    credits = [Credit(entity['entity_id'], entity['percent'], entity['sum'], entity['term']) for entity in data1.get('credit', [])]
    deposits = [Deposit(entity['entity_id'], entity['percent'], entity['sum'], entity['term']) for entity in data1.get('deposit', [])]

    # Обрабатываем кредиты и депозиты
    for credit in credits:
        credit.process()
    for deposit in deposits:
        deposit.process()

    # Удаляем закрытые кредиты и депозиты
    credits = [credit for credit in credits if not credit.closed]
    deposits = [deposit for deposit in deposits if not deposit.closed]

    # Записываем новые данные 
    data = {"credit": [credit.to_dict() for credit in credits], 
            "deposit": [deposit.to_dict() for deposit in deposits]}
    print(data)
    with open('credits_deposits.json', 'w') as file:
        json.dump(data, file)

    time.sleep(10)




###########Рабочий
# # Вызываем метод process каждый месяц = 10 сек
# while True:
#     with open('credits_deposits.json', 'r') as file:
#         data1 = json.load(file)    
#         # print(data)
#     credits = []
#     deposits = []

#     # Извлекаем список кредитов и депозитов из словаря data
#     credit_data = data1.get('credit', [])
#     deposit_data = data1.get('deposit', [])

#     # Создаем объекты кредитов и добавляем их в список credits
#     for entity in credit_data:
#         credit = Credit(entity['entity_id'], entity['percent'], entity['sum'], entity['term'])
#         credits.append(credit)

#     # Создаем объекты депозитов и добавляем их в список deposits
#     for entity in deposit_data:
#         deposit = Deposit(entity['entity_id'], entity['percent'], entity['sum'], entity['term'])
#         deposits.append(deposit)
#         for credit in credits:
#             credit.process()
#             if credit.closed:
#                 credits.remove(credit)
#         for deposit in deposits:
#             deposit.process()
#             if deposit.closed:
#                 deposits.remove(deposit)
                
#         # Записываем новые данные 
#         data = {"credit": [{"entity_id": credit.id, "percent": credit.percent, "sum": credit.sum, "term": credit.term} for credit in credits], 
#                 "deposit": [{"entity_id": deposit.id, "percent": deposit.percent, "sum": deposit.sum, "term": deposit.term} for deposit in deposits]}
#         with open('credits_deposits.json', 'w') as file:
#             json.dump(data, file)
#         time.sleep(10)      
        





# while True:
#     # Загружаем текущие данные из файла
#     with open('credits_deposits.json', 'r') as file:
#         data = json.load(file)

#     # Создаем списки для хранения объектов кредитов и депозитов
#     credits = []
#     deposits = []

#     # Создаем объекты кредитов и добавляем их в список credits
#     for entity in data.get('credit', []):
#         credit = Credit(entity['entity_id'], entity['percent'], entity['sum'], entity['term'])
#         credits.append(credit)

#     # Создаем объекты депозитов и добавляем их в список deposits
#     for entity in data.get('deposit', []):
#         deposit = Deposit(entity['entity_id'], entity['percent'], entity['sum'], entity['term'])
#         deposits.append(deposit)

#     # Обрабатываем и удаляем закрытые депозиты
#     deposits_to_remove = []
#     for deposit in deposits:
#         deposit.process()
#         if deposit.closed:
#             deposits_to_remove.append(deposit)

#     for deposit in deposits_to_remove:
#         deposits.remove(deposit)

#     # Обрабатываем и удаляем закрытые кредиты
#     credits_to_remove = []
#     for credit in credits:
#         credit.process()
#         if credit.closed:
#             credits_to_remove.append(credit)

#     for credit in credits_to_remove:
#         credits.remove(credit)

#     # Создаем список словарей с открытыми кредитами
#     credit_dicts = [credit.to_dict() for credit in credits]

#     # Создаем список словарей с открытыми депозитами
#     deposit_dicts = [deposit.to_dict() for deposit in deposits]

#     # Обновляем данные в словаре и записываем их в файл
#     current_data = {"credit": credit_dicts, "deposit": deposit_dicts}

#     with open('credits_deposits.json', 'w') as file:
#         json.dump(data, file)

#     time.sleep(1)









        
        
        
        

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



    
        