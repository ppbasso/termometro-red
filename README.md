# Termómetro RED (Transantiago) Data Pipeline & API 🚌📊

Plataforma de orquestación de datos End-to-End diseñada para ingerir telemetría de transporte público en tiempo real, persistirla en un Data Warehouse en la nube y exponerla a través de una API RESTful corporativa, facilitando la toma de decisiones y el análisis de movilidad urbana.

## 🎯 El Problema de Negocio
Las agencias de transporte público generan enormes volúmenes de telemetría (ubicación de la flota, tiempos estimados de llegada). Sin embargo, acceder a estos datos crudos en tiempo real suele implicar conectarse a APIs públicas inestables, con límites de peticiones (Rate Limiting) y formatos inconsistentes. 

Esta falta de centralización y estandarización dificulta la creación de sistemas analíticos internos (Dashboards) o la integración con microservicios de terceros que requieren alta disponibilidad y baja latencia.

## 💡 La Solución (Arquitectura N-Tier)
Se diseñó una arquitectura desacoplada en tres fases para garantizar resiliencia y escalabilidad:

1.  **Ingesta Automatizada (ETL Cíclico):** Un worker programado en **GitHub Actions** ejecuta un script Python que consume la API del Directorio de Transporte Público Metropolitano (DTPM), extrae los datos clave y los inyecta en una bóveda centralizada.
2.  **Capa de Almacenamiento Cloud:** Los datos persisten en **PostgreSQL (Neon.tech)**, asegurando integridad relacional y disponibilidad 24/7.
3.  **Exposición Corporativa (Backend):** Se construyó una API REST en **Java Spring Boot 2.7** que actúa como una capa de abstracción. Este backend implementa el patrón de diseño Repository mediante Hibernate/JPA, protegiendo la base de datos de peticiones masivas y sirviendo la información en un formato JSON estandarizado para cualquier cliente frontend o servicio de BI.

> *Visualización Dashboard Auditoría*
<br>
[IMAGEN PENDIENTE: Agregaremos el GIF del Dashboard aquí mañana]

## 🏗️ Arquitectura de Alto Nivel

~~~text
[API Pública RED/Transantiago] 
       | (Petición HTTP GET)
       v
[GitHub Actions (Python ETL)] ---> Extrae, Limpia y Estructura la telemetría
       |
       | (Librería Psycopg2 / SQL Insert)
       v
[Neon.tech (PostgreSQL)] <--- Data Warehouse Operativo (Bóveda Central)
       ^
       | (Spring Data JPA / Hibernate ORM)
       v
[Java Spring Boot 2.7 (REST API)] ---> Capa de Lógica y Exposición (Puerto 8080)
       |
       | (Petición HTTP GET / JSON)
       v
[Streamlit Cloud] ---> Dashboard Analítico Front-End
~~~

## 🧠 Características Técnicas Destacadas
* **Arquitectura Multicapa (N-Tier):** Separación estricta de responsabilidades. La lógica de ingesta (Python) no conoce la lógica de exposición (Java), permitiendo escalar cada servicio de forma independiente.
* **Mapeo Objeto-Relacional (ORM):** Uso de `Hibernate` para abstraer la persistencia. La base de datos es tratada como objetos Java (`@Entity`), eliminando las vulnerabilidades de inyección SQL y el acoplamiento de código.
* **Orquestación Serverless:** Eliminación de servidores de infraestructura para la ingesta. El cron job se gestiona de forma nativa mediante la sintaxis YAML de GitHub Actions.
* **Resolución de Conflictos de Encoding:** Gestión a nivel de scripting (PowerShell) para asegurar compilaciones limpias en entornos Windows (eliminación de BOM UTF-8), garantizando portabilidad cross-platform del código fuente.

## 🛠️ Stack Tecnológico
* **Ingesta (Data Engineering):** Python 3.10+, `psycopg2`, GitHub Actions (CI/CD Cron).
* **Almacenamiento (Database):** PostgreSQL (Neon.tech).
* **Backend (API Provider):** Java 11, Spring Boot 2.7 (Web, Data JPA), Maven Wrapper.
* **Frontend (Visualización):** Streamlit, Pandas.