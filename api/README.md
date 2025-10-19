Aquí tienes el texto plano completo:

# STITCHAPP | Endpoints

**Desarrollador:** Miguel Chamorro
**Contacto:** [miguelchamorro912@gmail.com](mailto:miguelchamorro912@gmail.com)

## General Response

{estado, descripcion,res} res: Contiene la respuesta de la api.


## GET

### Bordados

/api/bordados/filtrar Descripción: Filtra los bordados con distintos parametros opcionales.

contiene (str) : Filtra si contiene [contiene] en el nombre del bordado. favorito (bool) : Filtra si son favoritos o no. categoria (int) : Filtra por categoría. order (int) : Ordena la respuesta con las siguientes opciones; [1: A-Z | 2: Z-A | 3: Primera Modificación | 4: Última modificación].

Response: [{id, nombre, favorito}]


---

/api/bordados/imagen Descripción: Retorna la previsualizacaión de un bordado renderizada en pyembroidery.

id (int) : id del bordado (id >= 1)

Response: FileResponse, Type: PNG


---

/api/bordados/id:int Descripción: Retorna información de un bordado.

Response: {id, nombre, categoria, favorito, modificacion}


---

### Categorías

/api/categorias/lista Descripción: Retorna todas las categorías disponibles

Response: [{id,nombre,descripcion,cantidad}]


---

### Medios

/api/medios/lista Descripcion: Retorna los medios extraibles disponibles con filtros opcionales

solo_registrados (bool) : Filtra solo los medios extraíbles registrados.

Response: [{id, nombre, registrado}]


---

/api/medios/id:int Descripción: Retorna información acerca de un medio registrado.

Response: {id_bordados, limite}


---

## POST

### Bordados

/api/bordados/previsualizacion Descripción: Retorna una presivualización de un archivo .PES

Body: multiport/form-data {file (.PES)}

Response: FileResponse


---

/api/bordados Descripción: Crea un bordado nuevo

Body: multiport/form-data {nombre, categoria, favorito, file}

Response: id (int)


---

### Categorías

/api/categorias Descripción: Crea una categoría nueva

Body: multiport/form-data {nombre, descripcion}

Response: id (int)


---

### Medios

/api/medios/exportado Descripción: Registra la exportación de un bordado.

Body: multiport/form-data {id_bordado, id_medio}

Response: {current_timestamp}


---

/api/medios Descripción: Registra un medio extraíble.

Body: multiport/form-data {nombre_actual, nuevo_nombre}

Response: {id, current_timestamp, token}


---

## UPDATE

### Bordados

/api/bordados/id:int Descripción: Actualiza información sobre un bordado.

Body: multiport/form-data {nombre, categoria, favorito}

Response: {current_timestamp}


---

### Categorías

/api/categorias/id:int Descripción: Actualiza información sobre una categoría.

Body: multiport/form-data {nombre, descripción}

Response: {current_timestamp}


---

## DELETE

### Categorias

/api/categorias/id:int Descripción: Elimina una categoría

Body: null

Response: {current_timestamp}


---

### Medios

/api/medios/id:int Descripción: Elimina un bordado de un medio extraíble

Body: null

Response: {current_timestamp}