import os
import cv2
import mediapipe as mp
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=True)

X = []
y = []

ruta_dataset = "dataset"

print("Leyendo imágenes del dataset...")

for etiqueta in os.listdir(ruta_dataset):
    ruta_etiqueta = os.path.join(ruta_dataset, etiqueta)

    if not os.path.isdir(ruta_etiqueta):
        continue

    for archivo in os.listdir(ruta_etiqueta):
        ruta_imagen = os.path.join(ruta_etiqueta, archivo)

        imagen = cv2.imread(ruta_imagen)

        if imagen is None:
            print("No se pudo leer:", ruta_imagen)
            continue

        imagen_rgb = cv2.cvtColor(imagen, cv2.COLOR_BGR2RGB)
        resultado = hands.process(imagen_rgb)

        if resultado.multi_hand_landmarks:
            mano = resultado.multi_hand_landmarks[0]

            puntos = []
            for p in mano.landmark:
                puntos.extend([p.x, p.y, p.z])

            X.append(puntos)
            y.append(etiqueta)

print("Total de muestras:", len(X))
print("Etiquetas encontradas:", set(y))

if len(X) == 0:
    print("No hay datos para entrenar.")
    exit()

if len(set(y)) < 2:
    print("Necesitas al menos 2 señas diferentes para entrenar.")
    exit()

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.3,
    random_state=42
)
modelo = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

print("Entrenando modelo...")
modelo.fit(X_train, y_train)

predicciones = modelo.predict(X_test)

accuracy = accuracy_score(y_test, predicciones)

print("Accuracy:", accuracy)
print("\nReporte de clasificación:")
print(classification_report(y_test, predicciones))

joblib.dump(modelo, "model.pkl")

print("Modelo guardado como model.pkl")