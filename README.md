# Entrega practica
## Datos
* Nombre: Laura González Fernández
* Titulación: Doble Grado Ingeniería en Tecnologías de la Telecomunicación + Ingeniería Aeroespacial en Aeronavegación
* Despliegue: [PythonAnywhere](https://lauragf.pythonanywhere.com)
* Video básico: [YouTube](https://youtu.be/G0HUv8M1iEw)
* Video parte opcional: [YouTube](https://youtu.be/pousGX76mKI)
* Cuenta en los laboratorios: lgonz

## Cuenta Admin Site
* laura/root

## Cuentas usuarios
* testuser1/AtilaEl1
* testuser2/AtilaEl1

## Resumen parte obligatoria
* Caja de login/logout en dropdown en la barra de navegación
* Barra de navegación muestra página actual resaltada
* Formulario de nuevo alimentador único para todas las fuentes de información
* Alimentadores obligatorios:
    * *YouTube*: el alimentador es un canal de YouTube y los ítems son videos, se puede ver el video desde la página de ítem.
    * *Last.fm* [Clave API](https://www.last.fm/join?next=/api/account/create): el alimentador es un artista y los ítems los albumes más populares.
* Estilos en los elementos de la plantilla base (banner, barra, caja usuario, pie)
* Documentos XML y JSON accesibles desde los botones en la parte inferior de la página principal


## Lista partes opcionales
* Nuevos alimentadores:
    * *Reddit*:
        El alimentador en un subreddit y los ítems son las noticias más importantes en el subreddit.
        En la página de ítem se puede ver el contenido de la noticia.
    * *Flickr*:
        El alimentador es una etiqueta y los ítems son las fotos más recientes con esa etiqueta.
        En la página de ítem se puede ver la foto y su autor.
    * *Goodreads* [Clave API](https://www.goodreads.com/api/keys):
        El alimentador es un autor y los ítems son los libros más populares que ha escrito.
        En la página de ítem se puede ver la portada y la sinopsis.
    * *Spotify* [Clave API](https://developer.spotify.com/documentation/general/guides/app-settings/#register-your-app):
        El alimentador es un artista y los ítems son sus canciones más populares
        En la página de item se puede ver la carátula del album y escuchar una parte de la canción
* Canal RSS con los 10 comentarios más recientes
* Formato XML y JSON para la página de alimentadores, de alimentador, de ítems, de usuarios y de usuario
* Bootstrap y más css para la apariencia de la página (iconos en los botones, dropdown para los enlaces de login/logout)
* Iconos para votar los ítems, los votos se pueden resetear pulsando de nuevo
* Internacionalización: la página está disponible en español e inglés según el idioma del navegador.
* Paginación de items: alimentadores, ítems, comentarios y usuarios
* Eliminar comentarios: un usuario registrado puede eliminar sus propios comentarios de los ítems
* Tests adicionales: [miscosas/tests](miscosas/tests)
* Listado de alimentadores elegidos en la página de usuario
* Eliminación de la anterior imágen subida por el usuario al cambiar la foto de perfil
* Página de error personalizada para URLs de la aplicación o nuevos alimentadores con identificadores que no existan
* Favicon

## Claves de desarrollador de las APIs utilizadas
Los alimentadores de last.fm, Goodreads y Spotify necesitan una clave de desarrollador para poder obtener nuevos datos de la fuente. Estas claves se obtienen en las siguientes páginas:
* [Last.fm](https://www.last.fm/join?next=/api/account/create)
* [Goodreads](https://www.goodreads.com/api/keys)
* [Spotify](https://developer.spotify.com/documentation/general/guides/app-settings/#register-your-app)

Las claves obtenidas se introducirán en la plantilla disponible en [project/secretkeys.py](project/secretkeys.py). Si no se rellenan las claves, la página seguirá funcionando como habitualmente pero no se podrán introducir nuevos alimentadores o actualizar la información de los ya existentes que provangan de esas fuentes.
