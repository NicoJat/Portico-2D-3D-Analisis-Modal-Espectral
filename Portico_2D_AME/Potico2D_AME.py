import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.linalg import eigh
import Funciones_sismos as BN
from nodo import Nodo
from elemento import Elemento
from estructura import Estructura
from IPython import display

# 1. Definir propiedades geométricas y mecánicas
E = 1900000  # Módulo de elasticidad (T/m^2)

# Sección de columnas (0.30 x 0.30 m)
A_col = 0.30 * 0.30 
I_col = (0.30 * 0.30**3) / 12 

# Sección de viga (0.30 x 0.40 m)
A_viga = 0.30 * 0.40 
I_viga = (0.30 * 0.40**3) / 12 

# 2. Crear los Nodos (id, x, y, restr_x, restr_y, restr_giro)
# Base del pórtico (Empotramientos)
n1 = Nodo(1, 0, 0, rx=True, ry=True, rm=True)
n2 = Nodo(2, 5, 0, rx=True, ry=True, rm=True)

# Techo del pórtico (Nodos libres)
n3 = Nodo(3, 0, 3, rx=False, ry=False, rm=False)
n4 = Nodo(4, 5, 3, rx=False, ry=False, rm=False)

# Asignamos la masa traslacional principal en X, una pequeña en Y, y el valor ínfimo en la rotación
n3.set_mass(mx=10, my=0, mrot=0)
n4.set_mass(mx=10, my=0, mrot=0)

# 3. Crear los Elementos (id, nodo_i, nodo_j, A, I, E)
col1 = Elemento(1, n1, n3, A_col, I_col, E)
col2 = Elemento(2, n2, n4, A_col, I_col, E)
viga = Elemento(3, n3, n4, A_viga, I_viga, E)

# 4. Ensamblar la Estructura
portico = Estructura()
for n in [n1, n2, n3, n4]:
    portico.ag_nodos(n)
for el in [col1, col2, viga]:
    portico.ag_elementos(el)

# TRUCO: Tu método original resolver() enumera los GDL y ensambla la matriz de rigidez S. 
# Lo llamamos primero sin cargas para que prepare la matriz S.
portico.resolver() 
portico.gdls_totales = len(portico.P) # Guardamos la cantidad de GDLs libres

###### Espectro de respuesta ########
zona = 5
suelo = 'C'
fip = 1
fie = 0.8
fa = 1.2
fd = 1.11
fs = 1.11
n = 2.6
z = 0.6     #Para un TR475 años
Imp = 1   #Importancia
rr = 1
R = 5.5


Spec, SpecI, Tmp, To, Tc, Tl = BN.Spec_NEC(n, z, fa, fd, fs, rr, Imp, R, fip, fie, 2.5)
# display(pd.DataFrame(SpecI).style.set_caption('Sa_Espectro Inelastico'))
# fig, ax = plt.subplots()
# plt.plot(Tmp, Spec[:,1], label='Espectro Elastico')
# plt.plot(Tmp, SpecI[:,1], label='Espectro Inelastico')
# ax.axhline(0, color='black', linewidth=0.7)
# ax.axvline(0, color='black', linewidth=0.7)
# ax.set_xlabel('Periodos T')
# ax.set_ylabel('Sa en función de g')
# plt.legend()
# plt.show()

#####################################

# Ejecutamos el análisis
resultados = portico.analisis_modal_espectral(SpecI)

# Escala 1.0 para ver el desplazamiento a escala real (suele ser pequeño) o 10.0 para exagerarlo
portico.graficar_resultados(
    tipo='deformada', 
    escala=5.0, 
    vector_d=resultados["qmax"][:, 0], # Índice 0 = Modo 1
    titulo_custom="Desplazamientos Máximos Esperados - Modo Fundamental"
)

# Usamos la matriz de autovectores 'Modos'. Aquí la escala suele ser grande porque los autovectores están normalizados a la masa.
portico.graficar_resultados(
    tipo='deformada', 
    escala=1.0, 
    vector_d=resultados["Modos"][:, 0], # Índice 1 = Modo 2
    titulo_custom="Forma Modal 2 (Curvatura relativa)"
)

# 7. Mostrar Resultados explícitamente en el script
print("\n--- MATRICES GLOBALES ---")
display(pd.DataFrame(resultados["K"]).style.set_caption('Matriz de Rigidez Global (K)'))
display(pd.DataFrame(resultados["M"]).style.set_caption('Matriz de Masas (M)'))

print("\n--- PROPIEDADES DINÁMICAS ---")
display(pd.DataFrame({'w (rad/s)': resultados["w"], 'T (s)': resultados["Periodos"], 'V (w^2)': resultados["V"]}).style.set_caption('Frecuencias y Periodos'))
display(pd.DataFrame(resultados["Modos"]).style.set_caption('Matriz de Modos de Vibración (phi)'))

print("\n--- PARTICIPACIÓN MODAL ---")
display(pd.DataFrame(resultados["Lw"], columns=["Lw"]).style.set_caption('Factores de Participación (Lw)'))
display(pd.DataFrame({'Masa Efectiva (%)': resultados["Masa_Efectiva"], 'Acumulada (%)': np.cumsum(resultados["Masa_Efectiva"])}).style.set_caption('Participación de Masa'))

print("\n--- RESPUESTAS MÁXIMAS ---")
display(pd.DataFrame(resultados["qmax"]).style.set_caption('Desplazamientos Máximos Modales (qmax)'))
display(pd.DataFrame(resultados["Qmax"]).style.set_caption('Fuerzas Estáticas Equivalentes (Qmax)'))

print("\n--- SUPERPOSICIÓN MODAL ---")
display(pd.DataFrame(resultados["SRSS"], columns=["Fuerzas SRSS"]).style.set_caption('Fuerzas Combinadas (SRSS)'))



from pypst.document import Document
from pypst.heading import Heading
from pypst.content import Content
from pypst.table import Table
from pypst.image import Image
from pypst.figure import Figure


# ==========================================
# 3. GENERACIÓN DEL DOCUMENTO TYPST
# ==========================================
doc = Document() #
doc.add(Heading("Reporte de Análisis Modal Espectral 2D", level=1)) #

# --- Propiedades ---
doc.add(Heading("1. Propiedades del Pórtico", level=2))
doc.add(Content(
    f"Se analizó un pórtico 2D con un módulo de elasticidad $E = {E}$ T/m². "
    f"Las columnas tienen un área $A = {A_col:.4f}$ m² y una inercia $I = {I_col:.6f}$ m⁴. "
    f"La viga presenta un área $A = {A_viga:.4f}$ m² y una inercia $I = {I_viga:.6f}$ m⁴."
)) #

# --- Matrices Condensadas ---
doc.add(Heading("2. Matrices Globales Condensadas", level=2))
doc.add(Content("Matriz de Rigidez Lateral ($K $):"))
doc.add(Table.from_dataframe(pd.DataFrame(np.round(resultados["K"], 2)))) #

doc.add(Content("Matriz de Masas ($M $):"))
doc.add(Table.from_dataframe(pd.DataFrame(np.round(resultados["M"], 2))))

# --- Propiedades Dinámicas ---
doc.add(Heading("3. Propiedades Dinámicas", level=2))
df_dinamicas = pd.DataFrame({
    'Modo': range(1, len(resultados["w"])+1),
    'w (rad/s)': np.round(resultados["w"], 4),
    'V (w^2)': np.round(resultados["V"], 4),
    'T (s)': np.round(resultados["Periodos"], 4)
}).set_index('Modo')
doc.add(Table.from_dataframe(df_dinamicas))

doc.add(Heading("3.1 Modos de Vibración Expandidos ($phi$)", level=3))
df_modos = pd.DataFrame(np.round(resultados["Modos"], 4))
doc.add(Table.from_dataframe(df_modos))

# --- Participación Modal ---
doc.add(Heading("4. Participación Modal", level=2))
df_participacion = pd.DataFrame({
    'Modo': range(1, len(resultados["Lw"])+1),
    'Lw': np.round(resultados["Lw"], 4),
    'Masa Efectiva (%)': np.round(resultados["Masa_Efectiva"], 2),
    'Acumulada (%)': np.round(np.cumsum(resultados["Masa_Efectiva"]), 2)
}).set_index('Modo')
doc.add(Table.from_dataframe(df_participacion))

# --- Respuestas Máximas ---
doc.add(Heading("5. Respuestas Máximas y Superposición", level=2))
doc.add(Heading("5.1 Desplazamientos Modales Máximos ($q_{max}$)", level=3))
doc.add(Table.from_dataframe(pd.DataFrame(np.round(resultados["qmax"], 6))))

doc.add(Heading("5.2 Fuerzas Estáticas Equivalentes ($Q_{max}$)", level=3))
doc.add(Table.from_dataframe(pd.DataFrame(np.round(resultados["Qmax"], 4))))

doc.add(Heading("5.3 Fuerzas Combinadas (Regla SRSS)", level=3))
df_srss = pd.DataFrame(np.round(resultados["SRSS"], 4), columns=["Fuerzas SRSS"])
doc.add(Table.from_dataframe(df_srss))

# --- Gráficas ---
doc.add(Heading("6. Visualización de la Deformada", level=2))

img_modo1 = Image(path="modo_fundamental_2d.png", width="75%") #
fig_modo1 = Figure(body=img_modo1, caption="[Desplazamientos máximos esperados del Modo Fundamental.]" ) #
doc.add(fig_modo1)

img_modo2 = Image(path="forma_modal_2_2d.png", width="75%")
fig_modo2 = Figure(body=img_modo2, caption="[Forma Modal 2 (Curvatura relativa).]" )
doc.add(fig_modo2)

# ==========================================
# 4. EXPORTAR REPORTE TYPST
# ==========================================
with open("reporte_portico_2d.typ", "w", encoding="utf-8") as f:
    f.write(doc.render())
    
print("¡Reporte 2D generado con éxito en 'reporte_portico_2d.typ'!")
print("Imágenes generadas: 'modo_fundamental_2d.png' y 'forma_modal_2_2d.png'")
