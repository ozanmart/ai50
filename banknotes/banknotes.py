import csv
import random

from sklearn import svm
from sklearn.linear_model import Perceptron
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB

# model = Perceptron()
# model = svm.SVC()
model = KNeighborsClassifier()

with open("banknotes.csv") as f:
    reader = csv.reader(f)
    next(reader)

    data = []
    for row in reader:
        data.append(
            {
                "evidence": [float(col) for col in row[:4]],
                "label": "Authentic" if row[4] == "0" else "Counterfeit"
            }
        )

    hold_out = int(0.4 * len(data))
    random.shuffle(data)

    x_training_set = [row["evidence"] for row in data[hold_out:]]
    y_training_set = [row["label"] for row in data[hold_out:]]
    model.fit(x_training_set, y_training_set)

    x_testing_set = [row["evidence"] for row in data[:hold_out]]
    y_testing_set = [row["label"] for row in data[:hold_out]]
    predictions = model.predict(x_testing_set)

    correct = 0
    incorrect = 0
    for (prediction, actual) in zip(predictions, y_testing_set):
        if prediction == actual:
            correct += 1
        else:
            incorrect += 1

    print(f"Results for model {type(model).__name__}")
    print(f"Correct: {correct}")
    print(f"Incorrect: {incorrect}")
    print(f"Accuracy: {100 * correct / (correct + incorrect):.2f}%")
