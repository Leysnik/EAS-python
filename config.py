#server config
PORT = 8080
HOST = "localhost"

#data config

## dict with column names(xls->sql)
COLUMN_NAMES = {"index" : "index",
               "Дата платежа" : "date",
               "Сумма операции" : "oSum",
               "Категория" : "category",
               "Кэшбэк" : "cashback",
               "MCC" : "mcc",
               "Описание" : "description",
                "Статус" : "status"
               }

##list with useless columns
USELESS_COLUMNS = ['Дата операции', 'Номер карты', 'status',
           'Сумма платежа', 'Валюта платежа', 'Валюта операции',
           'Бонусы (включая кэшбэк)', 
           'Округление на инвесткопилку',
           'Сумма операции с округлением']