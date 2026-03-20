# 💊 FarmaView B2B - SaaS Management System

![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-00000F?style=for-the-badge&logo=mysql&logoColor=white)
![Bootstrap 5](https://img.shields.io/badge/Bootstrap-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white)
![SaaS](https://img.shields.io/badge/Architecture-SaaS_Multi--Tenant-blueviolet?style=for-the-badge)

**FarmaView** es una plataforma integral de gestión comercial diseñada específicamente para el sector farmacéutico y médico. Permite a las organizaciones administrar fuerzas de ventas, catálogos de productos, analítica gerencial y órdenes B2B en un entorno seguro, profesional y altamente escalable.

---

## 1. Características Principales

### 📊 Analítica Gerencial Proactiva
- Visualización de ingresos reales y proyectados mediante gráficos dinámicos (**Chart.js**).
- Seguimiento de cumplimiento de metas por representante comercial.
- Reportes anuales y comparativas históricas de crecimiento.

### 👥 Gestión de Equipo (RRHH)
- Control total sobre el acceso de usuarios (Gerentes y Vendedores).
- Nómina de integrantes con perfiles personalizables y estados activos/inactivos.
- Seguridad robusta basada en roles de usuario y permisos granulares.

### 📦 Catálogo y Órdenes B2B
- Gestión de inventario con SKUs únicos y control de stock.
- Carrito de compras en tiempo real para generar órdenes de transferencia rápidas.
- Soporte para carga masiva de productos y metas mediante archivos CSV/Excel.

### 🌍 Internacionalización (i18n)
- Sistema 100% bilingüe (**Español / Inglés**) integrado mediante `django.utils.translation`.
- Soporte dinámico para cambio de moneda, placeholders y formatos regionales.

---

## 2. Arquitectura Técnica: SaaS Multi-Tenant

El proyecto está diseñado para ser escalable bajo un modelo de **SaaS (Software as a Service)** con aislamiento total de datos para garantizar la privacidad de cada cliente:

- **Estructura de Datos:** Bases de Datos separadas por cliente (Multi-DB) para máxima seguridad y cumplimiento normativo.
- **Enrutamiento Dinámico:** Uso de `TenantMiddleware` para identificar clientes automáticamente a través de subdominios dinámicos (ej: `veterinaria.farmaview.cl`).
- **Backend:** Django 4.x con lógica de **Database Routers** personalizada para conmutación de conexiones en tiempo real según el host de la petición.
- **Frontend:** Interfaz moderna, limpia y responsiva construida con HTML5, CSS3 y Bootstrap 5.

---

## 3. Instalación y Desarrollo Local

Sigue estos pasos para configurar el entorno de desarrollo en tu máquina local:

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/tu-usuario/farmaview.git
   cd farmaview
   ```

2. **Configurar el entorno virtual:**
   ```bash
   # En Windows:
   python -m venv venv
   venv\Scripts\activate

   # En Linux/Mac:
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Compilar archivos de traducción:**
   ```bash
   python manage.py compilemessages
   ```

5. **Ejecutar migraciones y servidor:**
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

---

## 🌐 Despliegue en Producción (Recomendado)

Para garantizar un rendimiento óptimo en un entorno multi-cliente con alta concurrencia, se sugiere la siguiente infraestructura:

- **Infraestructura:** Cloud VPS (Se recomienda un plan con al menos 8GB RAM / 4 vCPUs para manejar múltiples conexiones MySQL).
- **Sistema Operativo:** Ubuntu 22.04 LTS o 24.04 LTS.
- **Servidor Web:** Nginx actuando como Reverse Proxy con certificados SSL (Cloudflare recomendado para gestión de Wildcard DNS `*.tuapp.com`).
- **App Server:** Gunicorn para el manejo de procesos Django.
- **Base de Datos:** MySQL 8.0 optimizado para múltiples esquemas independientes.

---

## ✒️ Autor
* **Polet Arenas** - *Arquitecto de Software & Desarrollador Fullstack* - [Tu LinkedIn](https://linkedin.com/in/poletarenas)

---
© 2026 FarmaView | Todos los derechos reservados.
