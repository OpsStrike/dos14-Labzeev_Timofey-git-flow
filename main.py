

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
        sum_total = float(credit['sum']) * float(credit['term'])
        credit['sum_total'] = str(sum_total)
        
    total_credit_sum = sum(float(credit['sum']) for credit in credit_data)
    account_data[0]['amount'] = str(float(account_data[0]['amount']) - total_credit_sum) 

    for i in credit_data + account_data:
        i["months"] = 12
        i["months_counter"] = 12       
       
    # Расчёт и запись значения sum_total в account_data
    for account in account_data:
            sum_total = float(credit['sum']) * float(credit['term'])
            account["sum_total"] = str(sum_total)
    return credit_data, deposit_data, account_data   
    
    
def write_to_file(account_data):
    with open('account.csv', 'w') as f:
        writer = csv.DictWriter(f, fieldnames=['id', 'amount', 'months', 'months_counter', 'sum_total'])
        writer.writeheader()
        #writer = csv.DictWriter(f, fieldnames=['id', 'amount'])
        writer.writerows (account_data)       
        
   

def calculate_credit(id, credit_data, account_data, sum_total_data):
    for credit in credit_data:
        account_id = int(credit['id'])
        if float(credit['sum']) > 0:
            monthly_payment = round(float(credit['sum']) / (float(credit['term']) * 12), 2)
            for account in account_data:
                if int(account['id']) == account_id:
                    if float(account['amount']) > 0: # проверяем, что счет клиента больше 0
                        account['amount'] = str(float(account['amount']) - monthly_payment)
                        if float(account['amount']) < 0:
                            print(f"Дорогой клиент, {account_id} Сумма задолженности {credit['sum']}")
                        else:
                            account_data[0]['amount'] = str(float(account_data[0]['amount']) + monthly_payment)
                            for dicto in credit_data + account_data:
                                dicto['months_counter'] = int(dicto['months_counter']) - 1
                    else:
                        print(f"Дорогой клиент, {account_id} у вас отрицательный баланс на счету, пожалуйста, пополните его")
    
    write_to_file(account_data)

    for credit in credit_data:
        account_id = int(credit['id'])
        sum_total = float(credit['sum']) * float(credit['term'])
        sum_total_data[account_id] = str(sum_total)

def calculate_deposits(deposit_data, account_data, credit_data):
    for deposit in deposit_data:
        if deposit['term'] > 0:
            for credit in credit_data:
                account_id = int(credit['id'])          
                sum_to_add = float(credit['sum_total']) / (deposit['term'] * 12) # Рассчитываем сумму, которую надо добавлять в месяц
                for account in account_data:
                    if str(deposit['id']) == account['id']:
                        # Добавляем сумму на счет клиента и списываем со счета банка
                        account['amount'] = str(float(account['amount']) - sum_to_add)
                        account['sum_total'] = str(float(account['sum_total']) + sum_to_add)
                        account['months_counter'] = int(account['months_counter']) - 1
                    
    write_to_file(account_data)

def main():
    credit_data, deposit_data, account_data = load_data()
    sum_total_data = {}
    
    is_first_iterration = True
    
    while True:
        if is_first_iterration:
            calculate_credit(id=None, credit_data=credit_data, account_data=account_data, sum_total_data=sum_total_data)
            is_first_iterration = False
        else:
            # При последующих итерациях используем сохранённые данные
            account_data = list(csv.DictReader(open('account.csv')))
            for account in account_data:
                account_id = int(account['id'])
                if account_id in sum_total_data:
                    account["sum_total"] = sum_total_data[account_id]

            calculate_credit(id=None, credit_data=credit_data, account_data=account_data, sum_total_data=sum_total_data)
            calculate_deposits(deposit_data=deposit_data, account_data=account_data, credit_data=credit_data)
        time.sleep(10)

if __name__ == '__main__':
    main()   
    