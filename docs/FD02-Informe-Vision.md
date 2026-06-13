**![C:\\Users\\EPIS\\Documents\\upt.png][image1]**

**UNIVERSIDAD PRIVADA DE TACNA**

**FACULTAD DE INGENIERIA**

**Escuela Profesional de Ingeniería de Sistemas**

 **Proyecto *Enmask***

Curso:BASE DE DATOS II

Docente:   
Mag. Patrick Cuadros Quiroga

Integrantes:

***Flores Navarro, Eduardo Gino                    (2023076793)***  
***Choqueña, Mauricio Adrian			(2023076799)***

**Tacna – Perú**  
***2026***

| CONTROL DE VERSIONES |  |  |  |  |  |
| :---: | :---: | :---: | :---: | :---: | ----- |
| Versión | Hecha por | Revisada por | Aprobada por | Fecha | Motivo |
| 1.0 | MPV | ELV | ARV | 10/10/2020 | Versión Original |

# 

# 

# 

# 

# 

# 

# 

# 

# 

# 

# 

# **Sistema *Enmask***

# 

# **Documento de Visión**

# 

# **Versión *2.0***

| CONTROL DE VERSIONES |  |  |  |  |  |
| :---: | :---: | :---: | :---: | :---: | ----- |
| Versión | Hecha por | Revisada por | Aprobada por | Fecha | Motivo |
| 1.0 | MPV | ELV | ARV | 10/10/2020 | Versión Original |

**INDICE GENERAL**

1\.	Introducción	1

1.1	Propósito	1

1.2	Alcance	1

1.3	Definiciones, Siglas y Abreviaturas	1

1.4	Referencias	1

1.5	Visión General	1

2\.	Posicionamiento	1

2.1	Oportunidad de negocio	1

2.2	Definición del problema	2

3\.	Descripción de los interesados y usuarios	3

3.1	Resumen de los interesados	3

3.2	Resumen de los usuarios	3

3.3	Entorno de usuario	4

3.4	Perfiles de los interesados	4

3.5	Perfiles de los Usuarios	4

3.6	Necesidades de los interesados y usuarios	6

4\.	Vista General del Producto	7

4.1	Perspectiva del producto	7

4.2	Resumen de capacidades	8

4.3	Suposiciones y dependencias	8

4.4	Costos y precios	9

4.5	Licenciamiento e instalación	9

5\.	Características del producto	9

6\.	Restricciones	10

7\.	Rangos de calidad	10

8\.	Precedencia y Prioridad	10

9\.	Otros requerimientos del producto	10

	[b) Estandares legales](#heading=h.e3e78nt179y4)	32

	[c) Estandares de comunicación](#heading=h.e3e78nt179y4)	37

	[d) Estandaraes de cumplimiento de la plataforma](#heading=h.e3e78nt179y4)	42

	[e) Estandaraes de calidad y seguridad](#heading=h.e3e78nt179y4)	42

[CONCLUSIONES](#heading=h.mqhmxaghy4r0)	46

[RECOMENDACIONES](#heading=h.nszg08t2cuew)	46

[BIBLIOGRAFIA](#heading=h.x3wodqjfs5iu)	46

[WEBGRAFIA](#heading=h.x0yo7omysuet)	46

# **1.Introducción:**

En la economía digital actual, el dato es el activo más valioso de una organización, pero también su mayor riesgo legal y reputacional. Con la entrada en vigor de regulaciones estrictas como el GDPR (Europa), CCPA (California) y leyes de protección de datos locales, el manejo de Información de Identificación Personal (PII) ya no es solo una cuestión técnica, sino una obligación legal crítica.

El problema central radica en el ciclo de vida del desarrollo de software. Para que los desarrolladores y equipos de QA (Aseguramiento de Calidad) puedan entregar productos sin errores, necesitan probar las aplicaciones con datos que reflejen la complejidad del mundo real. Históricamente, las empresas han optado por el camino más arriesgado: clonar bases de datos de producción hacia entornos de prueba. Esta práctica deja datos sensibles (nombres, tarjetas de crédito, historiales médicos) expuestos a personal que no debería tener acceso a ellos, creando una superficie de ataque masiva para filtraciones internas o externas.

Enmask surge como una respuesta tecnológica a esta problemática. No es simplemente un script de limpieza; es una plataforma de orquestación de privacidad diseñada para la arquitectura moderna. En un ecosistema donde las aplicaciones dependen tanto de bases de datos relacionales (SQL) para transacciones, como de bases de datos documentales (NoSQL) para escalabilidad, Enmask garantiza que la sensibilidad de los datos se elimine mediante técnicas de enmascarado estático determinístico.

Al transformar datos reales en versiones ficticias pero funcionalmente idénticas, Enmask permite a las organizaciones innovar a gran velocidad en sus procesos de desarrollo, manteniendo el cumplimiento normativo "por diseño" (*Privacy by Design*) y eliminando el riesgo de exposición de identidad en sus entornos no productivos.

## **1.1.Propósito**

El propósito principal de este informe es presentar el diseño, la fundamentación técnica y la estrategia de implementación de Enmask, una plataforma avanzada de Enmascarado Estático de Datos (Static Data Masking \- SDM). El sistema está diseñado para ser el puente de seguridad entre los datos reales de producción y los entornos de desarrollo, garantizando que la privacidad sea un componente intrínseco del ciclo de vida del software (*Privacy by Design*).

Los objetivos específicos que este proyecto busca cumplir son:

* Eliminación del Riesgo de Exposición: Proveer una metodología automatizada para transformar Información de Identificación Personal (PII) en datos ficticios, eliminando la posibilidad de filtraciones de datos reales en entornos de prueba (QA) y desarrollo (Staging).  
* Orquestación Híbrida y Consistente: Establecer un mecanismo técnico que permita el enmascarado simultáneo en motores PostgreSQL (Relacional) y MongoDB (NoSQL), asegurando que las relaciones entre ambos sistemas se mantengan íntegras tras la transformación.  
* Garantizar la Utilidad de los Datos: Implementar algoritmos de enmascarado determinístico que permitan a los desarrolladores y analistas realizar pruebas funcionales, de rendimiento y de integración con datos que conservan el formato, la lógica y las propiedades estadísticas de los originales, pero sin contenido sensible.  
* Cumplimiento Normativo Automatizado: Facilitar a las organizaciones el cumplimiento de estándares legales internacionales (como GDPR, LGPD o ISO 27001\) mediante la generación de auditorías y reportes sobre los procesos de desensibilización de datos realizados.  
* Optimización del flujo DevOps: Integrar el proceso de enmascarado como un paso sencillo y configurable dentro de los flujos de trabajo de ingeniería, reduciendo la fricción entre el equipo de seguridad y el equipo de desarrollo.

## **1.2.Alcance**

El proyecto Enmask se define como una plataforma de software para el enmascarado estático de datos en arquitecturas híbridas. El alcance detallado incluye:

* Conectividad Multimotor: Soporte nativo para la extracción y carga de datos en PostgreSQL (Relacional) y MongoDB (NoSQL/Documental).  
* Identificación de PII: Funcionalidad para que el usuario mapee columnas (SQL) y campos/claves (NoSQL) que contienen información sensible.  
* Algoritmos de Transformación: Implementación de al menos cuatro técnicas de desensibilización:  
  * *Sustitución:* Reemplazo por datos ficticios realistas (Librería Faker).  
  * *Redacción:* Ocultamiento parcial o total (ej. `****-1234`).  
  * *Hashing Determinístico:* Transformación de IDs manteniendo la consistencia entre SQL y NoSQL.  
  * *Nullificación:* Eliminación de datos no esenciales para las pruebas.  
* Interfaz de Gestión (Frontend): Un panel de control basado en React para la configuración de reglas, visualización de esquemas y ejecución de tareas de enmascarado.  
* Motor de Orquestación (Backend): Una API en FastAPI encargada de procesar las reglas y ejecutar los jobs de transformación de manera asíncrona.

Fuera del Alcance:

* Enmascarado dinámico (en tiempo real sobre la base de datos de producción).  
* Soporte para archivos no estructurados (PDFs, imágenes, audios).  
* Limpieza de datos (Data Cleansing) o corrección de errores preexistentes en la fuente.

## **1.3.Definiciones, Siglas y Abreviaturas**

| Sigla / Término | Definición |
| :---- | :---- |
| **PII** | *Personally Identifiable Information*. Cualquier dato que pueda identificar a una persona (nombre, DNI, biométricos). |
| **SDM** | *Static Data Masking*. Proceso de crear una copia física de la base de datos con los datos ya transformados. |
| **DDM** | *Dynamic Data Masking*. Técnica que enmascara los datos "al vuelo" según los permisos del usuario que consulta. |
| **API REST** | Interfaz de programación de aplicaciones que utiliza peticiones HTTP para transferir datos. |
| **FastAPI** | Framework moderno de Python para construir APIs de alto rendimiento con validación de datos automática. |
| **Determinismo** | Capacidad de un algoritmo para devolver siempre el mismo resultado ante la misma entrada (clave para mantener integridad entre SQL y NoSQL). |
| **BSON** | *Binary JSON*. Formato de almacenamiento binario utilizado por MongoDB para sus documentos. |
| **Docker** | Plataforma de virtualización a nivel de sistema operativo para desplegar contenedores de software. |
| **GDPR** | *General Data Protection Regulation*. Reglamento de la Unión Europea que sirve de estándar global para la privacidad. |
| **Integridad Referencial** | Regla de consistencia en SQL que asegura que una clave foránea siempre apunte a una clave primaria válida. |

## **1.4.Referencias**

Para el desarrollo y fundamentación técnica de Enmask, se han tomado como base los siguientes estándares, marcos legales y documentaciones oficiales:

* **Marcos Legales de Privacidad:**  
  * *Reglamento General de Protección de Datos (GDPR/RGPD):* Específicamente los artículos referentes a la "Privacidad desde el diseño" y la "Seudonimización".  
  * *Ley de Protección de Datos Personales (LPDP):* Normativa local vigente para el tratamiento de información sensible.  
* **Documentación Tecnológica:**  
  * *PostgreSQL Global Development Group (v16.x):* Estándares de seguridad en bases de datos relacionales y gestión de llaves foráneas.  
  * *MongoDB Manual (v7.0+):* Guías de seguridad para colecciones BSON y agregaciones de datos.  
  * *FastAPI Framework Documentation:* Estándares para el desarrollo de APIs asíncronas y validación Pydantic.  
  * *React Docs:* Mejores prácticas para la gestión de estados en interfaces de usuario complejas.  
* **Estándares de Seguridad:**  
  * *OWASP Top 10:* Guía de referencia para la mitigación de vulnerabilidades en aplicaciones web.  
  * *ISO/IEC 27001:* Estándar internacional para sistemas de gestión de seguridad de la información.

## **1.5.Visión general**

Este informe está estructurado para guiar al lector desde la necesidad estratégica hasta la implementación técnica detallada de Enmask:

1. **Posicionamiento:** Analiza la oportunidad de negocio y define el problema crítico de la exposición de datos en entornos de prueba.  
2. **Interesados y Usuarios :** Identifica a los actores clave (CISO, Desarrolladores, QA) y sus necesidades específicas dentro de la organización.  
3. **Vista General del Producto:** Explica la arquitectura técnica (FastAPI \+ React), las capacidades de enmascarado y los costos asociados.  
4. **Características y Restricciones :** Detalla las funcionalidades del motor de enmascarado y las limitaciones técnicas impuestas por el entorno.  
5. **Estándares y Calidad:** Profundiza en el cumplimiento legal, de comunicación y seguridad que validan el proyecto como una solución empresarial.

# **2\. Posicionamiento**

### **2.1 Oportunidad de negocio**

En el mercado actual, las organizaciones enfrentan una presión sin precedentes para acelerar sus ciclos de desarrollo (*Time-to-Market*) mientras cumplen con regulaciones de privacidad cada vez más estrictas. La oportunidad de negocio de Enmask se sustenta en tres pilares financieros y operativos:

* **Reducción de Costos por Incumplimiento:** Las multas por violaciones al GDPR pueden alcanzar los 20 millones de euros o el 4% de la facturación anual. **Enmask** actúa como un escudo legal, eliminando el riesgo de sanciones al asegurar que los datos en entornos de prueba no sean considerados "datos personales".  
* **Eficiencia Operativa en DevOps:** Actualmente, los equipos de DBA (Administradores de Bases de Datos) pierden horas anonimizando datos manualmente con scripts frágiles. **Enmask** automatiza este proceso, permitiendo que un entorno de prueba esté listo en minutos, no en días.  
* **Aceleración de la Innovación Segura:** Permite la externalización de servicios de desarrollo (Outsourcing) o el uso de consultores externos sin el riesgo de entregarles información sensible de clientes reales.

### **2.2 Definición del problema**

Para entender la necesidad de Enmask, se define la problemática actual mediante la siguiente matriz de diagnóstico:

| Elemento | Descripción |
| :---- | :---- |
| **El problema de** | El uso de datos reales de producción en entornos de desarrollo, pruebas (QA) y analítica. |
| **Afecta a** | Oficiales de Seguridad (CISO), Desarrolladores de Software, Testers de QA y el Departamento Legal. |
| **El impacto es** | Exposición de PII a personal no autorizado, vulnerabilidad ante filtraciones internas y riesgo inminente de multas legales y pérdida de reputación de marca. |
| **Una solución exitosa sería** | Una plataforma centralizada (**Enmask**) que automatice el enmascarado de datos en arquitecturas híbridas (SQL y NoSQL), garantizando que los datos sean seguros pero mantengan su utilidad funcional. |

# **3\. Descripción de los interesados y usuarios**

### **3.1 Resumen de los interesados**

Los interesados son aquellos que tienen un interés estratégico en que los datos estén protegidos, aunque no necesariamente operen la herramienta.

| Interesado | Rol Principal | Interés en el Proyecto |
| :---- | :---- | :---- |
| **CISO (Oficial de Seguridad)** | Garantizar la integridad y privacidad de la información. | Reducir la superficie de ataque y evitar filtraciones de PII. |
| **Oficial de Cumplimiento (DPO)** | Asegurar el cumplimiento legal (GDPR/LPDP). | Evitar multas legales y asegurar auditorías exitosas. |
| **Director de Tecnología (CTO)** | Optimizar los procesos de ingeniería. | Acelerar el ciclo de vida del software (SDLC) con datos seguros. |
| **Clientes Finales** | Dueños de los datos originales. | Que su información personal no sea expuesta en entornos de prueba. |

### **3.2 Resumen de los usuarios**

Los usuarios son el personal técnico que interactuará directamente con la interfaz de Enmask.

| Usuario | Descripción | Uso de Enmask |
| :---- | :---- | :---- |
| **Desarrollador de Backend** | Crea y mantiene las aplicaciones. | Solicita bases de datos enmascaradas para depurar errores reales. |
| **Tester** | Ejecuta pruebas de calidad. | Utiliza datos enmascarados para validar flujos de negocio. |
| **Administrador de BD (DBA)** | Gestiona la infraestructura de datos. | Configura las reglas de enmascarado y ejecuta los jobs de transformación. |

### **3.3 Entorno de usuario**

Los usuarios de **Enmask** operan en un entorno de alta exigencia técnica:

* **Ubicación:** Oficinas corporativas o trabajo remoto mediante VPN segura.  
* **Plataforma:** Navegadores web modernos (Chrome, Firefox, Edge) para acceder al dashboard de React.  
* **Entorno Técnico:** Terminales de desarrollo con acceso a clústeres de PostgreSQL y MongoDB en redes internas o nube (AWS/Azure).

### **3.4 Perfiles de los interesados**

* **CISO:** Persona con perfil gerencial y técnico preocupada por los riesgos. Su éxito se mide en la ausencia de incidentes de seguridad.  
* **DPO (Data Protection Officer):** Perfil legal-técnico que requiere reportes de cumplimiento y evidencia de que los datos han sido anonimizados correctamente.

### **3.5 Perfiles de los Usuarios**

* **Ingeniero de DevOps/DBA:** Usuario experto. Requiere una herramienta que sea automatizable (vía API de FastAPI) y que no rompa la estructura de las bases de datos complejas.  
* **QA Tester:** Usuario funcional. No necesita ver el código, pero necesita que los datos "parezcan reales" (ej. que un campo de email tenga formato de email) para que sus pruebas automáticas no fallen.

### **3.6 Necesidades de los interesados y usuarios**

| Interesado/Usuario | Necesidad Crítica | Solución de Enmask |
| :---- | :---- | :---- |
| **CISO / DPO** | Reportes de auditoría y cumplimiento legal. | Generación de logs de enmascarado y dashboards de estado. |
| **DBA** | Mantener la integridad entre SQL y NoSQL. | Motor de enmascarado determinístico que vincula ambos mundos. |
| **Desarrollador / QA** | Datos realistas para pruebas funcionales. | Uso de algoritmos de sustitución (Faker) para mantener el formato. |
| **Empresa** | Reducción de tiempos de aprovisionamiento de datos. | Automatización del proceso de clonado y enmascarado en un solo flujo. |

# **4\. Vista General del Producto**

### **4.1 Perspectiva del producto**

Enmask no es una base de datos aislada, sino un orquestador de seguridad que se sitúa entre el entorno de Producción y el entorno de Desarrollo. Su arquitectura está diseñada para conectarse de forma segura a fuentes de datos sensibles, procesar la información en memoria y depositar una versión "limpia" en servidores de destino.

* **Arquitectura:** Basada en microservicios, utilizando FastAPI para la lógica de procesamiento pesado y React para la consola de administración.  
* **Interoperabilidad:** Se integra nativamente con clústeres de PostgreSQL y MongoDB, permitiendo una visión unificada de los datos de la organización, independientemente de si son estructurados o documentales.

### **4.2 Resumen de capacidades**

El producto se divide en cuatro módulos funcionales principales:

| Capacidad | Descripción Técnica |
| :---- | :---- |
| **Escaneo de Esquemas** | Identificación automática de tablas en SQL y colecciones en NoSQL. |
| **Motor de Enmascarado** | Algoritmos de transformación (Sustitución, Hashing, Redacción) que operan sobre el flujo de datos. |
| **Sincronización Híbrida** | Garantía de que los IDs relacionados en Postgres y Mongo se enmascaren de forma idéntica (Determinismo). |
| **API de Orquestación** | Permite disparar jobs de enmascarado desde pipelines de CI/CD (GitHub Actions, Jenkins). |

### **4.3 Suposiciones y dependencias**

Para el correcto funcionamiento de Enmask, se asumen las siguientes condiciones:

* **Acceso a Red:** El servidor donde resida el backend de Enmask debe tener permisos de lectura en la red de origen (Producción/Pre-producción) y de escritura en la red de destino (Dev/QA).  
* **Recursos de Hardware:** Se requiere una instancia con al menos 8GB de RAM para manejar buffers de datos durante procesos de enmascarado masivos.  
* **Dependencias de Software:** El sistema requiere contenedores Docker para asegurar la consistencia de las versiones de Python y las librerías de conexión (psycopg2 para Postgres y motor para MongoDB).

### **4.4 Costos y precios**

Aunque Enmask se proyecta inicialmente como una herramienta interna, su estructura de costos para la organización se divide en:

* **Costo de Infraestructura:** Servidores en la nube (AWS/Azure) para alojar el backend y el frontend.  
* **Costo de Mantenimiento:** Horas de ingeniería para la actualización de reglas de privacidad según cambien las leyes locales.  
* **Ahorro Proyectado:** Se estima un ahorro del 70% en tiempo de DBA y la eliminación total del riesgo de multas por exposición de datos en QA.

### **4.5 Licenciamiento e instalación**

* **Licenciamiento:** El software se distribuye bajo una licencia Enterprise Propia (o MIT si decides hacerlo Open Source), permitiendo su uso ilimitado dentro de los dominios de la corporación.  
* **Instalación:** El despliegue se realiza mediante Docker Compose, lo que permite levantar todo el stack (Frontend, Backend y Base de Datos de configuración) con un solo comando, facilitando la portabilidad entre servidores locales y la nube.

# **5\. Características del producto**

Este capítulo detalla las capacidades operativas de Enmask, divididas por su lógica de procesamiento y su compatibilidad con los distintos motores de base de datos.

### **5.1 Motor de Enmascarado Multiformato**

El núcleo de Enmask permite aplicar transformaciones específicas dependiendo del tipo de dato y el motor de origen:

* **Enmascarado para SQL (PostgreSQL):**  
  * **Preservación de Integridad Referencial:** Al enmascarar una Clave Primaria (PK), el sistema actualiza automáticamente todas las Claves Foráneas (FK) relacionadas para que las relaciones entre tablas (ej. Clientes y Facturas) no se rompan.  
  * **Enmascarado a nivel de Columna:** Permite seleccionar columnas específicas (como email, telefono, ssn) para ser transformadas, dejando el resto de la tabla intacta.  
* **Enmascarado para NoSQL (MongoDB):**  
  * **Manejo de Esquema Flexible:** Capacidad de identificar y enmascarar campos sensibles incluso si estos no aparecen en todos los documentos de una colección.  
  * **Procesamiento de Documentos Anidados:** El motor puede navegar a través de subdocumentos y arreglos (arrays) para encontrar PII oculta en estructuras complejas.

### **5.2 Catálogo de Técnicas de Desensibilización**

**Enmask** ofrece una librería de funciones de enmascarado preconfiguradas:

1. **Sustitución Realista (Faking):** Reemplaza datos reales por datos ficticios que mantienen el formato (ej. reemplaza un nombre real por uno generado aleatoriamente que "parece" real).  
2. **Hashing Salteado (Ouscuscación):** Convierte identificadores en cadenas alfanuméricas irreconocibles pero únicas. Si se usa la misma clave, el ID 100 siempre será aB89x, permitiendo cruzar datos entre SQL y NoSQL sin revelar la identidad.  
3. **Redacción Parcial (Masking):** Ideal para visualización parcial (ej. transformar 4555-1234-5678-9012 en XXXX-XXXX-XXXX-9012).  
4. **Aleatorización Numérica:** Aplica una varianza a valores numéricos (ej. salarios o montos de transacciones) para que los totales estadísticos sean similares pero los valores individuales sean falsos.

### **5.3 Panel de Control y Configuración (UI)**

Interfaz desarrollada en **React** que permite:

* **Explorador de Conexiones:** Configurar y probar la conexión a múltiples bases de datos.  
* **Mapeador de Privacidad:** Interfaz visual para "arrastrar y soltar" reglas de enmascarado sobre el esquema detectado.  
* **Monitor de Tareas:** Visualización en tiempo real del progreso del enmascarado (porcentaje completado, filas/documentos procesados).

### **5.4 Auditoría y Reportes**

* **Logs de Ejecución:** Registro detallado de qué tablas fueron procesadas, cuándo y bajo qué reglas (sin guardar nunca los datos sensibles originales).  
* **Certificado de Anonimización:** Generación de un reporte técnico que certifica que la base de datos de destino ya no contiene PII, útil para auditorías de cumplimiento legal.

# **6\. Restricciones**

Las restricciones definen los límites operativos y técnicos bajo los cuales Enmask garantiza un funcionamiento óptimo. Estas se dividen en tres categorías principales:

### **6.1 Restricciones de Infraestructura y Hardware**

* **Capacidad de Memoria RAM:** El proceso de enmascarado de grandes volúmenes de datos ocurre en buffers de memoria para optimizar la velocidad. Se requiere un mínimo de **8 GB de RAM** para evitar el desbordamiento al procesar tablas con millones de registros.  
* **Conectividad de Red:** El sistema requiere una conexión de baja latencia entre el servidor de **Enmask** y los motores de base de datos (**PostgreSQL/MongoDB**). Caídas en la red durante el proceso de *streaming* de datos pueden invalidar la integridad del set de datos de destino.

### **6.2 Restricciones Técnicas de los Motores de Datos**

* **PostgreSQL (SQL):** \* No se soporta el enmascarado automático de tipos de datos personalizados (*User-Defined Types*) complejos sin una configuración manual previa.  
  * La **Integridad Referencial** solo se garantiza si las relaciones están explícitamente definidas mediante *Foreign Keys* en el esquema de la base de datos.  
* **MongoDB (NoSQL):**  
  * El enmascarado en documentos con más de 4 niveles de anidamiento puede degradar el rendimiento del motor de transformación.  
  * No se soporta el enmascarado de datos binarios almacenados en GridFS (archivos grandes).

### **6.3 Restricciones de Seguridad y Privacidad**

* **Enmascarado Unidireccional:** Por diseño, Enmask no almacena tablas de equivalencia entre el dato real y el enmascarado. El proceso es irreversible para garantizar que, ante un compromiso del servidor de desarrollo, los datos originales no puedan ser recuperados mediante ingeniería inversa.  
* **Acceso a Producción:** El software requiere permisos de solo lectura en la fuente. No se permite que Enmask realice cambios directamente sobre las bases de datos de producción para evitar riesgos de disponibilidad.

### **6.4 Restricciones de Desarrollo (Alcance Temporal)**

* **Lenguajes Soportados:** La interfaz y el motor están optimizados para caracteres UTF-8. El soporte para alfabetos no latinos (ej. cirílico o kanji) en las reglas de sustitución (Faker) está limitado a la disponibilidad de las librerías base.  
* **Versiones de Base de Datos:** Compatibilidad garantizada para **PostgreSQL 12+** y **MongoDB 5.0+**. Versiones anteriores podrían presentar incompatibilidades con los conectores asíncronos de **FastAPI**.

# **7\. Rangos de calidad**

Los rangos de calidad establecen los niveles de servicio y desempeño que Enmask debe mantener para ser considerado una solución de grado empresarial.

### **7.1 Disponibilidad y Escalabilidad**

* **Disponibilidad del Dashboard:** La interfaz de usuario (React) debe garantizar una disponibilidad del 99.5**%** durante el horario laboral, permitiendo a los administradores configurar reglas en cualquier momento.  
* **Escalabilidad Horizontal:** El backend (FastAPI) debe ser capaz de ejecutarse en múltiples contenedores Docker detrás de un balanceador de carga, permitiendo procesar múltiples bases de datos en paralelo sin degradación del servicio.

### **7.2 Rendimiento (Performance)**

* **Tiempo de Procesamiento:** El motor de enmascarado debe ser capaz de procesar un mínimo de 10,000 registros por segundo en PostgreSQL y 5,000 documentos por segundo en MongoDB (sujeto a la complejidad de los datos anidados).  
* **Latencia de la API:** Las consultas de configuración y lectura de esquemas desde el frontend deben tener un tiempo de respuesta menor a 200ms.

### **7.3 Seguridad y Privacidad**

* **Cifrado en Tránsito:** Toda comunicación entre el frontend, el backend y las bases de datos debe realizarse mediante protocolos cifrados (TLS 1.2 o superior).  
* **Aislamiento de Credenciales:** Las credenciales de las bases de datos de producción nunca se almacenan en el navegador del usuario; se gestionan mediante variables de entorno seguras o *secrets* en el servidor.  
* **Entropía de Datos:** Los datos sustituidos (Faker) deben pasar pruebas de aleatoriedad básica para asegurar que no existan patrones que permitan revertir el enmascarado mediante análisis estadístico.

### **7.4 Usabilidad**

* **Facilidad de Configuración:** Un usuario técnico nuevo (DBA o QA) debe ser capaz de configurar su primera tarea de enmascarado en menos de 10 minutos gracias a la interfaz intuitiva de "Point & Click".  
* **Consistencia Visual:** El dashboard debe seguir los principios de diseño de carga cognitiva mínima, resaltando claramente qué datos han sido protegidos y cuáles siguen siendo sensibles.

### **7.5 Portabilidad**

* **Independencia de Plataforma:** Gracias al uso de Docker y arquitecturas basadas en web, el sistema debe ser capaz de ejecutarse idénticamente en entornos Linux, Windows Server o MacOS, así como en nubes privadas o públicas.

# **8\. Precedencia y Prioridad**

Para garantizar el éxito del proyecto **Enmask**, las funcionalidades se han categorizado según su importancia crítica para la operación y el cumplimiento legal. Se utiliza la metodología MoSCoW (Must-have, Should-have, Could-have) para establecer el orden de desarrollo.

### **8.1 Prioridad Alta (Críticos \- MVP)**

Estas características representan el núcleo del producto y deben estar operativas en la primera fase de despliegue:

* **Conectividad Base:** Establecimiento de túneles seguros y conexión con PostgreSQL y MongoDB.  
* **Algoritmos de Sustitución y Hashing:** Implementación de las funciones de transformación de datos PII (nombres, documentos, correos).  
* **Motor de Consistencia Híbrida:** Lógica determinística para que el ID 001 en SQL sea igual al 001 en NoSQL tras el enmascarado.  
* **Interfaz de Mapeo:** Panel en React para que el usuario seleccione qué campos desea proteger.

### **8.2 Prioridad Media (Importantes)**

Funcionalidades que aportan un valor significativo pero no impiden el funcionamiento básico:

* **Escaneo Automático de Esquemas:** Capacidad del backend para detectar tablas y colecciones sin intervención manual.  
* **Dashboard de Monitoreo:** Visualización del progreso de las tareas de enmascarado en tiempo real.  
* **Manejo de Documentos Anidados:** Soporte avanzado para estructuras complejas de **BSON** en MongoDB.

### **8.3 Prioridad Baja (Deseables/Futuros)**

Características que mejoran la experiencia de usuario o escalabilidad, pero pueden postergarse:

* **Integración con CI/CD:** Plugins para disparar el enmascarado automáticamente desde Jenkins o GitHub Actions.  
* **Reportes de Cumplimiento PDF:** Generación automática de certificados de anonimización para auditores.  
* **Soporte para Motores Adicionales:** Expansión del soporte hacia bases de datos **Columnar** (como Cassandra) o **Key-Value** (como Redis) mencionadas en el mapa tecnológico inicial.

### **8.4 Matriz de Precedencia Técnica**

El desarrollo seguirá el siguiente orden lógico de dependencias:

1. **Backend (FastAPI):** Configuración de los conectores de base de datos.  
2. **Lógica de Enmascarado:** Desarrollo de los algoritmos de transformación.  
3. **Frontend (React):** Interfaz para la gestión de reglas.  
4. **Orquestador:** Unión de la interfaz con los procesos de ejecución asíncrona.

# **9\. Otros requerimientos del producto**

### **b) Estándares legales**

Para que **Enmask** sea una herramienta válida en entornos corporativos, debe alinearse con marcos legales que exigen la protección de la privacidad:

* **Cumplimiento con GDPR (RGPD):** El sistema implementa el concepto de "Privacidad desde el Diseño" (Artículo 25\) y permite la "Seudonimización" (Artículo 4), transformando datos de modo que no puedan atribuirse a un interesado sin información adicional (la cual queda fuera del alcance del entorno de prueba).  
* **Cumplimiento con Leyes Locales (LPDP):** Adaptación de las reglas de enmascarado para satisfacer los requisitos de soberanía de datos y protección de derechos de los titulares de información en el territorio nacional.  
* **Derecho al Olvido y Minimización:** El proceso de enmascarado garantiza la minimización de datos al permitir que solo la información estrictamente necesaria para el desarrollo sea migrada a los entornos de destino.

### **c) Estándares de comunicación**

La interacción entre los componentes de **Enmask** y los usuarios sigue protocolos estandarizados para asegurar la interoperabilidad:

* **Protocolo HTTP/S:** Toda la comunicación entre el frontend (React) y el backend (FastAPI) se realiza mediante REST APIs utilizando TLS 1.3 para el cifrado de datos en tránsito.  
* **Formato de Intercambio JSON:** Se utiliza el estándar JSON para el envío de configuraciones y metadatos de esquemas, asegurando compatibilidad total con el ecosistema **NoSQL (MongoDB)**.  
* **WebSockets:** Implementación de sockets para el reporte en tiempo real del progreso de las tareas de enmascarado masivo hacia el dashboard del usuario.

### **d) Estándares de cumplimiento de la plataforma**

* **Containerización (Docker):** El despliegue debe cumplir con el estándar de la Open Container Initiative (OCI), garantizando que el software funcione de manera idéntica en nubes locales o públicas (AWS, Azure, GCP).  
* **Arquitectura de Microservicios:** Cumplimiento con los principios de acoplamiento débil y alta cohesión, facilitando la escalabilidad de los motores de enmascarado de forma independiente.

### **e) Estándares de calidad y seguridad**

* **OWASP ASVS:** Alineación con el *Application Security Verification Standard* para prevenir vulnerabilidades comunes como la inyección de código o el acceso no autorizado a los conectores de base de datos.  
* **Hashing de Alta Entropía:** Uso de algoritmos SHA-256 con *salts* dinámicos para garantizar que el enmascarado determinístico no pueda ser revertido mediante ataques de diccionario o tablas de arcoíris.  
* **Validación de Datos (Pydantic):** Uso de tipado estricto en el backend para asegurar que ningún dato corrupto o malformado sea procesado por el motor de transformación.

# **CONCLUSIONES**

1. **Mitigación de Riesgos:** El proyecto Enmask demuestra ser una solución crítica para la seguridad empresarial, logrando reducir la superficie de ataque en entornos de desarrollo al eliminar el uso de datos reales, cumpliendo así con normativas internacionales como el GDPR.  
2. **Versatilidad Tecnológica:** La arquitectura híbrida implementada (FastAPI \+ React) permite gestionar de manera eficiente la complejidad de los datos estructurados en **PostgreSQL** y la flexibilidad de los documentos en MongoDB, resolviendo el reto de la consistencia de datos entre diferentes paradigmas.  
3. **Eficiencia Operativa:** La automatización del enmascarado estático no solo protege la privacidad, sino que optimiza los tiempos de entrega (Time-to-Market) al facilitar a los equipos de QA y Desarrollo el acceso inmediato a bases de datos seguras y funcionales.  
4. **Viabilidad Técnica:** El uso de técnicas determinísticas y algoritmos de sustitución realista (Faker) garantiza que las pruebas de software sigan siendo válidas, manteniendo la lógica de negocio intacta sin comprometer la identidad de los usuarios.

# **RECOMENDACIONES**

1. **Implementación de CI/CD:** Se recomienda integrar Enmask directamente en los flujos de integración continua para que el refresco de bases de datos enmascaradas sea un proceso totalmente desatendido.  
2. **Ampliación de Motores:** Dada la estructura modular del backend, se sugiere expandir los conectores hacia bases de datos de tipo Columnar (Cassandra) o Graph (Neo4j) para cubrir un espectro más amplio del mapa tecnológico empresarial.  
3. **Auditorías Periódicas:** Es aconsejable realizar pruebas de re-identificación periódicas sobre los datos enmascarados para asegurar que los algoritmos de hashing y sustitución mantengan niveles óptimos de entropía frente a nuevas técnicas de ciberataque.  
4. **Capa de Autenticación Avanzada:** Para futuras versiones, se recomienda integrar protocolos de seguridad como OAuth2 o SAML para gestionar el acceso de los administradores al dashboard de configuración.

# **BIBLIOGRAFIA**

* **Date, C. J.** (2019). *Database Design and Relational Theory: Normal Forms and All That Jazz*. O'Reilly Media.  
* **Kleppmann, M.** (2017). *Designing Data-Intensive Applications: The Big Ideas Behind Reliable, Scalable, and Maintainable Systems*. O'Reilly Media.  
* **OWASP Foundation.** (2025). *Top 10 Privacy Risks in Web Applications*.  
* **Ramakrishnan, R., & Gehrke, J.** (2003). *Database Management Systems*. McGraw-Hill.

# **WEBGRAFIA**

* **FastAPI Documentation:** [https://fastapi.tiangolo.com/](https://fastapi.tiangolo.com/)  
* **MongoDB Security Manual:** [https://www.mongodb.com/docs/manual/security/](https://www.mongodb.com/docs/manual/security/)  
* **PostgreSQL Anonymizer:** [https://postgresql-anonymizer.readthedocs.io/](https://postgresql-anonymizer.readthedocs.io/)  
* **GDPR Official Text:** [https://gdpr-info.eu/](https://gdpr-info.eu/)  
* **React Documentation:** [https://react.dev/](https://react.dev/)

[image1]: <data:image/png;base64,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>