import numpy as np  # linear algebra
import pandas as pd  # data processing, CSV file I/O (e.g. pd.read_csv)

import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA, TruncatedSVD
import matplotlib.patches as mpatches
import time
import pickle

from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.model_selection import train_test_split
from sklearn.model_selection import StratifiedShuffleSplit


from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from imblearn.pipeline import make_pipeline as imbalanced_make_pipeline
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import NearMiss
from imblearn.metrics import classification_report_imbalanced
from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    accuracy_score,
    classification_report,
)
from collections import Counter
from sklearn.model_selection import KFold, StratifiedKFold
import warnings
import database.fetch_psql_table as fetch_psql_table

warnings.filterwarnings("ignore")

conn_string = f"host=localhost port=5432 dbname=fraud_db user=norbert password={os.getenv("DB_PASS")}"


def load_data(path):
    df = pd.read_csv(path)
    return df


def load_data_from_db():
    return fetch_psql_table.fetch_from_postgresql(
        conn_string=conn_string, table_name="transactions", limit=1000
    )


def transform_data(df):
    rob_scaler = RobustScaler()

    df["scaled_amount"] = rob_scaler.fit_transform(df["Amount"].values.reshape(-1, 1))
    df["scaled_time"] = rob_scaler.fit_transform(df["Time"].values.reshape(-1, 1))

    df.drop(["Time", "Amount"], axis=1, inplace=True)

    scaled_amount = df["scaled_amount"]
    scaled_time = df["scaled_time"]

    df.drop(["scaled_amount", "scaled_time"], axis=1, inplace=True)
    df.insert(0, "scaled_amount", scaled_amount)
    df.insert(1, "scaled_time", scaled_time)

    X = df.drop("Class", axis=1)
    y = df["Class"]

    return df, X, y


def prepare_data(df, X, y):
    """
    Bunch of preprocessing mumbo jumbo
    """
    sss = StratifiedKFold(n_splits=5, random_state=None, shuffle=False)

    for train_index, test_index in sss.split(X, y):
        print("Train:", train_index, "Test:", test_index)
        original_Xtrain, original_Xtest = X.iloc[train_index], X.iloc[test_index]
        original_ytrain, original_ytest = y.iloc[train_index], y.iloc[test_index]

    original_Xtrain = original_Xtrain.values
    original_Xtest = original_Xtest.values
    original_ytrain = original_ytrain.values
    original_ytest = original_ytest.values

    train_unique_label, train_counts_label = np.unique(
        original_ytrain, return_counts=True
    )
    test_unique_label, test_counts_label = np.unique(original_ytest, return_counts=True)

    df = df.sample(frac=1)

    fraud_df = df.loc[df["Class"] == 1]
    non_fraud_df = df.loc[df["Class"] == 0][:492]

    normal_distributed_df = pd.concat([fraud_df, non_fraud_df])

    new_df = normal_distributed_df.sample(frac=1, random_state=42)

    v14_fraud = new_df["V14"].loc[new_df["Class"] == 1].values
    q25, q75 = np.percentile(v14_fraud, 25), np.percentile(v14_fraud, 75)
    print("Quartile 25: {} | Quartile 75: {}".format(q25, q75))
    v14_iqr = q75 - q25
    print("iqr: {}".format(v14_iqr))

    v14_cut_off = v14_iqr * 1.5
    v14_lower, v14_upper = q25 - v14_cut_off, q75 + v14_cut_off
    print("Cut Off: {}".format(v14_cut_off))
    print("V14 Lower: {}".format(v14_lower))
    print("V14 Upper: {}".format(v14_upper))

    outliers = [x for x in v14_fraud if x < v14_lower or x > v14_upper]
    print("Feature V14 Outliers for Fraud Cases: {}".format(len(outliers)))
    print("V10 outliers:{}".format(outliers))

    new_df = new_df.drop(
        new_df[(new_df["V14"] > v14_upper) | (new_df["V14"] < v14_lower)].index
    )
    print("----" * 44)

    v12_fraud = new_df["V12"].loc[new_df["Class"] == 1].values
    q25, q75 = np.percentile(v12_fraud, 25), np.percentile(v12_fraud, 75)
    v12_iqr = q75 - q25

    v12_cut_off = v12_iqr * 1.5
    v12_lower, v12_upper = q25 - v12_cut_off, q75 + v12_cut_off
    print("V12 Lower: {}".format(v12_lower))
    print("V12 Upper: {}".format(v12_upper))
    outliers = [x for x in v12_fraud if x < v12_lower or x > v12_upper]
    print("V12 outliers: {}".format(outliers))
    print("Feature V12 Outliers for Fraud Cases: {}".format(len(outliers)))
    new_df = new_df.drop(
        new_df[(new_df["V12"] > v12_upper) | (new_df["V12"] < v12_lower)].index
    )
    print("Number of Instances after outliers removal: {}".format(len(new_df)))
    print("----" * 44)

    v10_fraud = new_df["V10"].loc[new_df["Class"] == 1].values
    q25, q75 = np.percentile(v10_fraud, 25), np.percentile(v10_fraud, 75)
    v10_iqr = q75 - q25

    v10_cut_off = v10_iqr * 1.5
    v10_lower, v10_upper = q25 - v10_cut_off, q75 + v10_cut_off
    print("V10 Lower: {}".format(v10_lower))
    print("V10 Upper: {}".format(v10_upper))
    outliers = [x for x in v10_fraud if x < v10_lower or x > v10_upper]
    print("V10 outliers: {}".format(outliers))
    print("Feature V10 Outliers for Fraud Cases: {}".format(len(outliers)))
    new_df = new_df.drop(
        new_df[(new_df["V10"] > v10_upper) | (new_df["V10"] < v10_lower)].index
    )
    print("Number of Instances after outliers removal: {}".format(len(new_df)))

    X = new_df.drop("Class", axis=1)
    y = new_df["Class"]

    X = new_df.drop("Class", axis=1)
    y = new_df["Class"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    X_train = X_train.values
    X_test = X_test.values
    y_train = y_train.values
    y_test = y_test.values

    return X_train, X_test, y_train, y_test


def train(X_train, X_test, y_train, y_test):
    classifiers = {
        "LogisiticRegression": LogisticRegression(),
        "KNearest": KNeighborsClassifier(),
        "Support Vector Classifier": SVC(),
        "DecisionTreeClassifier": DecisionTreeClassifier(),
    }

    for key, classifier in classifiers.items():
        classifier.fit(X_train, y_train)
        training_score = cross_val_score(classifier, X_train, y_train, cv=5)
        print(
            "Classifiers: ",
            classifier.__class__.__name__,
            "Has a training score of",
            round(training_score.mean(), 2) * 100,
            "% accuracy score",
        )

    return classifiers


def save_lr_model(classifiers):
    with open("lr_model.pkl", "wb") as f:
        pickle.dump(classifiers["LogisiticRegression"], f)

    # pred = classifiers["LogisiticRegression"].predict(X_train[15:21])
    # print(pred)


def main():
    # df = load_data("creditcard.csv")
    df = load_data_from_db()
    df, X, y = transform_data(df)
    X_train, X_test, y_train, y_test = prepare_data(df, X, y)
    classifiers = train(X_train, X_test, y_train, y_test)
    save_lr_model(classifiers)
    # save_lr_model(train(prepare_data(transform_data(load_data("creditcard.csv")))))


if __name__ == "__main__":
    main()
