
import numpy as np
import matplotlib.pyplot as plt
from tensorflow import keras
from tensorflow.keras.datasets import mnist  
from tensorflow.keras.layers import Dense, Flatten, Dropout, Conv2D, MaxPooling2D
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from google.colab import files
import time

"""Загрузим датасет из базы данных рукописных цифр MNIST:"""

(train_images, train_labels), (test_images, test_labels) = mnist.load_data()

"""Каждое изображения имеет разрешение 28x28 пикселей и представлено в черной-белом цвете."""

#рассмотрим пример такого изображения
plt.imshow(train_images[3], cmap=plt.cm.binary)
print(train_images[3].shape)

"""Нейронная сеть гораздо быстрее работает со значениями, 
находящимися в диапазоне от 0 до 1, поэтому стандартизируем наши данные, 
чтобы наибольшее значение было равно 1:"""

#стандартизируем входные данные
train_images = train_images / 255
test_images = test_images / 255

"""Преобразуем лейблы наших изображений в векторы размерности 10x1. 
Для i+1 лейбла вектор выглядит следующим образом: на i позиции стоит 1, а на всех остальных - 0."""

train_labels_cat = keras.utils.to_categorical(train_labels, 10)
test_labels_cat = keras.utils.to_categorical(test_labels, 10)

#рассмотрим пример 
print(train_labels[3])
print(train_labels_cat[3])
print(train_labels_cat[3].shape)

"""На вход сверточному слою нейросети подается тезор размерности 4, 
поэтому нам необходимо к нашей обучающей и тестовой выборке добавить одну размерность:"""

train_images = np.expand_dims(train_images, axis=3)
test_images = np.expand_dims(test_images, axis=3)

"""Используя метод Sequential из библиотеки keras, создаем модель нашей нейросети. Она состоит из семи слоев, 
пять из которых скрытые. Первые четыре слоя - сверточные, последующие три слоя составляют простейшую 
полносвязную нейросеть, в которую передается вектор размерностью 3. 
По концепции сверточных нейронных сетей: каждый последующий слой должен укрупнять масштаб полученных признаков, 
поэтому после сверточного слоя Conv2D идет слой MaxPooling2D, который выбирает максимальные значения из квадратов, 
выбранного размера, уменьшая карту признаков.
"""

model = keras.Sequential([
    Conv2D(32, (3,3), padding='same', activation='relu', input_shape=(28, 28, 1)),
    MaxPooling2D((2, 2), strides=2),
    Conv2D(64, (3,3), padding='same', activation='relu'),
    MaxPooling2D((2, 2), strides=2),
    Flatten(),
    Dense(128, activation='relu'),
    Dense(10,  activation='softmax')
])

"""Так как наша задача состоит в классификации изображений более чем на 2 класса, 
а также функция softmax является функцией активации для выходного слоя, в качестве критерия качества 
мы будем использовать категориальную кроссэнтропию."""

model.compile(optimizer='adam', 
             loss='categorical_crossentropy', 
             metrics=['accuracy'])

print(model.summary())

"""Начнем обучение нашей модели на тренировочных данных. 
В датасете из библиотеки MNIST 60, 000 изображений составляют обучающую выборку. 
Мы разделим эту выборку на два класса - непосредственно обучающую выборку и выборку валидации, 
которая будет составлять 20% от общего объема обучающей выборки (12, 000 изображений)."""

t=time.time()
fit = model.fit(train_images, train_labels_cat, batch_size=32, epochs=5, validation_split = 0.2)
t = time.time() - t

print("Время обучения модели: ", t, "с")

"""Оценим работу нашей модели на тестовой выборке (она составляет 10, 000 изображений):"""

eval = model.evaluate(test_images, test_labels_cat)

print("Точность: {}%".format(round(eval[1]*100,4)))

"""Построим графики точности и потерь на каждой итерации:
"""

f = plt.figure(figsize=(20,7))

 
f.add_subplot(121)

plt.plot(fit.epoch, fit.history['accuracy'], label = "Точность") 
plt.plot(fit.epoch, fit.history['val_accuracy'], label = "Контрольная точность")  

plt.title("График точности", fontsize=16)
plt.xlabel("Эпоха", fontsize=12)
plt.ylabel("Точность", fontsize=12)
plt.grid(alpha = 0.3)
plt.legend()

 
f.add_subplot(122)

plt.plot(fit.epoch, fit.history['loss'], label = "Потери") 
plt.plot(fit.epoch, fit.history['val_loss'], label = "Контрольные потери") 
plt.title("График потерь", fontsize=16)
plt.xlabel("Эпоха", fontsize=12)
plt.ylabel("Потери", fontsize=12)
plt.grid(alpha = 0.3)
plt.legend()

plt.show()

files.upload()

"""Проверим работу нашей нейронной сети на изображениях, которые не участвовали в обучении, 
и определим ее точность:"""

correct = 0

wrong_img = []
wrong_labels = []

rows = 2
cols = 5

f = plt.figure(figsize=(2*cols, 2*rows))

for i in range(rows * cols): 
    img = load_img(f'{i}.jpg')
    img_array = img_to_array(img)
    img_array = img_array / 255
    img_array = img_array[:,:,:1].reshape([1,28,28,1])
    pred = np.argmax(model.predict(img_array), axis = 1)[0]
    
    f.add_subplot(rows,cols,i+1)
    img_array=img_array.reshape([28,28])
    plt.imshow(img_array, cmap="Blues") 
    plt.axis("off")
    plt.title("{}".format(pred), y=-0.15, color="green")

    if i == pred:
      correct += 1

    if i != pred:
      wrong_img.append(img_array)
      wrong_labels.append(pred)

plt.plot()

print("Точность распознавания изображений не участвовавших в обучении: ", (correct / 10)*100, "%")

"""Выведем изображения цифр, которые нейросеть распознала неверно:"""

f = plt.figure(figsize=(8, 4))

n = 10 - correct

for i in range(n):
  f.add_subplot(1,n,i+1)
  plt.imshow(wrong_img[i], cmap="Blues") 
  plt.title("{}".format(wrong_labels[i]), y=-0.15, color="red")

"""Сохраним нашу модель:"""

model.save('model.h5')