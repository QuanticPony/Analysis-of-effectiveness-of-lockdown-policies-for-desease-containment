<h1 style="text-align: center;"> Trabajo Fin de Grado de Física </h1>
<br/><br/>

<img 
    style="display: block; 
           margin-left: auto;
           margin-right: auto;
           width: 60%;"
    src="https://external-content.duckduckgo.com/iu/?u=http%3A%2F%2Fwzar.unizar.es%2Fperso%2Fiarenillas%2Fimg%2Flogo_ciencias.jpg&f=1&nofb=1" 
    alt="Our logo">
</img>
<br/><br/>

_______

<h2 style="text-align: center;">
Análisis de efectividad de la contención epidémica por confinamiento</h2>
<h2 style="text-align: center;"> Analysis of effectiveness of lockdown policies for desease containment </h2>

_________
<br/><br/>


<p style="text-align: center;">Autor</p>

<h2 style="text-align: center;">
Unai Lería Fortea</h2>

<p style="text-align: center;">Directores</p>

<h2 style="text-align: center;">
Jesús Gómez Gardeñes</h2>
<h2 style="text-align: center;">
David Soriano Paños</h2>

<br/><br/>

<h3 style="text-align: center;">
DEPARTAMENTO DE FÍSICA DE LA MATERIA CONDENSADA</h3>
<h3 style="text-align: center;">
2022</h3>
<br/><br/>

# Resumen

> Nuestro objetivo en este trabajo es ofrecer un modelo epidemiológico simple que
tenga en cuenta las políticas de restricción de movilidad, que permita emular las
evoluciones de epidemias reales y que ofrezca información sobre la importancia de estas
medidas. Mostraremos la relevancia de la determinación del número de reproducción
básico $R_0$ al comienzo de epidemias para obtener información de la expansión de la
enfermedad y lo evaluaremos en nuestro modelo. Simularemos epidemias para estudiar
los efectos de implementaciones precoces/tardías de las restricciones y el efecto de la
permeabilidad de estas medidas. Para crear el modelo epidemiológico aprovecharemos
las herramientas de modelos compartimentales en su aproximaci ón de campo medio.

>Finalmente, haremos uso de un m ́etodo de inferencia bayesiana relatívamente nuevo,
*Approximate Bayesian Computation* (ABC), para ajustar los parámetros del modelo a
datos reales de múltiples países. Con este análisis perseguimos el objetivo de observar
si existe una correlación entre la permeabilidad de las medidas restrictivas con algún
parámetro socio-económico que refleje la riqueza de la población de cada país.

<br/><br/>

# Memoria

https://deposita.unizar.es/record/69350?ln=es

<br/><br/>

# Requisitos
*   [numpy](https://numpy.org/)
*   [cupy](https://cupy.dev/) así como una tarjeta gráfica compatible
*   [pandas](https://pandas.pydata.org/)
*   [geopandas](https://geopandas.org/en/stable/)
*   [matplotlib](https://matplotlib.org/)
*   [scipy](https://scipy.org/)
*   [SciencePlots](https://github.com/garrettj403/SciencePlots) es el estilo principal usado en los gráficos. No es imprescindible

<br/><br/>

# Archivos
## [launcher.py](launcher.py)
Archivo principal para ejecutar el código.

## [configuration_managment.ipynb](configuration_managment.ipynb)
Archivo encargado de generar las configuraciones y preparar las simulaciones.

## [model/](model/)
Carpeta dedicada a los archivos con nuestro modelo.

## [model_seir/](model_seir/)
Carpeta dedicada a los archivos con el modelo SEIR. Durante el trabajo solo es usada para las demostraciones del método *Approximate Bayesian Computation* ABC.

<br/><br/>

# Agradecimientos
El estilo de las figuras ha sido fuertemente influenciado e inspirado por el libro [*"Scientific Visualization: Python & Matplotlib"*](https://github.com/rougier/scientific-visualization-book).
