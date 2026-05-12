# '''
# x = input('1. sayı: ')
# y = input('2. sayı: ')
# z = input('3. sayı: ')
# toplam = float(x) + float(y) + float(z) #float eklersek ondalıklı int eklersek düz hesaplar
# print(toplam) 

# x = input('1. sayı: ')
# y = input('2. sayı: ')
# print(type(x)) #input ile alınan değerler str tipindedir
# print(type(y)) 
# toplam = int(x) + int(y) 
# print(toplam) 

# x = 5
# y = 2.3
# name = 'alperen'
# cinsiyet = True
# print(type(x))
# print(type(y))
# print(type(name))
# print(type(cinsiyet))
# print('-------------------')

# x = float(x) #int i float a çevirdik
# print(x)
# print(type(x))  
# y = int(y) #float ı int e çevirdik
# print(y)     
# print(type(y))
# print('-------------------')
# result = x + y 
# print(result)
# print(type(result))
# print('-------------------')
# cinsiyet = str(cinsiyet) #bool u str ye çevirdik
# print(cinsiyet) 
# print(type(cinsiyet))
# print('-------------------')

# cinsiyet = int(cinsiyet) #bool u int e çevirdik, true olduğu için 1 der
# print(cinsiyet)
# print(type(cinsiyet))
# print('-------------------')

# pi = 3.14
# yaricap = float(input('yarıçapı girin: '))
# alan = pi * yaricap ** 2
# cevre = 2 * pi * yaricap
# print('alan: ', alan)
# print('çevre : ' , cevre)

# name = 'hazal'
# surname = 'savaş'
# age = 22

# greeting = 'benim adım ' + name + ' ' + surname + ' ve yaşım ' + str(age)
# print(f'benim adım {name} {surname} ve yaşım {age}')
# print(greeting[0]) #ilk harfi yazdırır
# print(greeting[3]) #4. harfi yazdırır
# print(greeting[-1]) #son harfi yazdırır
# print(greeting[-3]) #sondan 3. harfi yazdırır
# print(greeting[0:5]) #0 dan 5 e kadar olan kısmı yazdırır
# print(greeting[3:8]) #3 den 8 e kadar olan kısmı yazdırır
# print(greeting[0:]) #başlangıçtan sona kadar yazdırır
# print(greeting[:10]) #başlangıçtan 10 a kadar yazdırır
# print(greeting[::2]) #2 şer 2 şer atlayarak yazdırır
# print(greeting[::-1]) #tersten yazdırır
# print(len(greeting)) #karakter sayısını yazdırır
# print(greeting.lower()) #tüm harfleri küçültür
# print(greeting.upper()) #tüm harfleri büyültür
# print(greeting.replace('a' , '@')) #a harflerini @ ile değiştirtirir
# print(greeting.split()) #boşluklardan ayırır ve liste yapar
# print('ad' in greeting) #greeting içinde ad var mı diye kontrol eder, varsa true yoksa false döner
# print('xyz' in greeting) #greeting içinde xyz var mı diye kontrol eder, varsa true yoksa false döner
# print(greeting.index('savaş')) #savaş kelimesinin başladığı indexi verir
# print(greeting.index('a')) #ilk a harfinin başladığı indexi verir 
# print(greeting.count('a')) #greeting içinde kaç tane a harfi olduğunu sayar
# print(greeting.count('z')) #greeting içinde kaç tane z harfi olduğunu sayar
# print('-------------------') '''
# '''name = 'hazal'
# surname = 'savaş'
# age = 22
# print ('benim adım {} {} ve yaşım {}'.format(name , surname , age))
# print ('benim adım {1} {0} ve yaşım {2}'.format(surname , name , age))  
# print ('benim adım {n} {s} ve yaşım {a}'.format(n = name , s = surname , a = age))
# '''
# '''result = 3 + 2 * 4 / 2 - 1  #matematikteki işlem önceliğine göre hesaplar
# print(result)
# result = (3 + 2) * (4 / 2 - 1)  #parantez içinden başlayarak işlem önceliğine göre hesaplar
# print(result)
# result = 200 / 700
# print('the result is {:.2f}'.format(result))  #virgülden sonra 2 basamak gösterir
# print(f'the result is {result:.3f}')  #virgülden sonra 3 basamak gösterir
# print('-------------------')
# x = 5
# x += 3  #x = x + 3 ile aynı anlama gelir
# print(x)

# website = 'http://www.pythonilk.com'
# course = 'python kursu: baştan sona python programlama rehberi'

# # 1- 'course' karakter dizisinde kaç karakter bulunmaktadır?
# print(len(course))
# # 2- 'website' içinden www karakterlerini alın.
# print(website[7:10])    
# # 3- 'website' içinden com karakterlerini alın.
# print(website[-3:])
# # 4- 'course' karakter dizisinin tüm karakterlerini büyük harf yapın.
# print(course.upper())
# # 5- 'course' karakter dizisinin tüm karakterlerini küçük harf yapın.
# print(course.lower())
# # 6- 'website' karakter dizisinde kaç tane a karakteri bulunmaktadır?
# print(website.count('a'))
# # 7- 'course' karakter dizisinde 'python' kelimesi kaç kere geçmektedir?
# print(course.count('python'))
# # 8- 'website' karakter dizisinin 'www' ile başlayıp '.com' ile bitip bitmediğini kontrol edin.
# print(website.startswith('www'))    
# print(website.endswith('.com'))
# # 9- 'course' karakter dizisinde 'programlama' kelimesinin başlangıç indexi nedir?
# print(course.index('programlama'))
# # 10- 'course' karakter dizisindeki tüm boşluk karakterlerini '-' ile değiştirin.
# print(course.replace(' ', '-'))
# # 11- 'course' karakter dizisini boşluk karakterlerinden ayırın.
# print(course.split())   '''
# '''message = "Hello, World!"
# message = message.upper() # Tüm harfleri büyük yap
# print(message)  # Çıktı: "HELLO, WORLD!"
# message = message.lower() # Tüm harfleri küçük yap
# print(message)  # Çıktı: "hello, world!"
# message = message.replace("world", "Python") # "world" kelimesini "Python" ile değiştir
# print(message)  # Çıktı: "hello, Python!"
# message = message.split(", ") # Virgülden ayırarak liste yap
# print(message)  # Çıktı: ['hello', 'Python!']
# print(len(message))  # Çıktı: 2 (liste uzunluğu)
# message = message.title() # İlk harfleri büyük yap
# print(message)  # Çıktı: "Hello Python!"
# message = message.capitalize() # Sadece ilk harfi büyük yap
# print(message)  # Çıktı: "Hello python!"
# '''
# message = "Hello , My name is Hazal Savaş!"
# # message = message.split() #boşluklardan ayırarak liste yapar
# # print(message)  # Çıktı: ['Hello', ',', 'My', 'name', 'is', 'Hazal', 'Savaş!']
# # message = ' '.join(message) #listeyi boşluklarla birleştirir
# # print(message)  # Çıktı: "Hello , My name is Hazal Savaş!"
# # messaage = '*'.join(message) #karakterlerin arasına * ekler
# # print(messaage)  # Çıktı: "H*e*l*l*o* * ,* *M*y* *n*a*m*e* *i*s* *H*a*z*a*l* *S*a*v*a*s*!
# # index = message.index('Hazal') #Hazal kelimesinin başladığı indexi verir
# # print(index)  # Çıktı: 17
# # isFound = message.startswith('Hello') #Hello ile başlayıp başlamadığını kontrol eder
# # print(isFound)  # Çıktı: True
# # isFound = message.endswith('Savaş!') #Savaş! ile bitip bitmediğini kontrol eder
# # print(isFound)  # Çıktı: True
# # message = message.replace('Hazal' , 'Alperen') #Hazal kelimesini Alperen ile değiştirir
# # print(message)  # Çıktı: "Hello , My name is Alperen Savaş!"
# # message = message.center(100) #karakter dizisini 100 karakterlik alanda ortalar
# # print(message)  # Çıktı: "                     Hello , My name is Alperen Savaş!
# # messsage = messsage.center(20 , '*') #karakter dizisini 20karakterlik alanda ortalar ve boşlukları * ile doldurur
# # print(messsage)  # Çıktı: "*****Hello , My name is Alperen Savaş!*****"
# # message= message.lstrip()   #karakter dizisinin solu ndaki boşlukları siler
# # print(message)  # Çıktı: "Hello , My name is Alperen Savaş!                     "
# # message= message.rstrip()   #karakter dizisinin sağındaki boşlukları siler
# # print(message)  # Çıktı: "Hello , My name is Alperen Savaş !"
  # Çıktı: ['python', 'öğreniyorum']
# metin = "##  pyThOn ## öğrenİyorum ## çok ## koLay ##"
# metin = metin.lower()
# metin = metin.replace('#', ' ')
# metin = metin.replace('  ', ' ')
# metin = metin.strip()
# print(metin)

# vize = float(input('vize notunu girin: '))
# final = float(input('final notunu girin: '))
# ortalama = vize * 0.4 + final * 0.6
# if ortalama >= 90:
#     print('AA') 
# elif ortalama >= 80:
#     print('BA')
# elif ortalama >= 70:
#     print('BB')
# elif ortalama >= 60:
#     print('CB')
# elif ortalama >= 50:
#     print('CC')
# elif ortalama >= 40:
#     print('DC')  


# sayilar = [1, 3,5,7,9,12,19,21]
# i = 0
# while i < len(sayilar):
#     print(sayilar[i])
#     i += 1  (i yi 1 artırarak sıradaki sayıya geçer sayıları ekrana yazdırır)
# baslangic = int(input('başlangıç değeri: '))
# bitis = int(input('bitiş değeri: '))
# i = baslangic 
# while i < bitis : 
#     i +=1
#     if(i % 2 ==1):
#         print(i)
number =[]
i = 0
while i < 5:
    sayi = int(input('sayı: '))
    number.append(sayi)
    i += 1
number.sort()
print(number)