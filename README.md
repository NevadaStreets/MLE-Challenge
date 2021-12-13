# ML Engineer Challenge - Spike 

En este repositorio se desarrolló lo necesario para abordar el desafío propuesto por Spike para el puesto de Machine Learning Engineer. Este repositorio está compuesto por dos grandes proyectos:
1. Un `pipe` de procesamiento y predicción desarrollado en Apache Airflow. Esto principalmente se encuentra en la carpeta `dags`. 
2. Una API desarrollada en Flask para generar las predicciones del modelo.

# Cómo montar el proyecto

Todo está contenido en contenedores en [`docker`](https://docs.docker.com/get-docker/). Por lo que es necesario primero tener todo instalado.

Basta con ejecutar en la consola el siguiente comando dentro de la carpeta `ML-Pipe-Server`

```docker-compose up --build```

Esto debería levantar dos endpoints:
1. El primero es el del servidor en Airflow, montado en `http://localhost:8080/admin/`
2. El segundo es el de la API, montado en `http://localhost:5000/`

# Flujo de uso
## ML-Pipe

Dentro del endpoint `http://localhost:8080/admin/` es necesario activar los DAGs. Estos ejecutaran el pipeline de procesamiento y predicción de datos. Se debe activar dentro de la interfaz
<p align="center">
    <img src="images/1.png" width="800"/>
</p>
<p align="center">
    <img src="images/2.png" width="800"/>
</p>

Este pipeline está diseñado para almacenar los datos procesados en la carpeta `ML-Pipe-Server/dags/data`. Originalmente la idea era subir y obtener datos desde algún bucket (Google o AWS S3), pero debido a que no era posible utilizar un proveedor, se utilizó el mismo repositorio para el almacenamiento.

Finalmente, lo que hace el pipeline es dejar ejecutando un cronjob, que corre diariamente entrenando el modelo y generando un archivo serializado de él.

## API

La api es un servidor con dos enpoints en Flask. Estas son las rutas.

1. `GET`, `/` : Muestra un landpage
2. `POST`, `/predict`: Recibe un `JSON` con el formato:

    ```json
    {
        "data": [
            {
                "Precio_leche_shift3_mean": 216.025,
                "Coquimbo_shift3_mean": 2.606764709,
                "Valparaiso_shift3_mean": 5.3843100628,
                "Metropolitana_de_Santiago_shift3_mean": 12.5406711312,
                "Libertador_Gral__Bernardo_O_Higgins_shift3_mean": 6.0499689933,
                "Maule_shift3_mean": 5.4237271239,...
            },
            {
                "Precio_leche_shift3_mean": 216.025,
                "Coquimbo_shift3_mean": 2.606764709,
                "Valparaiso_shift3_mean": 5.3843100628,
                "Metropolitana_de_Santiago_shift3_mean": 12.5406711312,
                "Libertador_Gral__Bernardo_O_Higgins_shift3_mean": 6.0499689933,
                "Maule_shift3_mean": 5.4237271239,...
            },
            ...
        ]
    }
    ```
    Donde `data` es un arreglo con objetos que representan en el formato del dataset de entrenamiento.

    Lo que retorna es un arreglo con la predicción para cada dato, para este caso, sería algo así

    ```json
    [
        220.37761313926705,
        201.77613705123123,
        ...
    ]
    ```
# Decisiones y Supuestos
1. Se utilizó el modelo entrenado con todos los datos, sin utilizar set de testing ya que este ya habría sido validado de manera offline.
2. Como no se pudieron utilizar proveedores pagados, se utilizó todo mediante archivos locales. No se pudo almacenar directamente en el proyecto de la API el modelo serializado, ya que estaba en un diferente contenedor al del pipeline de procesamiento. Finalmente, se esperaba hacer la conexión entre ámbos proyectos mediante algún bucket.
3. Se buscó hacer el repositorio y el código lo más simple posible. Simplemente que cumpliera las funciones y responsabilidades establecidas, más que privilegiar una arquitectura compleja y robusta.
# Conclusiones y comentarios
1. Primero, aclarar que este `README` lo finalicé fuera del plazo establecido, no así la entrega del código. Por lo que si estiman necesario, pueden evaluarme utilzando el último commit antes de la hora de entrega. Para competir de forma justa con el resto.
2. Si bien el desafío no era tan complejo, decidí aprender Airflow para tratar de cumplir las expectativas. Al parecer eso me quitó demasiado tiempo jajaja, y no logré terminar el proyecto como quería :pensive:.
3. Inependiente de mi falta de tiempo, estuvo entretenido de todas formas. De hecho, me dieron muchas ganas de hacer el desafío de Data Science, se veía muy bacán el enunciado.
4. Si hubiera tenido más tiempo, hubiera organizado mejor el código y la estructura general del repositorio. Agradezco mucho que me hayan considerado para la postulación.
5. Arreglé un par de typos fuera de plazo. Tamnbién pueden no considerarlos si lo ven justo.

