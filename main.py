data_sum = [
    "1_1000",
    "2_30000",
    "3_100000",
    "8_100",
    "5_11111",
    "9_14124124124",
    "6_444",
    "4_123456",
    "7_100000000000",
    "10_81214",
]
data_sum.sort(key=lambda x: int(x.split("_")[0]))

data_rate = [
    "1_10",
    "2_11",
    "3_8",
    "4_13",
    "5_11",
    "6_6",
    "7_9",
    "8_11",
    "9_13",
    "10_12",
]

data_term = ["1_1", "2_2", "3_2", "4_6", "5_8", "6_20", "7_9", "8_11", "9_13", "10_12"]

# Объявляем пустой список для записи в нее результата в последующем.
results = []
a_hard_perncent = results
# Проходимся циклом по массиву с функцией range, которая создает последовательность чисел от 0 с шагом 1 до конечного значения в нашел случаи.
# функцией len расчитываем кол-во элементов в списке, т.е длинну.
for i in range(len(data_sum)):
    # Разделение строки на отдельные переменные. Пример (id  и start_sum).
    # id, start_sum = data_sum[i].split('_')
    # id, rate = data_rate[i].split('_')
    # id, term = data_term[i].split('_')
    id, start_sum = data_sum[i].split("_")
    id, rate = data_rate[i].split("_")
    id, term = data_term[i].split("_")

    # Чтобы потом выполнить расчёты преобразовываем строковые значения в числа.
    start_sum = int(start_sum)
    rate = float(rate)  # float - тип данных, числа с плавающей запятой.
    term = int(term)

    # Расчёт итоговой суммы по формуле вычисления сложного процента.
    end_sum = start_sum * (1 + rate / 100) ** term

    # Создание словаря с результатом
    result = {
        "id": id,
        "start_sum": start_sum,
        "rate": rate,
        "term": term,
        "end_sum": end_sum,
    }

    # Добавления словаря в список функции append.
    results.append(result)

print(
    "{:<5} {:<12} {:<8} {:<10} {:<10}".format(
        "id".upper(),
        "start_sum".upper(),
        "rate".upper(),
        "term".upper(),
        "end_sum".upper(),
    )
)
for result in results:
    print(
        "{:<5} {:<12} {:<8} {:<10} {:<10}".format(
            result["id"].upper(),
            str(result["start_sum"]).upper(),
            str(result["rate"]).upper(),
            str(result["term"]).upper(),
            str(result["end_sum"]).upper(),
        )
    )


# Commit памятка, что сделал:
# Данный код представляет собой скрипт, который использует данные, представленные в трёх списках - data_sum, data_rate и data_term, и выполняет расчеты итоговых сумм по формуле сложного процента для каждого элемента списка.

# Первые три списка содержат информацию о стартовой сумме start_sum, процентной ставке rate и сроке вклада term для каждого элемента.

# Создаётся пустой список results, в который будут добавлены результаты вычислений для каждого элемента. Далее в цикле for перебираются элементы списка data_sum с помощью функции range(), которая создает последовательность чисел от 0 с шагом 1 до конечного значения в данном случае - длины списка data_sum.

# Внутри цикла строка data_sum[i] разбивается на две переменные id и start_sum с помощью метода split(). Аналогичная операция выполняется для элементов списков data_rate и data_term.

# Затем строки, содержащие числа, преобразуются из типа str в типы int и float, соответственно, с помощью функций int() и float().

# Далее производятся расчеты итоговой суммы end_sum по формуле сложного процента и создается словарь с результатами вычислений result, который включает id, start_sum, rate, term и end_sum. Этот словарь добавляется в список results с помощью метода append().

# В конце выполнения скрипта выводится на экран список results, содержащий результаты вычислений для каждого элемента списка.


# ФОРМАТИРОВАНИЕ В ТАБЛИЦУ:
# Распределение значений по столбцам и строкам происходит с помощью форматирования строк в Python.
# В строке форматирования '{:<5} {:<12} {:<8} {:<10} {:<10}' каждый из фрагментов между фигурными скобками {} представляет отдельный столбец в выводимой таблице.
# Между фигурными скобками можно указать дополнительные параметры, например, '<' означает выравнивание по левому краю, а число после двоеточия - ширину столбца.
# Таким образом, строка форматирования указывает, что в выводимой таблице должно быть 5 столбцов: первый столбец шириной 5 символов, второй - шириной 12 символов,
# третий - шириной 8 символов, четвертый - шириной 10 символов, пятый - шириной 10 символов. Каждый столбец разделен от другого пробелами.
# Когда мы используем эту строку форматирования в команде print(), мы передаем значения для каждого столбца в порядке их расположения в строке форматирования,
# и Python автоматически выравнивает их по заданным параметрам, чтобы получилась таблица.

#LESSON 17        

import json
import csv
import yaml

# Открываем и считываем информацию из файлов
with open('credit.json') as f:
    credit_data = json.load(f)

with open('deposit.yaml') as f:
    deposit_data = yaml.load(f, Loader=yaml.FullLoader)

with open('account.csv') as f:
    account_data = list(csv.DictReader(f))

# Сортируем списки по возрастанию id
credit_data = sorted(credit_data, key=lambda x: x['id'])
deposit_data = sorted(deposit_data, key=lambda x: x['id'])
account_data = sorted(account_data, key=lambda x: int(x['id']))

for i in credit_data + account_data:
    i["sum_total"] = end_sum
    i["months"] = 12
    i["months_counter"] = 12   

import csv
import time
import json

# def read_from_file():
#      with open('account.csv', 'r') as f:
#         reader = csv.DictReader(f)
#         account_data = [row for row in reader]
#         return account_data
def write_to_file(account_data):
    with open('account.csv', 'w') as f:
        writer = csv.DictWriter(f, fieldnames=['id', 'amount'])
        writer.writeheader()
        writer = csv.DictWriter(f, fieldnames=['id', 'amount', 'months', 'months_counter', 'sum_total'])

        # writer.writerows (account_data)       
        
total_credit_sum = sum(float(credit['sum']) for credit in credit_data)
account_data[0]['amount'] = str(float(account_data[0]['amount']) - total_credit_sum)    

      

def calculate_credit():
    for credit in credit_data:
        if float(credit['sum']) > 0:
            monthly_payment = end_sum / (float(credit['term']) * 12) 
            account_id = int(credit['id'])
            for account in account_data:
                if int(account['id']) == account_id:
                    account['amount'] = str(float(account['amount']) - monthly_payment)
                    if float(account['amount']) < 0:
                        print(f"Дорогой клиент, {account_id} погасите ваш кредит. Сумма задолженности {credit['sum']}")
                    else:
                        account_data[0]['amount'] = str(float(account_data[0]['amount']) + monthly_payment)
                        for dicto in credit_data + account_data:
                            dicto["months_counter"] -= 1
    write_to_file(account_data)

    
import csv

def calculate_deposits(deposit_data, account_data):
    for deposit in deposit_data:
        if deposit['term'] > 0:
            # Рассчитываем сумму, которую надо добавлять в месяц
            sum_to_add = end_sum / (deposit['term'] * 12)
            for account in account_data:
                if str(deposit['id']) == account['id']:
                    # Добавляем сумму на счет клиента и списываем со счета банка
                    account['amount'] = str(float(account['amount']) - sum_to_add)
                    account['sum_total'] = str(float(account['sum_total']) + sum_to_add)
                    account['months_counter'] = int(account['months_counter']) - 1
                    
write_to_file(account_data)

while True:
    for dictor in credit_data:
        if dictor["months_counter"] < 0:
            print(f"Расчёт окончен")
            break
        else:  
            calculate_credit()
            calculate_deposits(deposit_data, account_data)
            time.sleep(10)    