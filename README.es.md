# PayRetailers Python SDK

[English](README.md) | [Português](README.pt.md) | [Русский](README.ru.md) | [简体中文](README.zh.md)

SDK de Código Abierto (Open Source) en Python diseñado para agilizar la integración con **PayRetailers**. Hecho con amor para ayudarte a procesar pagos de forma rápida y segura.

Listo para producción, con validación de tipos y completamente documentado.

- **Repositorio Git**: [agentkyo/payretailers_python](https://github.com/agentkyo/payretailers_python)
- **Mantenedor**: agentkyo
- **Contacto**: caioviniciusxd@gmail.com | integrations@payretailers.com

---

## Características

- **Soporte Multi-País**: Clientes especializados para Brasil, México, Colombia, Chile, Argentina, Perú, Ecuador, Costa Rica y más.
- **Validación Inteligente**: Validación automática para IDs fiscales (CPF, CURP, RUT, etc.) y campos obligatorios.
- **Integración H2H**: Soporte integrado para transacciones Host-to-Host donde esté disponible.
- **Manejo Robusto de Errores**: Excepciones claras y reintentos automáticos para problemas de red.
- **Seguridad de Tipos**: Completamente tipado con modelos de Pydantic.
- **Gestión de Entornos**: Cambio fluido entre Sandbox y Producción.

## Instalación

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh

uv sync

uv run mexico.py // example 
```

## Inicio Rápido

### 1. Inicializar el Cliente

Selecciona el cliente especializado para tu país objetivo.

```python
from payretailers import PayRetailersMexico

# Inicializar para México (Sandbox)
client = PayRetailersMexico(
    shop_id="TU_SHOP_ID",
    secret_key="TU_SECRET_KEY",
    subscription_key="TU_SUBSCRIPTION_KEY",
    sandbox=True  # Establecer en False para Producción
)
```

### 2. Crear una Transacción

El SDK maneja los valores predeterminados de moneda y validación por ti.

```python
import uuid

try:
    transaction = client.create_transaction(
        amount=100.00,  # MXN por defecto para cliente de México
        description="Suscripción Premium",
        tracking_id=uuid.uuid4().hex,
        notification_url="https://tu-dominio.com/webhook",
        customer_email="cliente@ejemplo.com",
        customer_first_name="Juan",
        customer_last_name="Pérez",
        customer_personal_id="ABC123456789",  # CURP válido requerido
        payment_method_tag="OXXO"  # Opcional: Preseleccionar método de pago
    )

    print(f"Transacción Creada: {transaction.get('id')}")
    print(f"URL de Pago: {transaction.get('url')}")

except Exception as e:
    print(f"Error al crear la transacción: {e}")
```

### 3. Consultar Estado

```python
transaction_id = "TRANS_ID_DE_LA_RESPUESTA"
status = client.get_transaction(transaction_id)
print(f"Estado Actual: {status.get('status')}")
```

## Países Soportados

El SDK proporciona clases especializadas para configuraciones regionales predeterminadas:

| País | Clase | Moneda Predeterminada |
| :--- | :--- | :--- |
| **Brasil** | `PayRetailersBrazil` | BRL |
| **México** | `PayRetailersMexico` | MXN |
| **Chile** | `PayRetailersChile` | CLP |
| **Colombia** | `PayRetailersColombia` | COP |
| **Argentina** | `PayRetailersArgentina` | ARS |
| **Perú** | `PayRetailersPeru` | PEN |
| **Ecuador** | `PayRetailersEcuador` | USD |

Para otros países, usa `PayRetailersCountryClient` con los enums específicos.

## Uso Avanzado

### Anular Moneda
Puedes procesar transacciones en otras monedas (ej. USD) independientemente del cliente del país.

```python
transaction = client.create_transaction(
    amount=50.00,
    currency="USD",
    # ... otros campos
)
```

### Integración H2H (Host-to-Host)
El SDK intenta automáticamente obtener información de aterrizaje H2H para los métodos de pago soportados en Producción. Si está disponible, claves como `bank_account` o `pdf_link` estarán presentes en la respuesta bajo `h2h`.

---

Hecho con ♥ por Caio Vinicius.
