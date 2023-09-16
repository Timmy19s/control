import datetime

string = '2023-09-16 10:59:09.478888'

k = datetime.datetime.strptime(string, '%Y-%m-%d %H:%M:%S.%f')

k = (datetime.datetime.now() - k).total_seconds()
print(k>20)
# print(k.minute)