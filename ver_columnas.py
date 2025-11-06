import pandas as pd

# Mortalidad
df_mortalidad = pd.read_excel('data/Anexo1.NoFetal2019_CE_15-03-23.xlsx')
print("📄 Columnas en Anexo1.NoFetal2019:")
print(df_mortalidad.columns)

# Códigos de muerte
df_codigos = pd.read_excel('data/Anexo2.CodigosDeMuerte_CE_15-03-23.xlsx')
print("\n📄 Columnas en Anexo2.CodigosDeMuerte:")
print(df_codigos.columns)

# Divipola
df_divipola = pd.read_excel('data/Divipola_CE_.xlsx')
print("\n📄 Columnas en Divipola:")
print(df_divipola.columns)
