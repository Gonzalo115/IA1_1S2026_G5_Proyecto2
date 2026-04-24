Se debe de usar Python 3.11

py -3.11 -m pip install flask flask-cors

py - -m venv venv

venv\Scripts\activate

pip install opencv-python mediapipe==0.10.9 scikit-learn joblib

```bash
pruebas/
 ├── dataset/
 │    ├── hola/
 │    │    ├── 1.jpg
 │    │    ├── 2.jpg
 │    ├── gracias/
 │    │    ├── 1.jpg
 │    │    ├── 2.jpg
 ├── dataset_generator.py
 ├── train_model.py
 ├── prueba_mediapipe.py
```

py -3.11 predict_image.py
