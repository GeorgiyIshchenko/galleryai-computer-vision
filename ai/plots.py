import os
import math
import numpy as np
import matplotlib.pyplot as plt
from tasks import dataset_by_filenames, Train, Prediction


def train():
    model = Train()
    model.save("W:\ПРОГА\ПРЕДЗАЩИТА\model")


def test():
    dirname = r"W:\ПРОГА\ПРЕДЗАЩИТА\media\predict\match"
    files = os.listdir(dirname)
    class1 = map(lambda name: os.path.join(dirname, name), files)
    class1 = list(class1)

    class1_size = len(class1)

    dirname = r"W:\ПРОГА\ПРЕДЗАЩИТА\media\predict\not match"
    files = os.listdir(dirname)
    class2 = map(lambda name: os.path.join(dirname, name), files)
    class2 = list(class2)

    class2_size = len(class2)

    print(class1_size, class2_size)

    total_size = class1_size + class2_size
    result = Prediction()
    print(result)
    x_list = list()
    accuracy_list = list()
    precision_list = list()
    recall_list = list()
    delta = 1
    best = -1
    MAX_F1 = 0
    MAX_F1_X = 0
    for j in range(100):
        TP = 0
        TN = 0
        FP = 0
        FN = 0
        right_predictions = 0
        x = j * 0.01
        x_list.append(x)
        for i in range(1, total_size + 1):
            if i <= class1_size:
                if result[i - 1] > x:
                    TP += 1
                else:
                    FN += 1
            else:
                if result[i - 1] > x:
                    FP += 1
                else:
                    TN += 1

            if result[i - 1] > x:
                if i <= class1_size:
                    right_predictions += 1
            if result[i - 1] < x:
                if i > class1_size:
                    right_predictions += 1

        precision = TP / (TP + FP)
        recall = TP / (TP + FN)
        accuracy = right_predictions / total_size
        F1 = 2 * precision * recall / (precision + recall)
        if abs(precision - recall) < delta:
            best = x
            bestacc = accuracy
            delta = abs(precision - recall)
        print("x: ", x, " precision: ", precision, " recall: ", recall, " accuracy: ", accuracy, " F1: ", F1)
        precision_list.append(precision)
        recall_list.append(recall)
        accuracy_list.append(accuracy)
    print(accuracy_list)
    print(best, 1 - bestacc)
    chart(x_list, precision_list, recall_list)


def chart(x, y1, y2):
    fig = plt.figure(figsize=(8, 8))
    ax = plt.subplot(1, 1, 1)
    plt.plot(x, y1, color="red", label="precision")
    plt.plot(x, y2, color="green", label="recall")
    ax.legend();
    ax.set_xlabel("Пороговое значение", fontsize=12)
    ax.set_ylabel("Значение", fontsize=12)
    plt.show()
    fig.savefig("кубизм.jpg")


def plot_3D(b, name):
    Precision, Recall = np.mgrid[0.001:1:250j, 0.001:1:150j]
    Fb = (1 + b * b) * (Precision * Recall) / (b * b * Precision + Recall)
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection='3d')
    ax.plot_surface(Precision, Recall, Fb)
    ax.set_xlabel("Precision", fontsize=15)
    ax.set_ylabel("Recall", fontsize=15)
    ax.set_zlabel("F" + str(b) + " - мера", fontsize=15)
    ax.invert_yaxis()
    # ax.legend()
    plt.show()
    fig.savefig("F/" + "F" + name + ".jpg")


def ar(middle_x, middle_y, dx, dy, color):
    middle_x -= dx / 2.0
    middle_y -= dy / 2.0
    plt.arrow(middle_x, middle_y, dx, dy,
              width=0.008, ec="black", fc=color)


def get_color(length):
    max = 1.757829861025378
    min = 0.7071067811865476
    color2 = [254, 0, 236]
    color1 = [2, 201, 175]
    a = max - length
    b = length - min
    R = color1[0] * a / (a + b) + color2[0] * b / (a + b)
    G = color1[1] * a / (a + b) + color2[1] * b / (a + b)
    B = color1[2] * a / (a + b) + color2[2] * b / (a + b)
    return (R / 256, G / 256, B / 256)


def grad():
    fig = plt.figure(figsize=(8, 8))
    ax = plt.subplot(1, 1, 1)
    min = 0
    for i in range(1, 16):
        for j in range(1, 16):
            point_x = i / 15.0
            point_y = j / 15.0
            dx = 2 * math.pow(point_y, 2) / math.pow(point_x + point_y, 2)
            dy = 2 * math.pow(point_x, 2) / math.pow(point_x + point_y, 2)
            length = math.pow(math.pow(dx, 2) + math.pow(dy, 2), 0.5)
            if length > min:
                min = length
            x = 0.03 / length
            dx *= x
            dy *= x
            ar(point_x, point_y, dx, dy, get_color(length))
            ax.set_xlabel("Precision", fontsize=12)
            ax.set_ylabel("Recall", fontsize=12)

    fig.savefig("градиент.jpg")
    plt.show()


def t():
    dirname = r"W:\ПРОГА\ПРЕДЗАЩИТА\media\predict\match"
    files = os.listdir(dirname)
    class1 = map(lambda name: os.path.join(dirname, name), files)
    class1 = list(class1)

    class1_size = len(class1)

    dirname = r"W:\ПРОГА\ПРЕДЗАЩИТА\media\predict\not match"
    files = os.listdir(dirname)
    class2 = map(lambda name: os.path.join(dirname, name), files)
    class2 = list(class2)

    class2_size = len(class2)

    print(class1_size, class2_size)

    total_size = class1_size + class2_size
    result = Prediction()
    print(result)
