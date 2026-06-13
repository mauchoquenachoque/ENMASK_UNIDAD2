# Informe de Factibilidad

![Logo UPT](./media/logo-upt.png)

**UNIVERSIDAD PRIVADA DE TACNA**

**FACULTAD DE INGENIERÍA**

**Escuela Profesional de Ingeniería de Sistemas**

Curso:BASE DE DATOS II

Docente:   
Mag. Patrick Cuadros Quiroga

Integrantes:

***Flores Navarro, Eduardo Gino         (2023076793)***  
***Choqueña, Mauricio Adrian			(2023076799)***

**Tacna – Perú**  
***2026***

 **Proyecto Enmascarado de datos**

## Control de versiones

| Versión | Hecha por | Revisada por | Aprobada por | Fecha | Motivo |
|:-------:|:---------:|:------------:|:------------:|:-----:|:------:|
| 3.0 | MPV | ELV | ARV | 10/10/2026 | Versión original |

## Índice

1. [Descripción del Proyecto](#1-descripción-del-proyecto)
2. [Riesgos](#2-riesgos)
3. [Análisis de la Situación Actual](#3-análisis-de-la-situación-actual)
4. [Estudio de Factibilidad](#4-estudio-de-factibilidad)
   - [4.1 Factibilidad Técnica](#41-factibilidad-técnica)
   - [4.2 Factibilidad Económica](#42-factibilidad-económica)
   - [4.3 Factibilidad Operativa](#43-factibilidad-operativa)
   - [4.4 Factibilidad Legal](#44-factibilidad-legal)
   - [4.5 Factibilidad Social](#45-factibilidad-social)
   - [4.6 Factibilidad Ambiental](#46-factibilidad-ambiental)
5. [Análisis Financiero](#5-análisis-financiero)
6. [Conclusiones](#6-conclusiones)

---

## 1. Descripción del Proyecto

### 1.1 Nombre del proyecto

**Emask**

### 1.2 Duración del proyecto

El proyecto tiene una duración estimada de **16 semanas**.

### 1.3 Descripción

El proyecto consiste en el desarrollo de una aplicación para el enmascaramiento de datos sensibles en bases de datos. Su objetivo es mejorar la seguridad y el control de acceso a la información, permitiendo que cada usuario visualice únicamente los datos autorizados según su rol o área.

La solución integra una arquitectura compuesta por base de datos, backend y frontend, y aplica técnicas de seguridad a nivel de fila (Row Level Security), enmascaramiento dinámico y auditoría de accesos. También incluye mecanismos de optimización y pruebas de seguridad para garantizar un rendimiento adecuado y prevenir fugas de datos.

### 1.4 Objetivos

#### 1.4.1 Objetivo general

Desarrollar una aplicación integral de seguridad en bases de datos que aplique técnicas de enmascaramiento dinámico y seguridad a nivel de fila, con el fin de proteger la información sensible y garantizar un acceso controlado de acuerdo con los roles de los usuarios.

#### 1.4.2 Objetivos específicos

- Implementar políticas de seguridad a nivel de fila (RLS) para que la base de datos filtre automáticamente los registros devueltos en función del rol o el área del usuario.
- Desarrollar un módulo de enmascaramiento dinámico que oculte parcial o totalmente campos confidenciales (como contraseñas, correos o datos financieros) para usuarios sin privilegios.
- Construir una arquitectura web completa (frontend y backend) que permita a los administradores gestionar roles y a los usuarios realizar consultas seguras.
- Integrar mecanismos de auditoría que registren accesos y consultas sobre datos sensibles mediante logs o triggers.

## 2. Riesgos

Se han identificado los siguientes riesgos para el proyecto:

- **Riesgo tecnológico:** Incompatibilidad entre las funciones de enmascarado dinámico de la base de datos y el framework del backend.
- **Riesgo de seguridad:** Configuración inadecuada de las políticas de seguridad a nivel de fila (RLS), lo que podría permitir filtraciones de datos durante las pruebas.
- **Riesgo de gestión:** Retrasos en el cronograma debido a la complejidad de integrar múltiples capas de seguridad (base de datos + API).

## 3. Análisis de la Situación Actual

### 3.1 Planteamiento del problema

Actualmente, muchas organizaciones gestionan bases de datos donde usuarios de distintos niveles (desarrolladores, analistas, administrativos) acceden a información sin un control granular. Esto provoca que usuarios con privilegios básicos puedan visualizar datos sensibles que no necesitan para sus funciones.

La situación actual se caracteriza por:

- **Exposición innecesaria:** usuarios con permisos limitados visualizan datos confidenciales como DNI, correos o saldos.
- **Falta de segregación:** no existe un mecanismo automático que distinga registros según el usuario, lo que obliga a crear filtros manuales en cada aplicación.
- **Vulnerabilidad:** la falta de enmascaramiento aumenta el riesgo de fugas internas o accesos no autorizados.

### 3.2 Consideraciones de hardware y software

Para resolver esta problemática se evaluaron las siguientes tecnologías del entorno actual:

- **Hardware:** estaciones de trabajo con procesador x64 y al menos 8 GB de RAM para soportar contenedores o servidores locales de bases de datos.
- **Software actual:** sistemas de gestión de bases de datos como PostgreSQL o SQL Server, que soportan RLS y enmascaramiento.
- **Tecnología de aplicación:** entornos de ejecución como Node.js o Python para integrar el backend con la seguridad de la base de datos.

## 4. Estudio de Factibilidad

El estudio de factibilidad evalúa la viabilidad técnica, económica, operativa, legal, social y ambiental del proyecto.

### 4.1 Factibilidad Técnica

El proyecto es técnicamente viable, pues se dispone del conocimiento y recursos necesarios.

- **Tecnología de bases de datos:** PostgreSQL 15+ es una opción adecuada por su soporte nativo de Row Level Security y su capacidad para implementar enmascaramiento dinámico.
- **Backend:** el backend puede desarrollarse con Node.js o Python, frameworks que permiten manejar peticiones asíncronas y conexiones seguras.
- **Frontend:** React.js es una opción apropiada para construir una interfaz administrativa clara y dinámica.
- **Sistemas operativos:** el desarrollo puede realizarse sobre Windows con Docker, lo que facilita portabilidad y despliegue.
- **Hardware de infraestructura:** estación de trabajo con procesador de 4 núcleos, 16 GB de RAM y 500 GB SSD para pruebas de enmascaramiento de datos.
- **Red:** acceso a internet para gestión de dependencias y despliegue en entornos locales controlados.

### 4.2 Factibilidad Económica

El sistema propuesto no requiere una inversión elevada, ya que aprovecha recursos y herramientas mayoritariamente gratuitos.

#### Costos generales

| Descripción | Cantidad | Costo Unitario (S/) | Total (S/) |
|---|---|---|---|
| Resmas de papel Bond A4 | 2 | 15.00 | 30.00 |
| Lapiceros y marcadores | 1 kit | 20.00 | 20.00 |
| Folderes y archivadores | 5 | 5.00 | 25.00 |
| **Total** | | | **75.00** |

#### Costos operativos durante el desarrollo

| Servicio | Meses | Costo Mensual (S/) | Total (S/) |
|---|---|---|---|
| Energía eléctrica | 4 | 50.00 | 200.00 |
| Internet de alta velocidad | 4 | 100.00 | 400.00 |
| Agua y servicios básicos | 4 | 30.00 | 120.00 |
| **Total** | | | **720.00** |

#### Costos del ambiente

| Descripción | Cantidad | Costo (S/) |
|---|---|---|
| Servicio de hosting / servidor cloud (pruebas) | 4 meses | 150.00 |
| Dominio .com / .pe | 1 año | 60.00 |
| Certificado SSL | 1 año | 0.00 (Let's Encrypt) |
| **Total** | | **210.00** |

#### Costos totales estimados

| Categoría | Total (S/) |
|---|---|
| Costos generales | 75.00 |
| Costos operativos | 720.00 |
| Costos de ambiente | 210.00 |
| **Total estimado** | **1,005.00** |

### 4.3 Factibilidad Operativa

La aplicación estará diseñada con una interfaz sencilla e intuitiva. Los usuarios accederán mediante autenticación y visualizarán la información según sus permisos.

El sistema automatizará el control de acceso mediante roles y políticas de seguridad, reduciendo la intervención manual y los errores humanos. El equipo tiene la capacidad de gestionar e implementar el sistema dentro del entorno académico, siguiendo una estructura modular.

### 4.4 Factibilidad Legal

El proyecto es legalmente viable y promueve el uso correcto de la información. Su propósito es proteger datos sensibles mediante enmascaramiento y control de acceso, lo cual está alineado con principios de seguridad y confidencialidad.

Además, el desarrollo tiene fines académicos y utiliza herramientas autorizadas. No se emplearán datos reales no controlados; se trabajará con información simulada o de prueba.

### 4.5 Factibilidad Social

El sistema contribuye a la privacidad y la confianza en los sistemas informáticos. No genera un impacto negativo en los usuarios, ya que su interfaz será fácil de usar y no altera significativamente las actividades normales.

Su implementación reduce el riesgo de uso indebido de la información y fomenta buenas prácticas de seguridad dentro de la organización.

### 4.6 Factibilidad Ambiental

Al ser una aplicación informática, no requiere procesos industriales ni materiales contaminantes. Su ejecución se realiza en equipos convencionales, por lo que el consumo energético es reducido y no genera un impacto ambiental significativo.

## 5. Análisis Financiero

El análisis financiero muestra que no se requieren inversiones significativas para el desarrollo del proyecto. Se utilizarán herramientas de software accesibles y, en su mayoría, gratuitas o con licencias académicas.

Los principales recursos necesarios son:

- Equipos de cómputo ya disponibles para los integrantes.
- Software de desarrollo y gestión de bases de datos con licencias libres o académicas.
- Tiempo de desarrollo como recurso principal.

No se contemplan costos adicionales por infraestructura, licencias comerciales o contratación externa.

En un escenario real, la implementación de este sistema puede generar beneficios indirectos al reducir riesgos asociados a fugas de datos y evitar sanciones por incumplimiento de normas de protección de información.

## 6. Conclusiones

1. El proyecto de enmascaramiento de datos es viable en sus dimensiones técnica, económica, operativa, legal, social y ambiental.
2. Técnicamente, se cuenta con herramientas y conocimientos adecuados para la implementación.
3. Económicamente, no se requiere una inversión elevada, lo que facilita su desarrollo en un entorno académico.
4. Operativamente, la solución puede ser utilizada sin dificultades por usuarios con distintos niveles de conocimiento.
5. Legalmente y socialmente, la propuesta está alineada con la protección de datos sensibles y la privacidad.
6. Ambientalmente, el proyecto no presenta impactos negativos significativos.

En conclusión, el proyecto puede desarrollarse de manera adecuada y representa una solución relevante para mejorar la seguridad en el manejo de datos sensibles.