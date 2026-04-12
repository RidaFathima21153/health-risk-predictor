import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score
import shap

# Load data
data = pd.read_csv("data.csv")

if data['risk'].dtype == 'object':
    data['risk'] = data['risk'].map({'Low': 0, 'Medium': 1, 'High': 2})

data = data.dropna()

X = data[['age', 'bp', 'sugar', 'cholesterol']]
y = data['risk']

le = LabelEncoder()
y_encoded = le.fit_transform(y)

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(X_scaled, y_encoded, test_size=0.2, random_state=42)

models = {
    "Logistic Regression": LogisticRegression(max_iter=1000, class_weight='balanced'),
    "Random Forest": RandomForestClassifier(n_estimators=100, class_weight='balanced', random_state=42),
    "XGBoost": XGBClassifier(n_estimators=100, use_label_encoder=False, eval_metric='logloss', random_state=42)
}

model_metrics = {}

for name, clf in models.items():
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)
    
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, average='macro', zero_division=0)
    rec = recall_score(y_test, y_pred, average='macro', zero_division=0)
    
    model_metrics[name] = {
        "Accuracy": acc,
        "Precision": prec,
        "Recall": rec
    }

def predict_risk(age, bp, sugar, cholesterol, model_name="Random Forest"):
    input_scaled = scaler.transform([[age, bp, sugar, cholesterol]])
    clf = models[model_name]
    classes_encoded = list(clf.classes_)
    original_classes = le.inverse_transform(classes_encoded)
    
    if len(original_classes) == 2 and 2 in original_classes:
        idx_high = list(original_classes).index(2)
        prob_high = clf.predict_proba(input_scaled)[0][idx_high]
        
        if prob_high > 0.65:
            return "High", prob_high
        elif prob_high > 0.40:
            return "Medium", prob_high
        else:
            return "Low", prob_high
    else:
        pred_enc = clf.predict(input_scaled)[0]
        pred_orig = le.inverse_transform([pred_enc])[0]
        
        # Try finding probability if possible
        prob = clf.predict_proba(input_scaled).max()
        
        if pred_orig == 0:
            return "Low", prob
        elif pred_orig == 1:
            return "Medium", prob
        else:
            return "High", prob

def calc_bmi(weight_kg, height_cm):
    height_m = height_cm / 100
    if height_m > 0:
        return round(weight_kg / (height_m * height_m), 1)
    return 0

def calc_health_score(bmi, bp, sugar, cholesterol):
    score = 100
    if not (18.5 <= bmi <= 24.9): score -= 10
    if bmi > 30: score -= 10
    
    if bp > 120: score -= min((bp - 120) * 0.5, 20)
    if sugar > 100: score -= min((sugar - 100) * 0.5, 20)
    if cholesterol > 200: score -= min((cholesterol - 200) * 0.2, 20)
    
    return max(0, round(score))

def get_shap_values(age, bp, sugar, cholesterol, model_name="Random Forest"):
    input_scaled = scaler.transform([[age, bp, sugar, cholesterol]])
    clf = models[model_name]
    
    # Simple SHAP explainer
    if model_name in ["Random Forest", "XGBoost"]:
        explainer = shap.TreeExplainer(clf)
    else:
        explainer = shap.LinearExplainer(clf, X_train)
        
    shap_vals = explainer.shap_values(input_scaled)
    # SHAP structures differ: we'll grab the last class's array (typically positive/high)
    if isinstance(shap_vals, list):
        vals = shap_vals[-1][0]
    else:
        # If the shape is 3D (num_samples, num_features, num_classes) like some xgboost versions
        if len(np.shape(shap_vals)) == 3:
            vals = shap_vals[0, :, -1]
        else:
            vals = shap_vals[0]
            
    features = ['age', 'bp', 'sugar', 'cholesterol']
    return dict(zip(features, vals))
