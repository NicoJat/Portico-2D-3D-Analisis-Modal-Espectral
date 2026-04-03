import numpy as np
import pandas as pd
from nodo import Nodo
from elemento import Elemento
from estructura import Estructura
import Funciones_sismos as BN
from IPython import display

# ==========================================
# SCRIPT DE EJECUCIÓN
# ==========================================
b, h = 0.15, 0.20  # Base y Altura
A = b * h
Iy, Iz = (b * h**3)/12, (h * b**3)/12  # Inercias
J = (b**3 * h)/3 * (1 - 0.63*(min(b,h)/max(b,h))) if b != h else 0.141*b**4 # Torsión aprox.
Asy = Asz = A * 0.833  # Área cortante efectiva (factor 5/6)
print(f"Sección {b}x{h}m -> A={A:.4f}, Iy={Iy:.6f}, Iz={Iz:.6f}")

E, G = 200e6, 80e6  # Materiales

modelo = Estructura()

# Geometría Z-Vertical (Planta en X-Y, altura en Z)
n1 = Nodo(1, 0, 0, 0, rx=True, ry=True, rz=True, rmx=True, rmy=True, rmz=True)
n2 = Nodo(2, 0, 6, 0, rx=True, ry=True, rz=True, rmx=True, rmy=True, rmz=True)
n3 = Nodo(3, 6, 6, 0, rx=True, ry=True, rz=True, rmx=True, rmy=True, rmz=True)
n4 = Nodo(4, 6, 0, 0, rx=True, ry=True, rz=True, rmx=True, rmy=True, rmz=True)

n5 = Nodo(5, 0, 0, 6)
n6 = Nodo(6, 0, 6, 6)
n7 = Nodo(7, 6, 6, 6)
n8 = Nodo(8, 6, 0, 6)

for n in [n1, n2, n3, n4, n5, n6, n7, n8]: 
    modelo.ag_nodos(n)

for n in [n5, n6, n7, n8]: 
    n.set_mass(mx=20, my=20, mz=0, mrx=0, mry=0, mrz=0)



col1 = Elemento(1, n1, n5, A, Iz, Iy, J, E, G, Asy=Asy, Asz=Asz, cortante=True)
col2 = Elemento(2, n2, n6, A, Iz, Iy, J, E, G, Asy=Asy, Asz=Asz, cortante=True)
col3 = Elemento(3, n3, n7, A, Iz, Iy, J, E, G, Asy=Asy, Asz=Asz, cortante=True)
col4 = Elemento(4, n4, n8, A, Iz, Iy, J, E, G, Asy=Asy, Asz=Asz, cortante=True)

vig1 = Elemento(5, n5, n8, A, Iz, Iy, J, E, G, Asy=Asy, Asz=Asz, cortante=True)
vig2 = Elemento(6, n6, n7, A, Iz, Iy, J, E, G, Asy=Asy, Asz=Asz, cortante=True)  
vig3 = Elemento(7, n5, n6, A, Iz, Iy, J, E, G, Asy=Asy, Asz=Asz, cortante=True)
vig4 = Elemento(8, n7, n8, A, Iz, Iy, J, E, G, Asy=Asy, Asz=Asz, cortante=True)  

for el in [col1, col2, col3, col4, vig1, vig2, vig3, vig4]: 
    modelo.ag_elementos(el)
    
modelo.resolver()
d_original = modelo.d.copy() 

zona = 5; suelo = 'C'; fip = 1; fie = 0.8; fa = 1.2; fd = 1.11; fs = 1.11
n_nec = 2.6; z_nec = 0.6; Imp = 1; rr = 1; R = 5.5
Spec, SpecI, Tmp, To, Tc, Tl = BN.Spec_NEC(n_nec, z_nec, fa, fd, fs, rr, Imp, R, fip, fie, 2.5)

resultados = modelo.analisis_modal_espectral(SpecI, SpecI)
res_X = resultados['X']
res_Y = resultados['Y']

modelo.d = res_X["qmax"][:, 0].reshape(-1, 1)
modelo.graficar_deformada(escala=5.0)
modelo.d = res_X["Modos"][:, 1].reshape(-1, 1)
modelo.graficar_deformada(escala=1.0)
modelo.d = d_original


# ==========================================
# 8. IMPRESIÓN DE RESULTADOS (X e Y)
# ==========================================
print("Períodos modales Python:", resultados['Y']['Periodos'][:3])
print("\n--- MATRICES GLOBALES ---")
display(pd.DataFrame(modelo.S).style.set_caption('Matriz de Rigidez Global (S)'))
display(pd.DataFrame(modelo.M).style.set_caption('Matriz de Masas (M)'))

print("\n--- PROPIEDADES DINÁMICAS (Comunes a X e Y) ---")
w = res_X["Frecuencias_w"]
V = w**2 
df_dinamicas = pd.DataFrame({'w (rad/s)': w, 'V (w^2)': V, 'T (s)': res_X["Periodos"]})
display(df_dinamicas.style.set_caption('Frecuencias y Periodos'))
display(pd.DataFrame(res_X["Modos"]).style.set_caption('Matriz de Modos de Vibración (phi)'))

# --- RESULTADOS DIRECCIÓN X ---
print("\n" + "="*50)
print("           RESULTADOS DIRECCIÓN X")
print("="*50)
print("\n--- PARTICIPACIÓN MODAL X ---")
display(pd.DataFrame(res_X["Lw"], columns=["Lw_X"]).style.set_caption('Factores de Participación X'))
display(pd.DataFrame({'Masa Efectiva X (%)': res_X["Masa_Efectiva"], 'Acumulada X (%)': np.cumsum(res_X["Masa_Efectiva"])}).style.set_caption('Participación de Masa X'))

print("\n--- RESPUESTAS MÁXIMAS X ---")
display(pd.DataFrame(res_X["qmax"]).style.set_caption('Desplazamientos Modales Máximos X (qmax)'))
display(pd.DataFrame(res_X["Qmax"]).style.set_caption('Fuerzas Estáticas Equivalentes X (Qmax)'))

print("\n--- SUPERPOSICIÓN MODAL X ---")
display(pd.DataFrame(res_X["SRSS"], columns=["Fuerzas SRSS X"]).style.set_caption('Fuerzas Combinadas X (SRSS)'))

# --- RESULTADOS DIRECCIÓN Y ---
print("\n" + "="*50)
print("           RESULTADOS DIRECCIÓN Y")
print("="*50)
print("\n--- PARTICIPACIÓN MODAL Y ---")
display(pd.DataFrame(res_Y["Lw"], columns=["Lw_Y"]).style.set_caption('Factores de Participación Y'))
display(pd.DataFrame({'Masa Efectiva Y (%)': res_Y["Masa_Efectiva"], 'Acumulada Y (%)': np.cumsum(res_Y["Masa_Efectiva"])}).style.set_caption('Participación de Masa Y'))

print("\n--- RESPUESTAS MÁXIMAS Y ---")
display(pd.DataFrame(res_Y["qmax"]).style.set_caption('Desplazamientos Modales Máximos Y (qmax)'))
display(pd.DataFrame(res_Y["Qmax"]).style.set_caption('Fuerzas Estáticas Equivalentes Y (Qmax)'))

print("\n--- SUPERPOSICIÓN MODAL Y ---")
display(pd.DataFrame(res_Y["SRSS"], columns=["Fuerzas SRSS Y"]).style.set_caption('Fuerzas Combinadas Y (SRSS)'))



from pypst.document import Document
from pypst.heading import Heading
from pypst.content import Content
from pypst.table import Table
from pypst.image import Image
from pypst.figure import Figure

doc = Document()

# Título principal
doc.add(Heading("Reporte de Análisis Modal Espectral 3D", level=1))

# Sección 1: Propiedades
doc.add(Heading("1. Propiedades de la Sección y Materiales", level=2))
propiedades = (
    f"Se analizó un pórtico 3D con columnas y vigas de sección rectangular de base $b = {b}$ m y altura $h = {h}$ m."
    
    f"Las propiedades calculadas son: Área $A = {A:.4f}$ m², Inercia local en z $I_z = {Iz:.6f}$ m⁴, "
    
    f"Inercia local en y $I_y = {Iy:.6f}$ m⁴, y Constante torsional $J = {J:.6f}$ m⁴. "
    
    f"Los módulos de elasticidad utilizados son $E = {E}$ Pa y $G = {G}$ Pa."
)
doc.add(Content(propiedades))

# Sección 2: Propiedades Dinámicas
doc.add(Heading("2. Propiedades Dinámicas", level=2))
doc.add(Content("La condensación estática extrae los GDL con masa significativa. A continuación, los periodos y frecuencias naturales del sistema:"))

w = res_X["Frecuencias_w"]
V = w**2 
df_dinamicas = pd.DataFrame({'Modo': range(1, len(w)+1), 'w (rad/s)': np.round(w, 4), 'V (w^2)': np.round(V, 4), 'T (s)': np.round(res_X["Periodos"], 4)})
df_dinamicas.set_index('Modo', inplace=True)

tabla_dinamica = Table.from_dataframe(df_dinamicas)
tabla_dinamica.align = "center"
doc.add(tabla_dinamica)

# Sección 3: Resultados Sismo X
doc.add(Heading("3. Resultados Dirección X", level=2))

doc.add(Heading("3.1 Participación de Masa X", level=3))
df_masa_x = pd.DataFrame({
    'Modo': range(1, len(w)+1),
    'Lw_X': np.round(res_X["Lw"], 4),
    'Masa Efectiva X (%)': np.round(res_X["Masa_Efectiva"], 2),
    'Acumulada X (%)': np.round(np.cumsum(res_X["Masa_Efectiva"]), 2)
}).set_index('Modo')
doc.add(Table.from_dataframe(df_masa_x))

doc.add(Heading("3.2 Respuestas Máximas Modales X", level=3))
doc.add(Content("Desplazamientos modales máximos ($q_{max}$):"))
df_qmax_x = pd.DataFrame(np.round(res_X["qmax"], 4))
doc.add(Table.from_dataframe(df_qmax_x))

doc.add(Heading("3.3 Fuerzas Combinadas (SRSS) X", level=3))
doc.add(Content("Fuerzas estáticas equivalentes combinadas mediante la regla SRSS:"))
df_srss_x = pd.DataFrame(np.round(res_X["SRSS"], 2), columns=["Fuerzas SRSS X"])
doc.add(Table.from_dataframe(df_srss_x))

# Sección 4: Resultados Sismo Y
doc.add(Heading("4. Resultados Dirección Y", level=2))

doc.add(Heading("4.1 Participación de Masa Y", level=3))
df_masa_y = pd.DataFrame({
    'Modo': range(1, len(w)+1),
    'Lw_Y': np.round(res_Y["Lw"], 4),
    'Masa Efectiva Y (%)': np.round(res_Y["Masa_Efectiva"], 2),
    'Acumulada Y (%)': np.round(np.cumsum(res_Y["Masa_Efectiva"]), 2)
}).set_index('Modo')
doc.add(Table.from_dataframe(df_masa_y))

doc.add(Heading("4.2 Respuestas Máximas Modales Y", level=3))
doc.add(Content("Desplazamientos modales máximos ($q_{max}$):"))
df_qmax_y = pd.DataFrame(np.round(res_Y["qmax"], 4))
doc.add(Table.from_dataframe(df_qmax_y))

doc.add(Heading("4.3 Fuerzas Combinadas (SRSS) Y", level=3))
df_srss_y = pd.DataFrame(np.round(res_Y["SRSS"], 2), columns=["Fuerzas SRSS Y"])

doc.add(Table.from_dataframe(df_srss_y))

# Añadir el Diagrama de Momentos
img_mom = Image(path="momentos.png", width="80%")
fig_mom = Figure(
    body=img_mom, 
    caption="[Diagrama de Momentos Flectores ($M_z$) en el plano local x-y.]"
)
doc.add(fig_mom)

# ==========================================
# 3. EXPORTAR CÓDIGO
# ==========================================
codigo_typst = doc.render()

with open("reporte_estructural.typ", "w", encoding="utf-8") as f:
    f.write(codigo_typst)
    
print("¡Reporte generado con éxito en 'reporte_estructural.typ'!")