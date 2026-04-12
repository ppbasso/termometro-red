# Termómetro RED (Transantiago) Data Pipeline & API 🚌📊

Plataforma de orquestación de datos End-to-End diseñada para ingerir telemetría de transporte público en tiempo real, persistirla en un Data Warehouse en la nube y exponerla a través de una API RESTful corporativa, facilitando la toma de decisiones y el análisis de movilidad urbana.

## 🎯 El Problema de Negocio
Las agencias de transporte público generan enormes volúmenes de telemetría (ubicación de la flota, tiempos estimados de llegada). Sin embargo, acceder a estos datos crudos en tiempo real suele implicar conectarse a APIs públicas inestables, con límites de peticiones (Rate Limiting) y formatos inconsistentes (Tokens dinámicos). 

Esta falta de centralización y estandarización dificulta la creación de sistemas analíticos internos (Dashboards) o la integración con microservicios de terceros que requieren alta disponibilidad y baja latencia.

## 💡 La Solución (Arquitectura N-Tier Estricta)
Se diseñó una arquitectura desacoplada en tres fases para garantizar resiliencia, seguridad y escalabilidad:

1.  **Ingesta Automatizada (ETL Serverless):** Un worker programado en **GitHub Actions** ejecuta un script Python que consume la API de PredictorPlus del gobierno. Este script actúa como un cliente HTTP puro: extrae, limpia y envía la telemetría validada hacia nuestra API corporativa mediante peticiones `POST`.
2.  **Exposición y Lógica de Negocio (Backend API):** Se construyó una API REST en **Java Spring Boot 2.7** (desplegada en Hugging Face) que actúa como el único punto de entrada y salida de datos. Implementa controladores (`@RestController`) para recibir la data de Python y exponerla al frontend.
3.  **Capa de Almacenamiento Cloud:** El backend de Java implementa el patrón de diseño Repository mediante Hibernate/JPA para persistir y consultar los datos de forma segura en **PostgreSQL (Neon.tech)**, aislando por completo la base de datos del mundo exterior.

> *Visualización Dashboard Analítico*
<br>
*(Link a Streamlit Cloud - Despliegue Activo)*

## 🏗️ Arquitectura de Alto Nivel

~~~text
[API PredictorPlus RED] 
       | (Petición HTTP GET + JWT Token)
       v
[GitHub Actions (Python ETL)] ---> Extrae, Limpia y Estructura la telemetría
       |
       | (Petición HTTP POST / JSON Payload)
       v
[Java Spring Boot 2.7 API] <---> (Hibernate ORM) <---> [Neon.tech (PostgreSQL)]
  (Hugging Face Space)                                  Data Warehouse Central
       |
       | (Petición HTTP GET / JSON)
       v
[Streamlit Community Cloud] ---> Dashboard Analítico Front-End
~~~

## 🧠 Características Técnicas Destacadas
* **Arquitectura Multicapa (N-Tier) Estricta:** El script de ingesta (Python) no tiene acceso ni credenciales de la base de datos. Se comunica exclusivamente a través de la API REST de Java, delegando la responsabilidad de persistencia y seguridad al backend.
* **Mapeo Objeto-Relacional (ORM):** Uso de `Hibernate` para abstraer la persistencia. La base de datos es tratada como objetos Java (`@Entity`), eliminando vulnerabilidades de inyección SQL y acoplamiento.
* **Orquestación Serverless & Cloud:** Despliegue 100% en la nube sin gestión de servidores locales. GitHub Actions para el ETL cíclico, Hugging Face Spaces para el contenedor Docker de Spring Boot, Neon para DB y Streamlit Cloud para el frontend.
* **Resiliencia ante APIs Inestables:** El script de ingesta incluye validación de tipos de datos, captura de respuestas crudas y prevención de errores HTTP 405/500, garantizando estabilidad ante caídas de los servicios gubernamentales.

## 🛠️ Stack Tecnológico
* **Ingesta (Data Engineering):** Python 3.10+, `requests`, `python-dotenv`, GitHub Actions (CI/CD Cron).
* **Backend (API Provider):** Java 11, Spring Boot 2.7 (Web, Data JPA), Maven Wrapper, Hugging Face Spaces.
* **Almacenamiento (Database):** PostgreSQL serverless (Neon.tech).
* **Frontend (Visualización):** Python, Streamlit Community Cloud, Pandas.