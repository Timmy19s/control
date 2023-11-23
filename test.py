

print('Ваня, ответь!')


answer="Otvet"
print(answer)


from random import choice
answer_pc = choice(('Что Это?','Убери телефон!','bitch'))
print(answer_pc)


from random import randint
random_n = randint(0,2)
if random_n == 0:
    print("telephon, bich")
elif random_n == 1:
    print("eto rech")
else:
    print("mislya ot prosmotra Armanyskih prezentci")
    

k = randint(1,5)
print(f'Когда мы {"bich_"*k}')

s= input("1 или 2?")
if s == "1":
    print("Always has been")
else:
    print("C etoi prezentacii")