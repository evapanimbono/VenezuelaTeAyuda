# 🤝 Venezuela Te Ayuda

![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![NeonDB](https://img.shields.io/badge/Neon_Serverless_Postgres-00E599?style=for-the-badge&logo=postgresql&logoColor=black)
![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)

Plataforma web desarrollada en Django dedicada a la gestión de oportunidades laborales y recursos de apoyo comunitario.

---

## 🚀 Características Principales

* **Módulo de Empleos (`empleos`):** Publicación, consulta y gestión de ofertas de trabajo y postulaciones.
* **Persistencia en la Nube:** Conexión a base de datos relacional PostgreSQL hospedada en **Neon Serverless Postgres**.
* **Panel de Control:** Administración de solicitudes y contenidos a través de Django Admin.

---

## 🛠️ Estructura del Proyecto

* **`config/`**: Módulo principal del proyecto (configuración general, URLs base y WSGI/ASGI).
* **`empleos/`**: Aplicación encargada del modelo de datos, vistas y lógica de negocio para las ofertas.
* **`manage.py`**: Script de gestión de comandos de Django.

---

## ⚙️ Configuración e Instalación Local

Sigue estos pasos para ejecutar el proyecto en tu equipo:

### 1. Clonar el repositorio

    git clone https://github.com/evapanimbono/VenezuelaTeAyuda.git
    cd VenezuelaTeAyuda

### 2. Crear y activar el entorno virtual

    python -m venv venv

En Linux/macOS:

    source venv/bin/activate

En Windows:

    venv\Scripts\activate

### 3. Instalar dependencias

    pip install -r requirements.txt

### 4. Configurar variables de entorno (.env)

Crea un archivo `.env` en la raíz del proyecto y añade tus credenciales de conexión:

    SECRET_KEY=tu_secret_key_de_django
    DEBUG=True
    DATABASE_URL=postgresql://usuario:password@host/neondb?sslmode=require

### 5. Aplicar migraciones y ejecutar servidor

    python manage.py migrate
    python manage.py runserver

Abre http://127.0.0.1:8000/ en tu navegador.

---

## ✒️ Autora

* **Eva Panimbono** - *Software Engineer / Full-Stack Developer* - [GitHub](https://github.com/evapanimbono) | [LinkedIn](https://www.linkedin.com/in/evapanimbono)
