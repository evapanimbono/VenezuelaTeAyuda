# 🇻🇪 VenezuelaTeAyuda - Backend & API REST

Plataforma backend desarrollada en **Python** y **Django REST Framework (DRF)** orientada a la intermediación laboral y conexión entre candidatos y empresas en Venezuela. Proporciona una arquitectura de servicios web para la gestión de usuarios, perfiles profesionales, publicación de ofertas de empleo y seguimiento de postulaciones.

---

## 🛠️ Tech Stack & Arquitectura

- **Lenguaje:** Python 3.x
- **Framework Backend:** Django 5.x
- **API Framework:** Django REST Framework (DRF)
- **Autenticación:** DRF Token Authentication (`rest_framework.authtoken`)
- **Base de Datos:** SQLite (Desarrollo local) / Compatible con PostgreSQL
- **Control de Versiones:** Git & GitHub

---

## 📌 Módulos y Modelos de Datos (`empleos`)

El sistema cuenta con una arquitectura modular enfocada en la gestión de empleo:

- **`CandidatoProfile`:** Gestión de perfiles de solicitantes de empleo (datos de contacto, CV en PDF/Word, nivel educativo, habilidades y estado de búsqueda).
- **`EmpresaProfile`:** Registro y verificación de empresas reclutadoras (RIF, sector industrial, dirección física y contacto).
- **`OfertaEmpleo`:** Publicación y categorización de vacantes (modalidad laboral, ubicación por Estado/Municipio, rango salarial y requisitos).
- **`Postulacion`:** Flujo completo de solicitudes de empleo con estados dinámicos (*Postulado*, *En Revisión*, *Aceptado*, *Rechazado*).

---

## 🚀 Endpoints Principales de la API

### 🔐 Autenticación y Cuentas
- `POST /api/empleos/registro/candidato/` — Registro de nuevos candidatos.
- `POST /api/empleos/registro/empresa/` — Registro de perfil empresa.
- `POST /api/empleos/login/` — Autenticación y generación de Token de acceso.

### 👤 Perfiles
- `GET / PUT /api/empleos/perfil/candidato/` — Consulta y actualización del perfil del candidato (soporta subida de CV).
- `GET / PUT /api/empleos/perfil/empresa/` — Consulta y actualización del perfil de empresa.

### 💼 Ofertas y Postulaciones
- `GET / POST /api/empleos/ofertas/` — Listar ofertas públicas y crear nuevas vacantes (Empresas).
- `GET /api/empleos/mis-ofertas/` — Consultar vacantes creadas por la empresa autenticada.
- `POST /api/empleos/ofertas/<id>/postular/` — Enviar postulación a una vacante activa.
- `GET /api/empleos/mis-postulaciones/` — Historial de postulaciones del candidato.
- `GET /api/empleos/ofertas/<id>/postulaciones/` — Revisar candidatos postulados a una oferta.
- `PATCH /api/empleos/postulaciones/<id>/estado/` — Actualizar el estado de una postulación.

---

## 💻 Instalación y Ejecución Local

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

### 4. Aplicar migraciones y ejecutar servidor
python gestionar.py migrate

python gestionar.py runserver

Abre http://127.0.0.1:8000/ en tu navegador.

---

## ✒️ Autora

* **Eva Panimbono** - *Software Engineer / Full-Stack Developer* - [GitHub](https://github.com/evapanimbono) | [LinkedIn](https://www.linkedin.com/in/evapanimbono)

