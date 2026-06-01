# SGV – Sistema de Gestión de Ventas

Aplicación de escritorio para la gestión integral de ventas, inventario, clientes, caja y reportes. Desarrollada en Python con Flet y SQLite.

---

## Equipo de desarrollo

| Integrante | Rol |
|---|---|
| Adrian Carmona | Desarrollo |
| Manuel Pianeta | Desarrollo |
| Libardo Morales | Desarrollo |
| Ramiro Rangel | Desarrollo |

**Institución:** Corporación Universitaria Americana – Ingeniería de Sistemas  
**Año:** 2026

---

## Repositorio

```
https://github.com/josevc12/sgv_final.git
```

---

## Stack tecnológico

| Tecnología | Versión | Rol |
|---|---|---|
| Python | 3.12+ | Lenguaje principal |
| Flet | 0.28.3 | Framework de UI (desktop) |
| flet-cli | 0.28.3 | CLI de Flet |
| flet-desktop | 0.28.3 | Runtime de escritorio |
| flet-web | 0.28.3 | Módulo web de Flet |
| SQLite | 3.x (stdlib) | Base de datos embebida |
| ReportLab | 4.x | Generación de PDFs |

---

## Requisitos previos

- Python 3.12 o superior instalado
- pip actualizado

---

## Instalación y ejecución

**1. Clonar el repositorio**

```bash
git clone https://github.com/josevc12/sgv_final.git
cd sgv_final
```

**2. Instalar dependencias**

```bash
pip install flet==0.28.3 flet-cli==0.28.3 flet-desktop==0.28.3 flet-web==0.28.3 reportlab
```

**3. Ejecutar la aplicación**

```bash
python main.py
```

**Credenciales por defecto**

```
Usuario:    admin
Contraseña: admin123
```

> Se recomienda cambiar la contraseña del administrador tras el primer inicio de sesión.

---

## Estructura del proyecto

```
sgv_final/
├── main.py                         # Punto de entrada
├── sgv.db                          # Base de datos SQLite (se genera automáticamente)
└── app/
    ├── config.py                   # Constantes globales (rutas, colores, dimensiones)
    ├── access.py                   # Control de acceso por rol
    ├── router.py                   # Enrutador central de vistas
    ├── main_app.py                 # Configuración de la página Flet
    ├── ui_compat.py                # Compatibilidad entre versiones de Flet
    ├── db/
    │   ├── connection.py           # Factory de conexiones SQLite
    │   └── init_db.py              # Inicialización del esquema y datos semilla
    ├── repositories/
    │   ├── audit_repository.py     # Auditoría
    │   ├── caja_repository.py      # Caja
    │   ├── clients_repository.py   # Clientes
    │   ├── inventory_repository.py # Movimientos de inventario
    │   ├── invoices_repository.py  # Facturas
    │   ├── products_repository.py  # Productos
    │   ├── sales_repository.py     # Ventas y detalle
    │   ├── settings_repository.py  # Configuración de la app
    │   └── users_repository.py     # Usuarios
    ├── services/
    │   ├── auth_service.py         # Autenticación y sesión
    │   ├── backup_service.py       # Copia de seguridad de la BD
    │   ├── client_service.py       # Lógica de negocio – clientes
    │   ├── inventory_service.py    # Lógica de negocio – inventario
    │   ├── invoice_service.py      # Lógica de negocio – facturas
    │   ├── product_service.py      # Lógica de negocio – productos
    │   ├── sales_service.py        # Lógica de negocio – ventas
    │   └── user_service.py         # Lógica de negocio – usuarios
    └── views/
        ├── login_view.py           # Pantalla de inicio de sesión
        ├── dashboard_view.py       # Panel principal con métricas
        ├── products_view.py        # Gestión de productos
        ├── clients_view.py         # Gestión de clientes
        ├── inventory_view.py       # Control de inventario
        ├── pos_view.py             # Punto de Venta (POS)
        ├── invoices_view.py        # Gestión de facturas
        ├── caja_view.py            # Apertura y cierre de caja
        ├── reports_view.py         # Reportes y estadísticas
        ├── users_view.py           # Administración de usuarios
        └── shared.py               # Componentes UI reutilizables
```

---

## Arquitectura

El proyecto sigue una **arquitectura en capas** estricta:

```
[ UI – Views ]
      ↓
[ Services ]
      ↓
[ Repositories ]
      ↓
[ SQLite – sgv.db ]
```

Ninguna vista accede directamente a la base de datos. Todo fluye a través de los servicios y repositorios correspondientes.

---

## Módulos principales del sistema

**`app/router.py`** – Controla la navegación entre vistas y verifica permisos antes de renderizar cualquier pantalla protegida.

**`app/access.py`** – Define los permisos por rol mediante el diccionario `ROLE_ACCESS`. Roles disponibles: `administrador`, `cajero`, `supervisor`.

**`app/db/init_db.py`** – Crea las 9 tablas del esquema al arrancar. Usa `CREATE TABLE IF NOT EXISTS` para ser idempotente. Gestiona migraciones no destructivas con `_ensure_column()`.

**`app/services/auth_service.py`** – Autenticación con hash SHA-256. Registra todos los intentos de login (exitosos y fallidos) en auditoría.

**`app/services/sales_service.py`** – Procesa una venta completa en una sola transacción: crea la venta, inserta el detalle, descuenta el stock con movimiento de inventario y genera la factura automáticamente. IVA aplicado: 19%.

**`app/services/backup_service.py`** – Crea copias de seguridad de `sgv.db` en la carpeta `backups/` con timestamp en el nombre del archivo.

---

## Base de datos

| Tabla | Descripción |
|---|---|
| `usuarios` | Usuarios del sistema con rol y contraseña cifrada |
| `clientes` | Clientes registrados (incluye Consumidor Final por defecto) |
| `productos` | Catálogo de productos con precios y control de stock |
| `movimientos_inventario` | Trazabilidad completa de cada cambio de stock |
| `ventas` | Cabecera de cada venta realizada |
| `detalle_venta` | Líneas de productos por venta |
| `facturas` | Factura generada automáticamente por cada venta |
| `caja` | Registro de aperturas y cierres de caja |
| `auditoria` | Log de todos los eventos del sistema |

La base de datos se genera automáticamente en la primera ejecución. No requiere configuración adicional.

---

## Buenas prácticas aplicadas

- Consultas SQL parametrizadas en todas las operaciones (prevención de SQL Injection)
- Baja lógica para usuarios y productos (no se eliminan físicamente)
- Trazabilidad completa: cada operación crítica queda registrada en auditoría
- Configuración centralizada en `config.py` (principio DRY)
- Componentes UI reutilizables en `shared.py` (principio DRY)
- Migraciones no destructivas con `_ensure_column()`
- Transacciones atómicas en operaciones críticas (ventas, inventario)
- Control de acceso por rol antes de renderizar cualquier vista protegida
