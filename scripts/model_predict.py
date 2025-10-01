from keras.models import load_model

def model_predict(img, model_pth):
  model = load_model(model_pth)
  predictions = model.predict(x=img)

  if predictions[0, 0] > predictions[0, 1]:
    print("Норма")
  elif predictions[0, 0] < predictions[0, 1]:
    print("Патология")
  else:
    print("Не определено")