# Informe de Especificación de Requerimientos
![Logo UPT](./media/logo-upt.png)

**UNIVERSIDAD PRIVADA DE TACNA**

**FACULTAD DE INGENIERÍA**

**Escuela Profesional de Ingeniería de Sistemas**

**Proyecto:** Emask - Sistema de Enmascaramiento de Datos  
**Curso:** Base de Datos II  
**Semestre:** 2026-I  
**Docente:** Mag. Patrick Cuadros Quiroga

**Integrantes:**
- Flores Navarro, Eduardo Gino (2023076793)
- Choqueña, Mauricio Adrian (2023076799)

**Tacna - Perú**  
**2026**

---

## Control de versiones

| Versión | Hecha por | Revisada por | Aprobada por | Fecha | Motivo |
|:-------:|:---------:|:------------:|:------------:|:-----:|:------:|
| 1.0 | EG / MA | ELV | ARV | 15/03/2026 | Versión Inicial |
| 1.1 | EG / MA | PCQ | PCQ | 22/03/2026 | Agregar diagramas UML |
| 2.0 | EG / MA | PCQ | PCQ | 01/04/2026 | Versión Final |

---

## Índice

1. [Introducción](#introducción)
2. [I. Generalidades de la Empresa](#i-generalidades-de-la-empresa)
   - [1. Nombre de la Empresa](#1-nombre-de-la-empresa)
   - [2. Visión](#2-visión)
   - [3. Misión](#3-misión)
   - [4. Organigrama](#4-organigrama)
3. [II. Visionamiento de la Empresa](#ii-visionamiento-de-la-empresa)
   - [1. Descripción del Problema](#1-descripción-del-problema)
   - [2. Objetivos de Negocios](#2-objetivos-de-negocios)
   - [3. Objetivos de Diseño](#3-objetivos-de-diseño)
   - [4. Alcance del Proyecto](#4-alcance-del-proyecto)
   - [5. Viabilidad del Sistema](#5-viabilidad-del-sistema)
   - [6. Información Obtenida del Levantamiento de Información](#6-información-obtenida-del-levantamiento-de-información)
4. [III. Análisis de Procesos](#iii-análisis-de-procesos)
   - [a) Diagrama del Proceso Actual](#a-diagrama-del-proceso-actual)
   - [b) Diagrama del Proceso Propuesto](#b-diagrama-del-proceso-propuesto)
5. [IV. Especificación de Requerimientos de Software](#iv-especificación-de-requerimientos-de-software)
   - [a) Requerimientos Funcionales Iniciales](#a-requerimientos-funcionales-iniciales)
   - [b) Requerimientos No Funcionales](#b-requerimientos-no-funcionales)
   - [c) Requerimientos Funcionales Finales](#c-requerimientos-funcionales-finales)
   - [d) Reglas de Negocio](#d-reglas-de-negocio)
6. [V. Fase de Desarrollo](#v-fase-de-desarrollo)
   - [1. Perfiles de Usuario](#1-perfiles-de-usuario)
   - [2. Modelo Conceptual](#2-modelo-conceptual)
   - [3. Modelo Lógico](#3-modelo-lógico)
7. [Conclusiones](#conclusiones)
8. [Recomendaciones](#recomendaciones)
9. [Bibliografía](#bibliografía)
10. [Webgrafía](#webgrafía)

---

## Introducción

El presente documento presenta la especificación de requerimientos para el desarrollo del sistema **Emask**, una aplicación integral de seguridad en bases de datos orientada al enmascaramiento de datos sensibles. Este proyecto surge de la necesidad crítica de proteger información confidencial en organizaciones donde múltiples usuarios con diferentes niveles de autorización requieren acceso a datos de la base de datos.

El enmascaramiento de datos es un mecanismo de seguridad fundamental que permite que usuarios visualicen únicamente la información que corresponde a su rol, aplicando técnicas como seguridad a nivel de fila (RLS), enmascaramiento dinámico y auditoría de accesos. Este enfoque reduce significativamente el riesgo de fugas de información y cumple con regulaciones modernas de protección de datos.

Este documento describe los requerimientos funcionales y no funcionales del sistema, analiza los procesos actuales, define reglas de negocio y proporciona especificaciones técnicas para la fase de desarrollo.

---

## I. Generalidades de la Empresa

### 1. Nombre de la Empresa

**Emask Solutions**

Una iniciativa académica de la Escuela Profesional de Ingeniería de Sistemas de la Universidad Privada de Tacna, enfocada en desarrollar soluciones de seguridad de datos.

### 2. Visión

Ser una solución de referencia en seguridad de datos a nivel de Sudamérica, proporcionando herramientas confiables y de fácil implementación que protegen la información sensible de las organizaciones mediante técnicas avanzadas de enmascaramiento y control de acceso.

### 3. Misión

Desarrollar una plataforma integral de enmascaramiento de datos que permita a las organizaciones proteger información sensible, garantizar cumplimiento normativo y facilitar el acceso controlado a datos según roles de usuario, mediante una arquitectura segura, escalable y de fácil implementación.

### 4. Organigrama

```
┌─────────────────────────────────────────┐
│   Dirección Académica (PCQ)             │
└────────────────┬────────────────────────┘
                 │
        ┌────────┴────────┐
        │                 │
   ┌────▼────┐      ┌─────▼─────┐
   │ Equipo  │      │   Equipo  │
   │Backend  │      │ Frontend  │
   │(EGF)    │      │  (MAC)    │
   └─────────┘      └───────────┘
```

---

## II. Visionamiento de la Empresa

### 1. Descripción del Problema

Las organizaciones modernas almacenan información financiera, personal y operativa en bases de datos centralizadas. Sin embargo, muchos usuarios con diferentes roles requieren acceder a ésta información para realizar sus funciones diarias. La problemática actual radica en que:

- **Expuesto de datos innecesariamente:** Usuarios con permisos básicos pueden visualizar datos sensibles (DNI, correos, saldos, información financiera) que no son necesarios para su trabajo.
- **Sin control granular:** Las bases de datos no poseen mecanismos nativos de filtrado automático, obligando a crear controles manuales complejos en la aplicación.
- **Riesgo de infiltración:** La falta de enmascaramiento aumenta el riesgo de fuga de información por acceso no autorizado o negligencia del personal.
- **Incumplimiento normativo:** Muchas jurisdicciones exigen control granular sobre el acceso a datos sensibles, y la ausencia de estas medidas puede resultar en sanciones legales.

### 2. Objetivos de Negocios

- Proteger información sensible de la organización mediante enmascaramiento automático.
- Cumplir con regulaciones de protección de datos (LPDP, GDPR, etc.).
- Reducir el riesgo de filtraciones internas en un 85%.
- Facilitar la auditoría de accesos a información sensible.
- Mejorar la confianza de clientes y stakeholders en la seguridad de datos.
- Implementar un modelo de seguridad a nivel de base de datos para todas las aplicaciones.

### 3. Objetivos de Diseño

- Diseñar una arquitectura que integre seguridad a nivel de fila (RLS) en la base de datos.
- Desarrollar un módulo de enmascaramiento dinámico en el backend.
- Crear una interfaz administrativa intuitiva para gestionar roles y políticas.
- Implementar mecanismos de auditoría automática de accesos.
- Asegurar que el sistema sea escalable y mantenible.
- Cumplir con estándares de calidad de código y seguridad.

### 4. Alcance del Proyecto

**Incluye:**
- Diseño e implementación de políticas de seguridad a nivel de fila (RLS) en PostgreSQL.
- Desarrollo de un módulo backend de enmascaramiento dinámico.
- Creación de interfaz de administración de roles.
- Implementación de auditoría de accesos.
- Base de datos de prueba con datos simulados.
- Documentación técnica y manual de usuario.
- Pruebas unitarias e integración con cobertura mínima del 75%.

**Excluye:**
- Migración de datos desde sistemas legados.
- Soporte para bases de datos distintas a PostgreSQL en esta versión.
- Integración con sistemas de autenticación corporativos (SSO, LDAP).
- Módulos de reportes avanzados.
- Aplicaciones móviles.

### 5. Viabilidad del Sistema

**Técnica:** El proyecto es técnicamente viable. Se utilizarán tecnologías probadas y de código abierto (PostgreSQL, Node.js/Python, React.js). La arquitectura propuesta es implementable en el cronograma establecido.

**Económica:** No requiere inversiones significativas. Se usarán herramientas gratuitas y licencias académicas. La estimación de costos es de S/. 1,005.00.

**Operica:** El sistema cuenta con una interfaz intuitiva que permite su operación por personas con conocimientos básicos en sistemas.

**Legal:** La solución cumple con regulaciones de protección de datos y no infringe normativa alguna.

**Ambiental:** No presenta impactos negativos significativos en el ambiente.

### 6. Información Obtenida del Levantamiento de Información

Se realizaron entrevistas y sesiones de trabajo con:

- **Docente responsable:** Para identificar objetivos académicos.
- **Analistas de datos:** Para comprender flujos de acceso a información.
- **Personal administrativo:** Para definir roles y permisos necesarios.

**Información clave recopilada:**

| Aspecto | Información |
|---|---|
| Tipos de datos sensibles | DNI, salarios, bancos, correos corporativos |
| Roles principales | Administrador, Analista, Supervisor, Usuario final |
| Frecuencia de acceso | Diaria (consultas + reportes) |
| Volumen de datos | Hasta 100,000 registros |
| Requisitos de performance | Respuesta en < 2 segundos |
| Requisitos de auditoría | Log de todos los accesos por usuario |

---

## III. Análisis de Procesos

### a) Diagrama del Proceso Actual

**Proceso actual:** Acceso sin control granular a datos sensibles.

```
Usuario Inicia Sesión
         ↓
┌─────────────────────┐
│ Valida credenciales │
└──────────┬──────────┘
           ↓
    ¿Credenciales válidas?
      ↙              ↖
    SÍ              NO
    ↓               ↓
Accede a BD      Rechaza sesión
    ↓
┌──────────────────────────┐
│ Consulta TODOS los datos │
│ Sin enmascaramiento      │
└──────────┬───────────────┘
           ↓
RIESGO: Usuario ve datos
no autorizados para su rol
```

**Problemas identificados:**

- No existe segregación de datos por rol.
- Todos los usuarios ven todos los registros.
- No hay enmascaramiento de campos sensibles.
- No se registra quién accede a qué información.

### b) Diagrama del Proceso Propuesto

**Proceso propuesto:** Acceso controlado con enmascaramiento automático.

```
Usuario Inicia Sesión
         ↓
┌──────────────────────────┐
│ Valida credenciales      │
│ Obtiene rol del usuario  │
└──────────┬───────────────┘
           ↓
    ¿Credenciales válidas?
      ↙              ↖
    SÍ              NO
    ↓               ↓
┌────────────────┐  Rechaza sesión
│ Aplica RLS     │
│ por rol        │
└────────┬───────┘
         ↓
┌────────────────────────────┐
│ Consulta filtrada a BD     │
│ Solo registros autorizados │
└────────┬───────────────────┘
         ↓
┌────────────────────────────┐
│ Aplica enmascaramiento     │
│ dinámico en backend        │
└────────┬───────────────────┘
         ↓
┌────────────────────────────┐
│ Registra acceso en audit   │
│ log (usuario, datos, hora) │
└────────┬───────────────────┘
         ↓
Usuario recibe datos
enmascarados según rol
```

**Mejoras implementadas:**

- Segregación automática de datos por rol en BD.
- Enmascaramiento dinámico de campos sensibles.
- Auditoría completa de accesos.
- Cumplimiento de regulaciones de protección de datos.

---

## IV. Especificación de Requerimientos de Software

### a) Requerimientos Funcionales Iniciales

| ID | Descripción | Prioridad |
|---|---|---|
| RF-001 | Autenticación de usuarios con email y contraseña | Alta |
| RF-002 | Gestión de roles y permisos en base de datos | Alta |
| RF-003 | Aplicación de políticas RLS en consultas | Alta |
| RF-004 | Enmascaramiento dinámico de campos sensibles | Alta |
| RF-005 | Consulta de datos con filtros | Media |
| RF-006 | Generación de reportes básicos | Media |
| RF-007 | Auditoría de cada acceso a datos | Alta |
| RF-008 | Administración de usuarios | Media |

### b) Requerimientos No Funcionales

| ID | Descripción | Prioridad |
|---|---|---|
| RNF-001 | API RESTful con latencia < 2 segundos | Alta |
| RNF-002 | Base de datos PostgreSQL versión 13+ | Alta |
| RNF-003 | Frontend responsive (móvil y escritorio) | Media |
| RNF-004 | Cobertura de pruebas mínima 75% | Alta |
| RNF-005 | Documentación completa del código | Alta |
| RNF-006 | Seguridad: encriptación de contraseñas (bcrypt) | Alta |
| RNF-007 | Seguridad: validación de entrada en todos los campos | Alta |
| RNF-008 | Rendimiento: máximo 100 consultas/segundo | Media |
| RNF-009 | Disponibilidad: 99.5% uptime en producción | Media |
| RNF-010 | Compatibilidad: Chrome, Firefox, Safari versiones recientes | Media |

### c) Requerimientos Funcionales Finales

| ID | Descripción | Estado | Pruebas |
|---|---|---|---|
| RF-001 | Autenticación con email/contraseña | Completado | Pruebas unitarias |
| RF-002 | Gestión de roles (Administrador, Analista, Supervisor, Usuario) | Completado | Pruebas de integración |
| RF-003 | RLS automático por usuario en SELECT * queries | Completado | Pruebas unitarias |
| RF-004 | Enmascaramiento para DNI (mostrar últimos 4 dígitos) | Completado | Pruebas unitarias |
| RF-005 | Enmascaramiento para email (mostrar dominio) | Completado | Pruebas unitarias |
| RF-006 | Enmascaramiento para datos financieros (mostrar **\*\*\*\*) | Completado | Pruebas unitarias |
| RF-007 | Auditoría con timestamp y usuario | Completado | Pruebas integración |
| RF-008 | Consulta con SELECT simple | Completado | Pruebas unitarias |
| RF-009 | Consulta con WHERE y ORDER BY | Completado | Pruebas integración |
| RF-010 | Panel administrativo de usuarios | Completado | Pruebas E2E |
| RF-011 | Panel administrativo de roles | Completado | Pruebas E2E |
| RF-012 | Visualización de logs de auditoría | Completado | Pruebas integración |

### d) Reglas de Negocio

#### RN-001: Acceso a Datos por Rol

- **Administrador:** Acceso total a todos los datos sin enmascaramiento y visualización de logs completos.
- **Analista:** Acceso a datos de su área; campos sensibles aparecen enmascarados.
- **Supervisor:** Acceso a datos agregados de su equipo; datos personales enmascarados.
- **Usuario Final:** Acceso solo a sus propios registros; datos financieros enmascarados siempre.

#### RN-002: Enmascaramiento de Campos Sensibles

| Campo | Enmascaramiento | Ejemplo |
|---|---|---|
| DNI | Últimos 4 dígitos | \*\*\*\*\*\*\*\*\*\*1234 |
| Email | nombre@\*\*\*\*\*\*\* | usuario@**\*.com** |
| Teléfono | Últimos 4 dígitos | \*\*\*\*\*\*5678 |
| Salario | Valor completo con \*\*\*\*\* | S/. ******* |
| Cuenta Bancaria | Últimos 4 dígitos | \*\*\*\*\*\*\*\*1592 |

#### RN-003: Auditoría Obligatoria

Cada acceso a datos sensibles debe registrar:
- Usuario que realiza la consulta
- Tabla y campos consultados
- Número de registros retornados
- Marca de tiempo
- IP de origen
- Resultado (éxito/error)

#### RN-004: Validación de Sesión

- Las sesiones expiran después de 30 minutos sin actividad.
- Las contraseñas deben tener mínimo 8 caracteres, letras mayúsculas y números.
- Máximo 5 intentos fallidos de login; bloqueo por 15 minutos después.

#### RN-005: Integridad de Datos

- Las políticas RLS deben ser evaluadas ANTES de retornar cualquier dato.
- El enmascaramiento debe aplicarse DESPUÉS del filtrado RLS.
- Los registros auditados no pueden ser modificados ni eliminados.

#### RN-006: Consistencia en Reportes

- Los reportes descargables deben aplicar el mismo enmascaramiento que la interfaz.
- Los exportes a Excel deben estar protegidos con contraseña.

#### RN-007: Segregación de Ambientes

- Base de datos de desarrollo: solo datos de prueba.
- Base de datos de QA: datos de prueba y casos edge.
- Base de datos de producción: datos reales con políticas estrictas.

---

## V. Fase de Desarrollo

### 1. Perfiles de Usuario

#### Perfil 1: Administrador del Sistema

| Atributo | Valor |
|---|---|
| Nombre | Administrador |
| Rol | Responsable de configuración |
| Permisos | Acceso total, gestión de usuarios y roles |
| Datos permitidos | Todos sin enmascaramiento |
| Acciones principales | Crear usuarios, asignar roles, visualizar logs |
| Frecuencia de uso | 2-3 veces por semana |

#### Perfil 2: Analista de Datos

| Atributo | Valor |
|---|---|
| Nombre | Analista Senior |
| Rol | Análisis de información |
| Permisos | Lectura de datos de su área |
| Datos permitidos | Datos de su departamento, campos sensibles enmascarados |
| Acciones principales | Consultas complejas, generación de reportes |
| Frecuencia de uso | Diaria (4-5 horas) |

#### Perfil 3: Supervisor de Equipo

| Atributo | Valor |
|---|---|
| Nombre | Supervisor |
| Rol | Supervisión de personal |
| Permisos | Lectura de datos del equipo a su cargo |
| Datos permitidos | Datos agregados, información sensible enmascarada |
| Acciones principales | Revisar desempeño del equipo, consultas básicas |
| Frecuencia de uso | Diaria (1-2 horas) |

#### Perfil 4: Usuario Final

| Atributo | Valor |
|---|---|
| Nombre | Empleado |
| Rol | Acceso limitado a información |
| Permisos | Lectura de sus propios datos |
| Datos permitidos | Solo registros propios, con enmascaramiento |
| Acciones principales | Consultar estado personal, descargar reportes |
| Frecuencia de uso | 2-3 veces por semana |

### 2. Modelo Conceptual

#### a) Diagrama de Paquetes

```
┌─────────────────────────────────────┐
│         Presentación                │
│  ┌───────────────────────────────┐  │
│  │   Frontend (React.js)         │  │
│  │ - Login                       │  │
│  │ - Dashboard                   │  │
│  │ - Gestión de usuarios         │  │
│  │ - Gestión de roles            │  │
│  │ - Consultas                   │  │
│  │ - Reportes                    │  │
│  └───────────────────────────────┘  │
└────────────┬────────────────────────┘
             │ HTTP REST
┌────────────▼────────────────────────┐
│        Aplicación                   │
│  ┌───────────────────────────────┐  │
│  │     Backend (Node.js/Python)  │  │
│  │ - API REST                    │  │
│  │ - Autenticación               │  │
│  │ - Enmascaramiento dinámico    │  │
│  │ - Auditoría                   │  │
│  │ - Gestión de roles            │  │
│  └───────────────────────────────┘  │
└────────────┬────────────────────────┘
             │ SQL / Conexiones
┌────────────▼────────────────────────┐
│          Datos                      │
│  ┌───────────────────────────────┐  │
│  │   PostgreSQL 13+              │  │
│  │ - Usuarios                    │  │
│  │ - Roles                       │  │
│  │ - Datos (sensibles)           │  │
│  │ - Política RLS                │  │
│  │ - Logs de auditoría           │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

#### b) Diagrama de Casos de Uso

```
┌─────────────────────────────────────────────────┐
│                   SISTEMA EMASK                 │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌──────────────┐          ┌─────────────────┐ │
│  │  Iniciador   │          │  Administrador  │ │
│  │    Sesión    │          │                 │ │
│  └──────┬───────┘          └────────┬────────┘ │
│         │                           │          │
│    ┌────┴──────────────────────────┴─────┐   │
│    │   Autenticar Usuario                │   │
│    └────┬──────────────────────────────┬──┘   │
│         │                              │       │
│  ┌──────▼──────┐            ┌──────────▼────┐ │
│  │ Consultar   │            │  Administrar  │ │
│  │ Datos       │            │  Usuarios     │ │
│  └──────┬──────┘            └──────┬────────┘ │
│         │                          │          │
│  ┌──────▼──────────────────────────▼────┐    │
│  │   Aplicar RLS & Enmascaramiento      │    │
│  └──────┬──────────────────────────────┬┘    │
│         │                              │     │
│  ┌──────▼──────┐            ┌──────────▼────┐│
│  │ Ver Datos   │            │  Registrar    ││
│  │ Filtrados   │            │  en Auditoría ││
│  └─────────────┘            └───────────────┘│
│                                              │
└─────────────────────────────────────────────┘
```

#### c) Escenarios de Caso de Uso (Narrativa)

##### Caso de Uso 1: Consultar Datos Sensibles

**Actor Principal:** Analista de Datos  
**Precondición:** Usuario autenticado

**Flujo Principal:**

1. El Analista accede al módulo de Consultas.
2. Ingresa filtros de búsqueda (departamento, rango de fechas).
3. El sistema valida los permisos del usuario basado en su rol.
4. La base de datos aplica RLS, retornando solo registros autorizados.
5. El backend aplica enmascaramiento a campos sensibles.
6. El sistema registra la consulta en el log de auditoría.
7. Los datos enmascarados se muestran en interfaz.

**Postcondición:** Datos consultados con seguridad garantizada.

##### Caso de Uso 2: Administrar Roles

**Actor Principal:** Administrador  
**Precondición:** Usuario autenticado como Administrador

**Flujo Principal:**

1. El Administrador accede a Gestión de Roles.
2. Visualiza lista de roles existentes.
3. Selecciona un rol para editar o crea uno nuevo.
4. Define permisos sobre tablas y columnas.
5. Asigna políticas de enmascaramiento por campo.
6. Guarda cambios.
7. El sistema aplica cambios a todas las conexiones nuevas.

**Postcondición:** Rol actualizado y aplicado a usuarios asignados.

##### Caso de Uso 3: Generar Reporte de Auditoría

**Actor Principal:** Administrador  
**Precondición:** Existen registros de auditoría

**Flujo Principal:**

1. El Administrador accede a Reportes > Auditoría.
2. Define filtros: rango de fechas, usuario, tipo de operación.
3. El sistema consulta la tabla de auditoría.
4. Genera reporte en formato PDF o Excel.
5. El reporte es protegido con contraseña.
6. Se permite descargar o consultar en línea.

**Postcondición:** Reporte generado y disponible para descargar.

---

### 3. Modelo Lógico

#### a) Análisis de Objetos

**Objeto 1: Usuario**

```
Usuario
├── id: Integer (PK)
├── email: String (UNIQUE)
├── contraseña: String (Hash bcrypt)
├── nombre: String
├── rol_id: Integer (FK)
├── estado: Enum (activo, inactivo)
├── fecha_creacion: DateTime
├── fecha_modificacion: DateTime
└── última_conexión: DateTime
```

**Objeto 2: Rol**

```
Rol
├── id: Integer (PK)
├── nombre: String (UNIQUE)
├── descripción: String
├── permisos: JSON
└── fecha_creacion: DateTime
```

**Objeto 3: Tabla Protegida**

```
Empleado (Tabla que requiere RLS)
├── id: Integer (PK)
├── email: String
├── dni: String (Sensible)
├── nombre: String
├── apellido: String
├── departamento: String
├── salario: Decimal (Sensible)
├── teléfono: String (Sensible)
├── número_cuenta: String (Sensible)
├── estado: Enum (activo, inactivo)
├── responsable_id: Integer (FK a Usuario)
└── fecha_creacion: DateTime
```

**Objeto 4: Auditoría**

```
AuditLog
├── id: Integer (PK)
├── usuario_id: Integer (FK)
├── tabla: String
├── operación: Enum (SELECT, INSERT, UPDATE, DELETE)
├── registros_afectados: Integer
├── fecha_hora: DateTime (automatic)
├── ip_origen: String
├── resultado: Enum (éxito, error)
└── descripción: String (mensaje de error si aplica)
```

#### b) Diagrama de Actividades con Objetos

```
Inicio
  ↓
Lectura: credenciales del usuario
  ↓
┌──────────────────────────────────┐
│ Verificar credenciales           │
│ en tablaUsuario                  │
└──────────┬───────────────────────┘
           ↓
    ¿Válidas?
    ↙         ↖
   SÍ         NO
   ↓          ↓
┌─────────────────────────────┐
│ Leer Rol del usuario        │
│ de tabla Rol                │
│ donde id = usuario.rol_id   │
└──────────┬──────────────────┘
           ↓
┌──────────────────────────────────┐
│ Lectura: Permisos del rol        │
│ del campo Rol.permisos (JSON)    │
└──────────┬─────────────────────┘
           ↓
┌──────────────────────────────────┐
│ Aplicar RLS en query SELECT      │
│ WHERE usuario_responsable_id = ? │
│ AND estado = 'activo'            │
└──────────┬─────────────────────┘
           ↓
Registrar en AuditLog
  ├── usuario_id = usuario.id
  ├── tabla = 'Empleado'
  ├── operación = 'SELECT'
  ├── resultado = 'éxito'
  └── fecha_hora = NOW()
  ↓
┌──────────────────────────────────┐
│ Aplicar Enmascaramiento          │
│ según Rol.permisos.máscaras      │
   - DNI → últimos 4               │
   - Email → nombre@***            │
   - Salario → S/. *****           │
└──────────┬─────────────────────┘
           ↓
Retornar datos enmascarados
  ↓
Fin
```

#### c) Diagrama de Secuencia

```
Usuario    Frontend    Backend    PostgreSQL  AuditLog
   │          │           │            │         │
   │─Login───→│           │            │         │
   │          │─POST /auth─>           │         │
   │          │           │            │         │
   │          │           │─Consulta user tab   │
   │          │           │←─Usuario+rol─       │
   │          │           │            │         │
   │          │           │─Registra acceso────→│
   │          │           │            │         │
   │          │←Token JWT─│            │         │
   │          │           │            │         │
   │←Autorizado           │            │         │
   │          │           │            │         │
   │─Consultar datos      │            │         │
   │          │           │            │         │
   │          │─GET /employees         │         │
   │          │            │           │         │
   │          │            │─Aplica RLS        │
   │          │            │─Query con WHERE───→│
   │          │            │           │         │
   │          │            │←Retorna datos      │
   │          │            │           │         │
   │          │─Aplica mascaramiento   │         │
   │          │            │           │         │
   │          │            │─Registra acceso──→│
   │          │            │           │         │
   │          │←JSON enmascarado       │         │
   │          │           │            │         │
   │←Datos protegidos      │            │         │
```

#### d) Diagrama de Clases

```
┌─────────────────────────────────┐
│           Usuario               │
├─────────────────────────────────┤
│ - id: int                       │
│ - email: string                 │
│ - contraseña: string            │
│ - nombre: string                │
│ - rol: Rol                      │
│ - estado: string                │
│ - fecha_creacion: DateTime      │
├─────────────────────────────────┤
│ + autenticar()                  │
│ + validarPermisos()             │
│ + cambiarContraseña()           │
│ + desactivar()                  │
└─────────────────────────────────┘
         ▲
         │ hereda
         │
┌─────────────────────────────────┐
│       Administrador             │
├─────────────────────────────────┤
│ + crearUsuario()                │
│ + eliminarUsuario()             │
│ + asignarRol()                  │
│ + crearRol()                    │
│ + verLogs()                     │
└─────────────────────────────────┘

┌─────────────────────────────────┐
│            Rol                  │
├─────────────────────────────────┤
│ - id: int                       │
│ - nombre: string                │
│ - descripción: string           │
│ - permisos: JSON                │
│ - máscaras: Map<string,string>  │
├─────────────────────────────────┤
│ + agregarPermiso()              │
│ + removerPermiso()              │
│ + aplicarMáscara()              │
└─────────────────────────────────┘
         ▲
         │ posee
         │
┌─────────────────────────────────┐
│         Permiso                 │
├─────────────────────────────────┤
│ - tabla: string                 │
│ - operación: string (SELECT...) │
│ - columnas: Array<string>       │
└─────────────────────────────────┘

┌─────────────────────────────────┐
│       ResultadoConsulta         │
├─────────────────────────────────┤
│ - datos: Array                  │
│ - enmascarados: boolean         │
│ - fecha_ejecución: DateTime     │
├─────────────────────────────────┤
│ + aplicarEnmascaramiento()      │
│ + validarAcceso()               │
│ + registrarAuditoría()          │
└─────────────────────────────────┘
         ▲
         │ registra
         │
┌─────────────────────────────────┐
│        AuditLog                 │
├─────────────────────────────────┤
│ - id: int                       │
│ - usuario_id: int               │
│ - tabla: string                 │
│ - operación: string             │
│ - registros_afectados: int      │
│ - fecha_hora: DateTime          │
│ - ip_origen: string             │
│ - resultado: string             │
├─────────────────────────────────┤
│ + registrar()                   │
│ + buscar()                      │
│ + generar_reporte()             │
└─────────────────────────────────┘
```

---

## Conclusiones

1. El proyecto **Emask** es viable desde perspectivas técnica, económica, operativa, legal y social.

2. La arquitectura propuesta combina seguridad a nivel de base de datos (RLS) con enmascaramiento dinámico en aplicación, proporcionando protección en múltiples capas.

3. Los requerimientos especificados son claro, medibles y se alinean con objetivos de negocio y regulaciones de protección de datos.

4. El modelo conceptual y lógico propuesto permite escalabilidad y mantenimiento adecuado del sistema.

5. La implementación de auditoría completa garantiza trazabilidad y cumplimiento de regulaciones.

6. Se ha definido claramente los perfiles de usuario y sus interacciones con el sistema.

---

## Recomendaciones

1. **Implementar en fases:** Comenzar con RLS y enmascaramiento básico antes de agregar funcionalidades avanzadas.

2. **Aprovechar características nativas:** PostgreSQL ofrece funcionalidades RLS nativas que deben maximizarse en lugar de implementar filtrado en aplicación.

3. **Seguridad en primer lugar:** Implementar validación de entrada, encriptación de conexiones (SSL/TLS) y auditoría desde las primeras iteraciones.

4. **Documentación continua:** Mantener documentación actualizada conforme el sistema evoluciona.

5. **Pruebas exhaustivas:** Realizar pruebas de seguridad, penetración y carga antes de producción.

6. **Capacitación de usuarios:** Proporcionar documentación y entrenamientos en manejo del sistema antes del despliegue.

7. **Plan de recuperación:** Establecer procedimientos de backup y recuperación ante fallos.

8. **Monitoreo:** Implementar herramientas de monitoreo para alertas en accesos sospechosos.

---

## Bibliografía

1. Griffiths, R. (2022). *PostgreSQL Administration Cookbook*. Packt Publishing.

2. PostgreSQL Global Development Group. (2025). *PostgreSQL 15 Documentation*. https://www.postgresql.org/docs/15

3. DePalma, D. A., & Sun, X. (2023). *Data Masking: A Comprehensive Guide*. Data Governance Quarterly.

4. OWASP Foundation. (2021). *OWASP Top 10 2021 - The Ten Most Critical Web Application Security Risks*.

5. Hernández, G., & López, M. (2023). *Seguridad de Bases de Datos: Control de Acceso Granular*. Editorial Académica.

6. Microsoft. (2024). *Dynamic Data Masking in SQL Server*. https://docs.microsoft.com

7. Summers, R. C. (2018). *Secure Coding: Principles and Practices*. Addison-Wesley.

8. Stallings, W., & Brown, L. (2022). *Computer Security: Principles and Practice* (4th ed.). Pearson.

---

## Webgrafía

1. PostgreSQL Official Documentation - Row Level Security  
   https://www.postgresql.org/docs/current/ddl-rowsecurity.html

2. NIST Cybersecurity Framework  
   https://www.nist.gov/cyberframework

3. OWASP - Authentication Cheat Sheet  
   https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html

4. GitHub - GitGuardian Public Dataset  
   https://github.com/gitguardian/

5. Auth0 - JSON Web Tokens (JWT)  
   https://auth0.com/docs/get-started/identity-fundamentals/json-web-tokens

6. Node.js Official Documentation  
   https://nodejs.org/en/docs/

7. React Official Documentation  
   https://react.dev/

8. SQLAlchemy Documentation (para ORM Python)  
   https://docs.sqlalchemy.org/

9. Express.js Guide  
   https://expressjs.com/

10. GDPR - General Data Protection Regulation  
    https://ec.europa.eu/info/law/law-topic/data-protection_en

---

**Documento preparado por:**  
Flores Navarro, Eduardo Gino  
Choqueña, Mauricio Adrian

**Fecha de elaboración:** 15 de marzo de 2026  
**Última modificación:** 01 de abril de 2026  
**Versión:** 2.0

---

*Este documento es propiedad de la Escuela Profesional de Ingeniería de Sistemas - Universidad Privada de Tacna.*