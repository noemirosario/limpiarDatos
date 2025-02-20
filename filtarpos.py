import pandas as pd

# Ruta del archivo de entrada (modifícala según sea necesario)
ruta_entrada = r"C:\Users\Juan\Downloads\unido.xlsx"
# Ruta del archivo de salida
ruta_salida = r"C:\Users\Juan\Downloads\totalps.xlsx"

# Lista de subdivisiones a filtrar
subdivisiones = [
    "Asimilados Extr","Cd Canales Espe","Cedis Ecommerce","CEDIS Guadalaja","Cedis León 2","Cedis Tultitlan","Credito Cobranz","Diseño e Imag 1","Dulcería Veracr","Grupo SJ","Honorarios","Importaciones","Mantenimiento","Prev Perdidas 2","Prev. Perdidas","Price Center  1","Servicios Admit","TC Cárdenas","TC Chihuahua","TC Coatzacoalco","TC Córdoba","TC Mérida 2","TC San Andres","TC Tampico","TC Tapachula","TC Texmelucan","TC Tuxpan","TC Tuxtla","TC Xalapa","TCP Celaya 2","TCP Chalco","TCP Guadalajara","TCP Medrano","TCP Nicolas Rom","TCP Puebla","TCP Queret Cen","TCP Tecate","TCP Tehuacan","TCP Toluca Cent","Tienda  Miraval","Tienda Aguascal","Tienda Arco Nor","Tienda Centro","Tienda Ecatepec","Tienda Guadalaj","Tienda Ixtapalu","Tienda Iztapala","Tienda León 2","Tienda Naucalpa","Tienda Puebla","Tienda Queretar","Tienda Tijuana","Tienda Toluca","Tienda Vallejo","Tienda Veracruz","Tnda Olivar Con"

]

# Columnas a incluir en el archivo final
columnas_a_incluir = [
    "Jefe", "Nº pers", "fecha ing", "Número de personal", "Soc", "Sociedad", "Div",
    "División de personal", "Subdivisión de", "Grupo de personal",
    "Área de personal", "Área de nómina", "Ce.coste", "Centro de coste", " Un.org.",
    "Unidad organizativa", "Posición", "Posición.1", "U.Org.Superior"
]

# Cargar el archivo de Excel
df = pd.read_excel(ruta_entrada, dtype=str)  # Cargar todos los datos como texto para evitar problemas de formato

# Filtrar solo las columnas requeridas
df = df[columnas_a_incluir]

# Crear un escritor de Excel para almacenar los datos filtrados
writer = pd.ExcelWriter(ruta_salida, engine='xlsxwriter')

# Lista para almacenar el resumen de posiciones por subdivisión
resumen_data = []

for subdivision in subdivisiones:
    df_filtrado = df[df["Subdivisión de"] == subdivision]  # Filtrar por subdivisión
    if not df_filtrado.empty:
        total_registros = len(df_filtrado)
        activas = df_filtrado[df_filtrado["Nº pers"].notna() & (df_filtrado["Nº pers"] != "0")].shape[0]
        vacantes = total_registros - activas

        # Agregar al resumen
        resumen_data.append([subdivision, total_registros, activas, vacantes])

        # Agregar la columna con el total de registros
        df_filtrado["Total de Registros"] = total_registros
        df_filtrado.to_excel(writer, sheet_name=subdivision[:31], index=False)  # Guardar en hoja de Excel

# Crear DataFrame con el resumen y guardarlo en una nueva hoja
resumen_df = pd.DataFrame(resumen_data, columns=["Subdivisión de", "Total Posiciones", "Activas", "Vacantes"])
resumen_df.to_excel(writer, sheet_name="Resumen", index=False)

# Guardar el archivo de salida
writer.close()

print(f"Archivo guardado en: {ruta_salida}")
