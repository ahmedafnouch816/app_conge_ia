import pandas as pd
import pickle
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from django.conf import settings
import os

MODEL_PATH = os.path.join(settings.BASE_DIR, "workload_model.pkl")
import pickle
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import numpy as np

def load_data(filepath):
    """
    Charge les données depuis un fichier Excel et les prépare pour l'entraînement.
    """
    data = pd.read_excel(filepath)
    required_columns = ['Période_analyse', 'Annee', 'Charge_de_travail']
    
    if not all(col in data.columns for col in required_columns):
        raise ValueError(f"Le fichier Excel doit contenir les colonnes suivantes : {required_columns}")
    
    if data['Charge_de_travail'].isna().any():
        raise ValueError("La colonne 'Charge_de_travail' contient des valeurs manquantes.")
    
    months_map = {"Janvier": 1, "Février": 2, "Mars": 3, "Avril": 4, "Mai": 5, "Juin": 6, "Juillet": 7, "Août": 8, 
                  "Septembre": 9, "Octobre": 10, "Novembre": 11, "Décembre": 12}
    
    data['Période_analyse'] = data['Période_analyse'].map(months_map)
    return data

def train_and_save_model(filepath):
    """
    Entraîne le modèle et le sauvegarde dans un fichier `.pkl`.
    """
    data = load_data(filepath)
    X = data[['Annee', 'Période_analyse']]
    y = data['Charge_de_travail']

    # Diviser les données
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Entraîner le modèle
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Évaluer le modèle
    y_pred = model.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))

    # Sauvegarder le modèle
    with open('workload_model.pkl', 'wb') as f:
        pickle.dump(model, f)

    return rmse

def load_model():
    """
    Charge le modèle depuis le fichier `.pkl`.
    """
    try:
        with open('workload_model.pkl', 'rb') as f:
            model = pickle.load(f)
        return model
    except FileNotFoundError:
        raise FileNotFoundError("Le modèle n'est pas trouvé. Veuillez entraîner le modèle d'abord.")

def predict_workload(model, annee, periode):
    """
    Prédit la charge de travail pour une année et une période donnée.
    """
    prediction = model.predict([[annee, periode]])[0]
    return prediction

def get_recommendation(prediction):
    """
    Génère une recommandation basée sur la prédiction.
    """
    if prediction > 75:
        return "approuve"
    elif 50 <= prediction <= 75:
        return "en_attente"
    else:
        return "rejete" 