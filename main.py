

#LESSON 17
import json
import csv
import yaml
import time

def load_data():
        # Открываем и считываем информацию из файлов
    with open('credit.json') as f:
        credit_data = json.load(f)

    with open('deposit.yaml') as f:
        deposit_data = yaml.load(f, Loader=yaml.FullLoader)

    with open('account.csv') as f:
        reader = csv.DictReader(f)
        account_data = list(csv.DictReader(f))

    # Сортируем списки по возрастанию id
    credit_data = sorted(credit_data, key=lambda x: x['id'])
    deposit_data = sorted(deposit_data, key=lambda x: x['id'])
    account_data = sorted(account_data, key=lambda x: int(x['id']))

    for credit in credit_data:
        #Расчёт сложного процента
        credit['sum_total'] = credit['sum']*(1+credit["percent"]/100) ** credit['term']
        #Сколько месяцев у нас длится наш кредит
        credit['months_counter'] = credit["term"]*12
        
    #Обогaщаем наш дикт данными по
    #итоговой сумме + сколько месяцев длится наш депозит
    for deposit in deposit_data:
        #Расчёт сложного процента
        deposit['sum_total'] = deposit['sum']*(1+deposit["percent"]/100) ** deposit['term']
        #Сколько месяцев у нас длится наш депозит
        deposit['months_counter'] = deposit["term"]*12 
        
    #Расчитаем сумму которую мы должны отнять cо
    #счёта банка   
    total_credit_sum = sum(float(credit['sum']) for credit in credit_data)
    account_data[0]['amount'] = float(account_data[0]['amount']) - total_credit_sum


    # Идём по списку кредитов
    # и добавляем сумму кредита на счёт клиентов
    for credit in credit_data:
        if credit['sum'] > 0:
            for account in account_data:
                if credit['id'] == int(account['id']):
                    account['amount'] = int(account['amount']) + int(credit['sum'])


    return credit_data, deposit_data, account_data  
    
    
def write_to_file(account_data):
    with open('account.csv', 'w') as f:
        writer = csv.DictWriter(f, fieldnames=['id', 'amount'])
        writer.writeheader()
        writer.writerows (account_data)       
        
   

def calculate_credit(credit_data, account_data):
     #Идём дальше только если у клиента есть кредит
        #и счётчик месяцев не равен 0
        if float(credit['sum']) > 0 and credit["months_counter"] != 0:
            #Расчёт месечного платежа
            monthly_payment = round(float(credit['sum_total']) / (float(credit['term']) * 12), 2)
            #Идём по нашим счетам
            for account in account_data:
                #Находим счёт с id клинета
                if int(account['id']) == account_id:
                    current_amount = float(account['amount'])
                    #вычитаем со счёта клиента месячный платёж
                    account['amount'] = current_amount  - monthly_payment
                    credit["months_counter"] -= 1
                    if float(account['amount']) > 0: # проверяем, что счет клиента больше 0
                        #Добавляем сумму на счёт банкa
                        account_data[0]['amount'] = float(account_data[0]['amount']) + monthly_payment
                    else:
                        #Добавляем остаток на счёте
                        #в случаях когда сумма на счёте была
                        #чуть меньше monthly_payment
                        if current_amount > 0:
                           account_data[0]['amount'] = float(account_data[0]['amount']) + current_amount
                        #Печатаем сколько клиент должен заплатить ещё. Берём по модулю сумму на счёте
                        print(f"Дорогой клиент, {account_id} Сумма задолженности {abs(account['amount'])}")

write_to_file(account_data)

    

def calculate_deposits(deposit_data, account_data):
    for deposit in deposit_data:
        account_id = int(deposit['id'])
        #Идём дальше только если у клиента есть депозит 
        #и счётчик месяцев не равен 0
        if deposit['sum'] > 0 and deposit["months_counter"] != 0:
                sum_to_add = float(deposit['sum_total']) / (deposit['term'] * 12) # Рассчитываем сумму, которую надо добавлять в месяц
                for account in account_data:
                    if str(deposit['id']) == account['id']:
                        # Добавляем сумму на счет клиента и списываем со счета банка
                        account['amount'] = str(float(account['amount']) + sum_to_add)
                        account_data[0]['amount'] = str(float(account_data[0]['amount']) - sum_to_add)
                        deposit['months_counter'] -= 1

write_to_file(account_data)

def main():
    credit_data, deposit_data, account_data = load_data()
    
    while True:
        calculate_credit(credit_data, account_data)
        calculate_deposit(deposit_data, account_data)
        time.sleep(10)

if __name__ == '__main__':
    main()   
    
