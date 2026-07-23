import os
caminho = os.path.abspath("inteligencia_macro.db")
print(caminho)
print("Existe?", os.path.exists(caminho))