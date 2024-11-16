from sklearn.datasets import load_breast_cancer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
import xgboost as xgb
from xgboost import XGBRegressor
from skopt import BayesSearchCV
from skopt.space import Real, Integer
import pandas as pd

from sklearn.preprocessing import LabelEncoder
# Load the dataset
df = pd.read_csv('../data_preprocessing/pivoted_cancer.csv')

# Separate features and target
X = df.iloc[:, :-1]
y = df.iloc[:, -1]

state_encoder = LabelEncoder()
state_county_encoder = LabelEncoder()
X['State'] = state_encoder.fit_transform(X['State'])
X['State-County'] = state_county_encoder.fit_transform(X['State-County'])

# Split into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X,
                                                    y,
                                                    test_size=0.2,
                                                    random_state=42)

# Further split training set into training and validation sets
X_train, X_val, y_train, y_val = train_test_split(X_train,
                                                  y_train,
                                                  test_size=0.2,
                                                  random_state=42)


## PROBLEM: This code creates label encodings that are not consistent across the training, validation, and test sets.
# # Encode categorical features
# state_encoder = LabelEncoder()
# state_county_encoder = LabelEncoder()

# X_train['State'] = state_encoder.fit_transform(X_train['State'])
# X_train['State-County'] = state_county_encoder.fit_transform(
#     X_train['State-County'])

# X_val['State'] = state_encoder.transform(X_val['State'])
# X_val['State-County'] = state_county_encoder.transform(X_val['State-County'])

# X_test['State'] = state_encoder.transform(X_test['State'])
# X_test['State-County'] = state_county_encoder.transform(X_test['State-County'])

# Level 1 Parameter Search
# param_grid = {
#     'max_depth': [3, 4, 5],
#     'learning_rate': [0.1, 0.01, 0.05],
#     'n_estimators': [100, 200, 300],
#     'subsample': [0.8, 1.0],
#     'colsample_bytree': [0.8, 1.0]
# }

# # Level 2 Parameter Search
# param_grid = {
#     'max_depth': [3, 4, 5, 6, 8],  # Depth of trees; deeper trees can capture more complexity but risk overfitting
#     'learning_rate': [0.01, 0.05, 0.1, 0.2],  # Smaller values for fine updates, larger for faster convergence
#     'n_estimators': [100, 200, 300, 500],  # Number of boosting rounds
#     'subsample': [0.6, 0.8, 1.0],  # Fraction of samples used for training
#     'colsample_bytree': [0.5, 0.8, 1.0],  # Fraction of features used per tree
#     'gamma': [0, 0.1, 0.2, 0.5],  # Minimum loss reduction for a split
#     'min_child_weight': [1, 3, 5, 7],  # Minimum sum of instance weights for a leaf
#     'reg_alpha': [0, 0.01, 0.1, 1],  # L1 regularization to control sparsity
#     'reg_lambda': [1, 1.5, 2, 3],  # L2 regularization to prevent overfitting
# }

# Level 3 Parameter Search
param_grid = {
    # Booster Parameters
    "booster": [
        "gbtree", "dart"
    ],  # "gblinear" can also be included, but it's less common for most use cases.
    "tree_method": ["auto", "exact", "approx", "hist",
                    "gpu_hist"],  # Depends on data size and hardware.

    # General Parameters
    "n_estimators": [100, 200, 500, 1000],
    "learning_rate": [0.01, 0.05, 0.1, 0.2, 0.3],

    # Tree-Specific Parameters
    "max_depth": [3, 5, 7, 9, 11],
    "min_child_weight": [1, 3, 5, 7, 10],
    "gamma": [0, 0.1, 0.3, 0.5,
              1.0],  # Regularization term to avoid overfitting.
    "subsample": [0.6, 0.8, 1.0],  # Fraction of samples used to grow trees.
    "colsample_bytree": [0.6, 0.8, 1.0],  # Fraction of features used per tree.
    "colsample_bylevel": [0.6, 0.8,
                          1.0],  # Fraction of features used per level.
    "colsample_bynode": [0.6, 0.8,
                         1.0],  # Fraction of features used per split.

    # Regularization Parameters
    "lambda": [0, 1, 5, 10],  # L2 regularization term.
    "alpha": [0, 1, 5, 10],  # L1 regularization term.

    # Additional Dart-Specific Parameters
    "sample_type": ["uniform", "weighted"],  # Only for Dart.
    "normalize_type": ["tree", "forest"],  # Only for Dart.
    "rate_drop": [0.0, 0.1, 0.2,
                  0.3],  # Probability of dropping a tree in Dart.

    # Early Stopping and Optimization
    "early_stopping_rounds":
    [10, 20, 50],  # Stops training when no improvement is seen.
    "scale_pos_weight": [1, 10, 25, 50],  # Useful for imbalanced datasets.

    # Objective Function
    "objective": [
        "reg:squarederror"  # Regression
    ],

    # Evaluation Metric
    "eval_metric": [
        "rmse",
        "mae"  # Regression metrics
    ]
}

# Add num_class parameter only if the objective is multi-class classification
if "multi:softmax" in param_grid["objective"] or "multi:softprob" in param_grid["objective"]:
    param_grid["num_class"] = [len(y.unique())]

# Create XGBoost classifier
# model = XGBRegressor(objective='reg:squarederror', random_state=42, n_jobs=1, enable_categorical=True)
model = XGBRegressor(objective='reg:squarederror', random_state=42, n_jobs=1)

# Perform Bayesian optimization
bayes_search = BayesSearchCV(estimator=model,
                             search_spaces=param_grid,
                             n_iter=25,
                             cv=3,
                             n_jobs=-1,
                             verbose=2)
bayes_search.fit(X_train, y_train, eval_set=[(X_val, y_val)])  # Provide validation set here

# Print best parameters
print(f"Best parameters: {bayes_search.best_params_}")
print(f"Best score: {bayes_search.best_score_}")

best_model = bayes_search.best_estimator_
best_model.save_model("xgb_predict_cancer.xgb")

# y_pred = best_model.predict(X_test)

# mse = mean_squared_error(y_test, y_pred)
# mae = mean_absolute_error(y_test, y_pred)
# r2 = r2_score(y_test, y_pred)

# print(f"Mean Squared Error (MSE): {mse:.4f}")
# print(f"Mean Absolute Error (MAE): {mae:.4f}")
# print(f"R^2 Score: {r2:.4f}")

# # Output all metadata as a dictionary
# meta_data = {
#     "best_params": bayes_search.best_params_,
#     "best_score": bayes_search.best_score_,
#     "mse": mse,
#     "mae": mae,
#     "r2": r2
# }

# meta_data_df = pd.DataFrame([meta_data])

# # Save metadata as a CSV file
# meta_data_df.to_csv("xgb_predict_cancer.csv", index=False)
