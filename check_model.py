import pickle

model     = pickle.load(open("models/xgb_model.pkl",     "rb"))
explainer = pickle.load(open("models/shap_explainer.pkl", "rb"))

print("Model loaded:", type(model))
print("Explainer loaded:", type(explainer))
