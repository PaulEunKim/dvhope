#%%
import numpy as np
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from xgboost import XGBClassifier
from ray import tune
from ray.tune.search.bayesopt import BayesOptSearch

# Generate a synthetic classification dataset
X, y = make_classification(n_samples=1000,
                           n_features=10,
                           n_informative=5,
                           n_redundant=2,
                           random_state=42)
X_train, X_test, y_train, y_test = train_test_split(X,
                                                    y,
                                                    test_size=0.2,
                                                    random_state=42)


# Define the objective function
# Define the objective function
def objective(config):
    model = XGBClassifier(
        n_estimators=int(config["n_estimators"]),  # Ensure it's an integer
        max_depth=int(config["max_depth"]),  # Ensure it's an integer
        learning_rate=config["learning_rate"],
        subsample=config["subsample"],
        colsample_bytree=config["colsample_bytree"],
        random_state=42,
    )
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    tune.report(accuracy=accuracy)  # Use tune.report to report metrics


# Define the search space
config = {
    "n_estimators": tune.quniform(50, 500,
                                  1),  # Use quniform for discrete steps
    "max_depth": tune.quniform(2, 10, 1),  # Use quniform for discrete steps
    "learning_rate": tune.loguniform(1e-3, 1e-1),
    "subsample": tune.uniform(0.5, 1.0),
    "colsample_bytree": tune.uniform(0.5, 1.0),
}

# Create a Ray Tune experiment
bayesopt = BayesOptSearch(metric="accuracy", mode="max")

analysis = tune.run(
    objective,
    config=config,
    search_alg=bayesopt,
    num_samples=50,
    resources_per_trial={"cpu": 2},
)

# Get the best hyperparameters and corresponding accuracy
best_config = analysis.get_best_config(metric="accuracy", mode="max")
best_accuracy = analysis.best_result["accuracy"]

print(f"Best hyperparameters: {best_config}")
print(f"Best accuracy: {best_accuracy:.4f}")
# %%
