import json
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from imblearn.over_sampling import SMOTE
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import RandomForestClassifier


prefix = os.path.dirname(os.path.realpath(__file__)) + "/"


def process_data(data, college, knn_cons, showing_plots=True):

    data = data.drop(data[data.sat2400 <= 0].index)
    train_y = data.resultCode
    train_x = pd.DataFrame(
        data.drop(["resultCode", "act", "type", "gpaCumulative", "satConcorded"], axis=1)).reset_index(drop=True)

    print("Before OverSampling, counts of label '1': {}".format(sum(train_y == True)))
    print("Before OverSampling, counts of label '0': {} \n".format(sum(train_y == False)))

    sm = SMOTE(random_state=2, k_neighbors=knn_cons)
    x_train_smote, y_train_smote = sm.fit_sample(train_x, train_y.ravel())

    print('After OverSampling, the shape of train_X: {}'.format(x_train_smote.shape))
    print('After OverSampling, the shape of train_y: {} \n'.format(y_train_smote.shape))

    print("After OverSampling, counts of label '1': {}".format(sum(y_train_smote == True)))
    print("After OverSampling, counts of label '0': {}".format(sum(y_train_smote == False)))

    x_train_smote = pd.DataFrame(x_train_smote)
    x_train_smote.columns = ['sats', 'gpa']

    fig = plt.figure(figsize=(10, 10))
    for i, tar in enumerate(np.unique(y_train_smote)):
        Xi = x_train_smote[y_train_smote == tar]
        plt.scatter(Xi.iloc[:, 0], Xi.iloc[:, 1], label=tar)
    plt.xlabel('Sat Score')
    plt.ylabel('GPA')
    plt.title(college.upper())
    plt.legend()
    if showing_plots:
        plt.show()

    return x_train_smote, y_train_smote


def main_admittance_predictor():
    showing_plots = False

    # Convert data into CSV format for management
    with open(prefix + "admissions_info_dict.json", "r") as fp:
        admissions_info_dict = json.load(fp)
        fp.close()
    college_specific_data = {}
    for college, scores in admissions_info_dict.items():
        ivs = ["type", "act", "sat2400", "gpaWeighted", "gpaCumulative", "satConcorded"]
        dvs = ["resultCode"]
        with open(prefix + "csv.csv", "w") as fp:
            for iv in ivs:
                fp.write(iv + ",")
            for dv in dvs:
                fp.write(dv)
            fp.write("\n")
            for score in scores:
                for iv in ivs:
                    fp.write(str(score[iv]) + ",")
                for dv in dvs:
                    fp.write(str(score[dv]))
                fp.write("\n")
            fp.close()
        college_specific_data[college] = {}
        college_specific_data[college]["entries"] = pd.read_csv(prefix + "csv.csv")
    os.remove(prefix + "csv.csv")

    print(college_specific_data["Harvard College"]["entries"].head())

    # Relabel dataset
    for college_data in college_specific_data.values():
        college_data["entries"]['resultCode'] = college_data["entries"]['resultCode'].apply(lambda x: False if x == 2 else True)

    # Plot out dataset
    college_list = list(college_specific_data.keys())
    f = plt.figure(figsize=(15, 15))
    for i in range(min(len(college_list), 6)):
        college = college_list[i]
        entries = college_specific_data[college]["entries"]
        f.add_subplot(i + 321)
        entries['resultCode'].value_counts().plot(kind='bar', title=college)
    if showing_plots:
        plt.show()

    # Define constants
    college_constants = {
        'Dartmouth College': {"knn_constant": 4, "model": "random_forest"},
        'Princeton University': {"knn_constant": 1, "model": "gaussian_nb"},
        'Northeastern University': {"knn_constant": 1, "model": "gaussian_nb"},
        'Columbia University': {"knn_constant": 5, "model": "random_forest"},
        # 'Harvard College': {"knn_constant": 5, "model": "qda_predict"},
    }

    # Up-sample your data
    for college in list(college_constants.keys()):
        data = college_specific_data[college]
        print("\nTraining with " + college + ".\n")
        knn_cons = college_constants[college]["knn_constant"]
        x_college, y_college = process_data(data["entries"], college, knn_cons, showing_plots=showing_plots)
        college_specific_data[college]["xy"] = (x_college, y_college)

    # Analyze for probabilities of getting in
    made_models = {}
    for college in list(college_constants.keys()):
        print("Predicting for " + college + ".")
        x_college, y_college = college_specific_data[college]["xy"]
        optimal_model_type = college_constants[college]["model"]
        if optimal_model_type == "random_forest":
            model = RandomForestClassifier(n_estimators=10, max_depth=3, random_state=0).fit(x_college, y_college)
        elif optimal_model_type == "qda_predict":
            model = QuadraticDiscriminantAnalysis().fit(x_college, y_college)
        elif optimal_model_type == "gaussian_nb":
            model = GaussianNB().fit(x_college, y_college)
        else:
            exit()
        print(model.predict_proba([[1600, 4.0]]))
        made_models[college] = model

    return made_models


if __name__ == '__main__':
    main_admittance_predictor()
