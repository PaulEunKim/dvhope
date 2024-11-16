import numpy as np
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import StackingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score
import matplotlib.pyplot as plt

# Generate a synthetic dataset
X, y = make_classification(n_samples=1000, n_classes=2, n_features=20, n_informative=10, random_state=42)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Define base models
rf = RandomForestClassifier(n_estimators=100, random_state=42)
lr = LogisticRegression()
knn = KNeighborsClassifier(n_neighbors=5)

# Define the stacking ensemble
base_models = [('rf', rf), ('lr', lr), ('knn', knn)]
xgb = XGBClassifier(n_estimators=100, learning_rate=0.01, random_state=42)
stacking_ensemble = StackingClassifier(estimators=base_models, final_estimator=xgb)

# Train and evaluate the stacking ensemble
stacking_ensemble.fit(X_train, y_train)
y_pred_stacking = stacking_ensemble.predict(X_test)
accuracy_stacking = accuracy_score(y_test, y_pred_stacking)

# Train and evaluate individual models
rf.fit(X_train, y_train)
y_pred_rf = rf.predict(X_test)
accuracy_rf = accuracy_score(y_test, y_pred_rf)

lr.fit(X_train, y_train)
y_pred_lr = lr.predict(X_test)
accuracy_lr = accuracy_score(y_test, y_pred_lr)

knn.fit(X_train, y_train)
y_pred_knn = knn.predict(X_test)
accuracy_knn = accuracy_score(y_test, y_pred_knn)

# Visualize the performance comparison
models = ['Random Forest', 'LR', 'KNN', 'Stacking Ensemble']
accuracies = [accuracy_rf, accuracy_lr, accuracy_knn, accuracy_stacking]

plt.figure(figsize=(8, 6))
plt.bar(models, accuracies)
plt.title('Model Performance Comparison')
plt.xlabel('Model')
plt.ylabel('Accuracy')
plt.ylim(0.8, 1.0)
plt.show()