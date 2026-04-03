# 🏗️ Pórtico 2D/3D & Generador de Reportes Typst

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Typst](https://img.shields.io/badge/Typst-Ready-orange)
![Pandas](https://img.shields.io/badge/Pandas-DataFrames-green)
![Matplotlib](https://img.shields.io/badge/Matplotlib-Plots-lightblue)

Este repositorio contiene un motor de cálculo matricial para el análisis sísmico de estructuras (pórticos 2D y 3D) escrito en Python, el cual está integrado de forma nativa con **PyPst**, una librería personalizada para la generación automática de reportes de ingeniería utilizando **Typst**.

## 📖 Descripción del Proyecto

Este proyecto automatiza y documenta el cálculo estructural con un enfoque programático y de alta calidad visual. Se divide en dos componentes principales que trabajan en perfecta sinergia:

1. **Motor de Análisis Estructural (Python):** Implementa el método matricial de rigidez para pórticos en 2D y 3D. Incluye capacidades avanzadas como la condensación estática de Guyan para extraer la rigidez lateral y la ejecución de un **Análisis Modal Espectral**. Soporta espectros de diseño basados en normativas como la NEC (Ecuador) y la ASCE 7-16.
2. **Generador de Reportes (PyPst + Typst):** Para eliminar la fricción entre el cálculo y la presentación de resultados, este proyecto incluye la librería local `pypst`. Esta permite transformar instantáneamente matrices, propiedades dinámicas (DataFrames de Pandas) y gráficas (Matplotlib) en documentos `.typ` estructurados mediante clases de Python, listos para compilarse a PDF.

## ✨ Características Principales

### Análisis Estructural
* **Ensamblaje Matricial:** Cálculo de matrices de rigidez local y global, y vectores de fuerzas.
* **Dinámica de Estructuras:** Condensación de GDL sin masa, cálculo de frecuencias, periodos y modos de vibración.
* **Análisis Sísmico Espectral:** Superposición modal mediante reglas SRSS y ABS. Obtención de cortantes basales, desplazamientos y fuerzas estáticas equivalentes.
* **Visualización:** Ploteo automático de la deformada elástica y diagramas de fuerzas internas (axial, cortante, momento).

### Generación de Reportes Automáticos
* **PyPst Wrapper:** Interfaz de Python para crear documentos Typst (`Document`, `Heading`, `Content`, `Table`, `Figure`, `Image`).
* **Tablas Automáticas:** Conversión directa de `pandas.DataFrame` a tablas de Typst con soporte para personalización (alineación, bordes, rellenos).
* **Gestión de Gráficos:** Inserción de gráficas de matplotlib directamente en el documento con pies de figura y numeración automática.
