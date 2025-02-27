import csv
import sys

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

TEST_SIZE = 0.4


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python shopping.py data")

    # Load data from spreadsheet and split into train and test sets
    evidence, labels = load_data(sys.argv[1])
    X_train, X_test, y_train, y_test = train_test_split(
        evidence, labels, test_size=TEST_SIZE
    )

    # Train model and make predictions
    model = train_model(X_train, y_train)
    predictions = model.predict(X_test)
    sensitivity, specificity = evaluate(y_test, predictions)

    # Print results
    print(f"Correct: {(y_test == predictions).sum()}")
    print(f"Incorrect: {(y_test != predictions).sum()}")
    print(f"True Positive Rate: {100 * sensitivity:.2f}%")
    print(f"True Negative Rate: {100 * specificity:.2f}%")


def load_data(filename):
    """
    Load shopping data from a CSV file `filename` and convert into a list of
    evidence lists and a list of labels. Return a tuple (evidence, labels).

    evidence should be a list of lists, where each list contains the
    following values, in order:
        - Administrative, an integer
        - Administrative_Duration, a floating point number
        - Informational, an integer
        - Informational_Duration, a floating point number
        - ProductRelated, an integer
        - ProductRelated_Duration, a floating point number
        - BounceRates, a floating point number
        - ExitRates, a floating point number
        - PageValues, a floating point number
        - SpecialDay, a floating point number
        - Month, an index from 0 (January) to 11 (December)
        - OperatingSystems, an integer
        - Browser, an integer
        - Region, an integer
        - TrafficType, an integer
        - VisitorType, an integer 0 (not returning) or 1 (returning)
        - Weekend, an integer 0 (if false) or 1 (if true)

    labels should be the corresponding list of labels, where each label
    is 1 if Revenue is true, and 0 otherwise.
    """

    with open("shopping.csv") as f:
        reader = csv.reader(f)
        next(reader)

        evidence = []
        labels = []
        for row in reader:
            counter = 0
            line = []
            for col_evidence in row[:17]:
                # int values
                if counter in (0, 2, 4, 10, 11, 12, 13, 14, 15, 16):
                    # month
                    if counter == 10:
                        val = (
                            0 if col_evidence == "Jan" else
                            1 if col_evidence == "Feb" else
                            2 if col_evidence == "Mar" else
                            3 if col_evidence == "Apr" else
                            4 if col_evidence == "May" else
                            5 if col_evidence == "June" else
                            6 if col_evidence == "Jul" else
                            7 if col_evidence == "Aug" else
                            8 if col_evidence == "Sep" else
                            9 if col_evidence == "Oct" else
                            10 if col_evidence == "Nov" else
                            11
                        )

                    elif counter == 15:
                        if col_evidence == "Returning_Visitor":
                            val = 1
                        else:
                            val = 0

                    elif counter == 16:
                        if col_evidence == "TRUE":
                            val = 1
                        else:
                            val = 0

                    else:
                        val = int(col_evidence)

                    line.append(val)

                # float values
                elif counter in (1, 3, 5, 6, 7, 8, 9):
                    line.append(float(col_evidence))

                counter += 1

            evidence.append(line)

            if row[17] == "TRUE":
                labels.append(1)
            else:
                labels.append(0)

    return evidence, labels


def train_model(evidence, labels):
    """
    Given a list of evidence lists and a list of labels, return a
    fitted k-nearest neighbor model (k=1) trained on the data.
    """
    model = KNeighborsClassifier(n_neighbors=1)
    model.fit(evidence, labels)
    return model


def evaluate(labels, predictions):
    """
    Given a list of actual labels and a list of predicted labels,
    return a tuple (sensitivity, specificity).

    Assume each label is either a 1 (positive) or 0 (negative).

    `sensitivity` should be a floating-point value from 0 to 1
    representing the "true positive rate": the proportion of
    actual positive labels that were accurately identified.

    `specificity` should be a floating-point value from 0 to 1
    representing the "true negative rate": the proportion of
    actual negative labels that were accurately identified.
    """

    sensitivity_true = []
    sensitivity_false = []
    specificity_true = []
    specificity_false = []

    for (actual, predicted) in zip(labels, predictions):
        if actual == 1:
            if predicted == 1:
                sensitivity_true.append(1)
            else:
                sensitivity_false.append(0)
        else:
            if predicted == 0:
                specificity_true.append(1)
            else:
                specificity_false.append(0)

    sensitivity = len(sensitivity_true) / (len(sensitivity_true) + len(sensitivity_false))
    specificity = len(specificity_true) / (len(specificity_true) + len(specificity_false))

    return sensitivity, specificity


if __name__ == "__main__":
    main()
