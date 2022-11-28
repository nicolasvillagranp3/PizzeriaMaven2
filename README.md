# PizzeriaMaven2
Este proyecto trata de obtener, a partir de una ETL que procesa una serie de pedidos de un dataset de una pizzeria, el número de ingredientes que se debe pedir por cada una de las semanas del año. La idea tras la transformacion de los datos es bastante simple: mapear las fechas de cada uno de los pedidos a su correspondiente semana, e ir sumando por cada pizza pedida los ingredientes necesarios por cada tipo de ingrediente distinto. Todo hecho con el objetivo de ser lo mas eficiente posible, usando las funciones built-in de pandas para iterar sobre los datos de manera rápida y segura. El output es un csv con el número de ingredientes para cada tipo por semana y dos ficheros xml con el reporte de tipologia antes de haberlo y transformado y despues. Lo consideramos interesante para mostrar que todos los datos han sido limpiados sin necesidad de obviar ni uno solo.
## Limpieza de Datos.
- Fechas ausentes: Al ordenar los pedidos por 'orderId' se ordenan automaticamente también las fechas, de ahi que nos bastara con coger la del dia anterior o siguiente. Pandas digiere muchos de los formatos dados, menos uno dado que debia ser controlado.
- Cantidad ausente o invalida: En este caso hemos considerado que en las cantidades negativas se habia introducido un signo por error (cosa bastante logica). En las que ni aparecian las cantidades hemos aplicado interpolacion lineal.
- Pizza Id ausente: En este caso hemos cogido las 10 pizzas mas vendidas (haciendo la suposicion de que con el numero de datos limpios teniamos una idea de la distribucion de las pizzas suficiente)  y hemos rellenado de manera aleatoria los ausentes.
De esta manera conseguimos usar todos los datos disponibles, haciendo una prediccion mucho mas robusta.
## Requirements.
Para poder correr el programa hay que instalar los paquetes necesarios con sus correspondientes versiones. Se ejecutara el siguiente codigo en terminal:
>>>pip install -r requirements.txt
## Docker.
Para lanzar la imagen de docker habrá que seguir los siguientes pasos:
1. Crear la imagen: 
- El punto indica que se cogen todos los archivos del directorio en el que nos encontramos. Podemos llamar a la imagen como queramos, teniendo en cuenta que al ejecutarla tendremos que usar ese nombre.
>>>docker build . -t 'Nombre Imagen'
2. Una vez que tengamos la imagen creada tendremos que elegir un path absoluto del directorio al que queramos que se linkee el contenedor de docker
para que podamos ver la salida del programa.
- absolute_path = ['path del directorio de salida host']. En el caso en el que no exista el directorio que queremos linkear lo crea.
- Es importante mantener la estructura del siguiente comando. En particular el path tras ':' no debera ser alterado ya que es el directorio interno del contenedor.
>>>docker run -v absolute_path:/out 'Nombre Imagen'
