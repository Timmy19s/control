import sqlite3

# Создаем подключение к базе данных (файл my_database.db будет создан)
connection = sqlite3.connect('Basedata.db')
cursor = connection.cursor()

# Создаем таблицу Users
cursor.execute('''
CREATE TABLE IF NOT EXISTS KW (
key_word TEXT NOT NULL,
type TEXT NOT NULL
)
''')


# # Добавляем нового пользователя
# cursor.execute('INSERT INTO KW (key_word, type) VALUES (?, ?)', ('калькулятор', 'bad'))

# def f(type):
#     return f'{type}'
# connection.create_function("f", 1, f)
# k = 'Радужные друзья'

# Выбираем всех пользователей
cursor.execute('SELECT * FROM PS',)
users = cursor.fetchall()
print(users)


# bad_pr = tuple([i for i in cursor.fetchall()])
# print(bad_pr)
# if any(key_w in 'безымянный - paint' for key_w in bad_pr):
#     print('badsad')
# Сохраняем изменения и закрываем соединение
connection.commit()
connection.close()