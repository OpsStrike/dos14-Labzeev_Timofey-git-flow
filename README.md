
## Homework 14

## _Tasks_

- 1 Создать новый репозиторий dos14-
family_name-git-flow
- 2 Создать 2 ветки master develop 
> [git checkout -b branch_name]
- 3 Cоздать ветку feature-hw-14
- 4 Добавит информацию о репозитории в
README.md
- 5 Сделать pull request в develop (после апрува
@ggramal смерджить) (cмерджить все ветки с
предыдущими домашками*) 
> [git merge develop]
- 6 Сделать из develop release-v0.0.1
- 7 Cмерджить в master и сделать тэг v0.0.1
> [(git tag -a v0.0.1 -m "beta ver..."; git push origin v0.0.1)]
- 8 Удалить release-v0.0.1 
> [( git push origin -d branch_name, local - git branch -D branch_name)]



## Homework 15

## _Tasks_

- Установить python 3.11 через pyenv
- Создать проект с помощью poetry
- Добавить группу зависимостей dev, сделать её опциональной и добавить black пакет
- Создать main.py с кодом - если перменная среды SHELL равна ‘/bin/bash’ напечатать в консоль Greetings bash если другое значение Hello <значение переменной среды>
- Сделать black ./
- Закоммитить все файлы (pyptoject.toml, poetry.lock, main.py etc) в feature ветку, слить ее с develop(без апрува)
- По готовности сделать пулл реквест в master с апрувером @ggramal, отписаться в тг канале

## Homework 16

## _Task_
- Расчёт сложного процента
# Исправления
- Отсортировал data_sum
- использовал black
- переименовал файл

## Homework 18

## _Task_
- Создать класс BankProduct

- задать свойства entity_id, percent, term, sum

- задать свойство end_sum Расчёт сложного процента (используя свойства объекта)

- свойства эти должны быть только на чтение

- создать метод process он должен быть абстрактным те никакой конкретной реализации не должно быть

- Создать класс Credit

- Унаследоваться от BankProduct

- Создать свойство только на чтение periods = term*12

- Создать свойство только на чтение closed = False

- Создать свойство monthly_fee = end_sum / term*12

- Реализовать метод process

- Записать транзакции в файл transactions.csv

- user_id,monthly_fee,'substract'

- 0,monthly_fee,'add'

- Уменьшить priods на 1

- Если periods == 0 то closed = True

- Создать класс Deposit

- Унаследоваться от BankProduct

- Создать свойство только на чтение periods = term*12

- Создать свойство только на чтение closed = False

- Создать свойство monthly_fee = end_sum / term*12

- Реализовать метод process

- Записать транзакции в файл transactions.csv

- user_id,monthly_fee,'add'

- 0,monthly_fee,'substract'

- Уменьшить priods на 1

- Если periods == 0 то closed = True

- Из базы данных credits_deposits.json получить данные

- На их основании создать объекты Кредитов и депозитов

- Каждый месяц вызывать у этих объектов метод process

- Если кредит, депозит закрыт удаляем его из списка и пишем в бд (файл credits_deposits.json)


## Homework 26
- ссылка на создание кредита или депозита curl -X PUT "localhost/api/v1/deposits?client_id=25&percent=15&sum=1000&term=2&periods=-1"
- Если не работает nginx проверять default.conf /etc/nginx/conf.d/

## Homework 29
- Файл с паролем зашифрован ansible-vault, команда:  ansible-vault create secrets.yml/расшифровка ansible-vault decrypt secrets.yml
- При запускке ansible указывать  --ask-vault-pass
