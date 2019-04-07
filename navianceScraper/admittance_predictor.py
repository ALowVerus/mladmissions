from sklearn.svm import SVC
import numpy as np
from random import randint
import json
import os

prefix = os.path.dirname(os.path.realpath(__file__)) + "/"

hyper_parameter_options = {
    "C": [0.01, 0.1, 0.2, 0.5, 0.8, 1.0, 1.5, 1.8, 2.0, 2.5, 3.0, 4.0, 5.0],
    "kernel": ["linear", "poly", "rbf", "sigmoid"],
    "gamma": ["auto", "scale"],
    "degree": [1, 2, 3],
    "coef0": [0.0, 0.1, 0.2, 0.3, 1.0, 10.0],
    "shrinking": [True, False],
    "tol": [0.01, 0.001, 0.0001, 0.00001],
    "max_iter": [100, 1000, 10000, 100000]
}
lift_floor = 0.01


# Read in data
def get_data(filename, features_in_use):
    global top_file_line
    file = open(filename)
    top_file_line = file.readline()
    data = []
    for line in file:
        data_points = line.split(",")
        # Get the features as an np vector
        features = [float(x) for x in data_points[0:features_in_use]]
        # Get the label as a -1 or +1 modifier
        label = int(data_points[-1])
        data.append({"label": label, "features": features})
    file.close()
    return data


get_data("csv.csv", )

for college, scores in starting_data.items():
    college_svm = SVC()
    training_data
