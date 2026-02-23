# PayRetailers Python SDK

[Español](README.es.md) | [Português](README.pt.md) | [Русский](README.ru.md) | [简体中文](README.zh.md)

Open Source Python SDK designed to streamline integration with **PayRetailers**. Built with love to help you process payments quickly and securely.

Production-ready, type-safe, and fully documented.

- **Git Repository**: [agentkyo/payretailers_python](https://github.com/agentkyo/payretailers_python)
- **Maintainer**: agentkyo
- **Contact**: caioviniciusxd@gmail.com | integrations@payretailers.com

---

## Features

- **Multi-Country Support**: Specialized clients for Brazil, Mexico, Colombia, Chile, Argentina, Peru, Ecuador, Costa Rica, and more.
- **Smart Validation**: Automatic validation for tax IDs (CPF, CURP, RUT, etc.) and required fields.
- **H2H Integration**: Built-in support for Host-to-Host transactions where available.
- **Robust Error Handling**: Clear exceptions and automatic retries for network issues.
- **Type Safety**: Fully typed with Pydantic models.
- **Environment Management**: Seamless switch between Sandbox and Production.

## Installation

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh

uv sync

uv run brazil.py // example 
```

## Quick Start

### 1. Initialize the Client

Select the specialized client for your target country.

```python
from payretailers import PayRetailersBrazil

# Initialize for Brazil (Sandbox)
client = PayRetailersBrazil(
    shop_id="YOUR_SHOP_ID",
    secret_key="YOUR_SECRET_KEY",
    subscription_key="YOUR_SUBSCRIPTION_KEY",
    sandbox=True  # Set False for Production
)
```

### 2. Create a Transaction

The SDK handles currency defaults and validation for you.

```python
import uuid

try:
    transaction = client.create_transaction(
        amount=100.00,  # BRL by default for Brazil client
        description="Premium Subscription",
        tracking_id=uuid.uuid4().hex,
        notification_url="https://your-domain.com/webhook",
        customer_email="customer@example.com",
        customer_first_name="John",
        customer_last_name="Doe",
        customer_personal_id="123.456.789-00",  # Valid CPF required
        payment_method_tag="PIX"  # Optional: Pre-select payment method
    )

    print(f"Transaction Created: {transaction.get('id')}")
    print(f"Checkout URL: {transaction.get('url')}")

except Exception as e:
    print(f"Error creating transaction: {e}")
```

### 3. Check Status

```python
transaction_id = "TRANS_ID_FROM_RESPONSE"
status = client.get_transaction(transaction_id)
print(f"Current Status: {status.get('status')}")
```

## Supported Countries

The SDK provides specialized classes for specific regional defaults:

| Country | Class | Default Currency |
| :--- | :--- | :--- |
| **Brazil** | `PayRetailersBrazil` | BRL |
| **Mexico** | `PayRetailersMexico` | MXN |
| **Chile** | `PayRetailersChile` | CLP |
| **Colombia** | `PayRetailersColombia` | COP |
| **Argentina** | `PayRetailersArgentina` | ARS |
| **Peru** | `PayRetailersPeru` | PEN |
| **Ecuador** | `PayRetailersEcuador` | USD |

For other countries, use `PayRetailersCountryClient` with specific enums.

## Advanced Usage

### Currency Override
You can process transactions in other currencies (e.g., USD) regardless of the country client.

```python
transaction = client.create_transaction(
    amount=50.00,
    currency="USD",
    # ... other fields
)
```

### H2H Integration (Host-to-Host)
The SDK automatically attempts to fetch H2H landing information for supported payment methods in Production. If available, keys like `bank_account` or `pdf_link` will be present in the response under `h2h`.

---

## Sandbox Response Examples

### Brazil (BRL)
**Transaction:**
```json
{"uid": "...", "status": "PENDING", "amount": 1000, "currency": "BRL", "paymentMethod": {"name": "PIX", "paymentMethodTag": "PIX"}}
```
**Paywall:**
```json
{"uid": "...", "amount": 1500, "currency": "BRL", "totalAmount": 15, "form": {"action": "https://api-sandbox.payretailers.com/payments/v2/public/paywalls/landing/..."}}
```

### Mexico (MXN)
**Transaction:**
```json
{"uid": "...", "status": "PENDING", "amount": 1000, "currency": "USD", "billing": {"currency": "MXN", "amount": 1000}}
```

### Colombia (COP)
**Transaction:**
```json
{"uid": "...", "status": "PENDING", "amount": 10000, "currency": "COP"}
```

### Chile (CLP)
**Transaction:**
```json
{"uid": "...", "status": "PENDING", "amount": 1000, "currency": "CLP"}
```

### Argentina (ARS)
**Transaction:**
```json
{"uid": "...", "status": "PENDING", "amount": 1000, "currency": "ARS"}
```

### Peru (PEN)
**Transaction:**
```json
{"uid": "...", "status": "PENDING", "amount": 1000, "currency": "PEN"}
```

### Ecuador (USD)
**Transaction:**
```json
{"uid": "...", "status": "FAILED", "message": "TRANSACTION_MIN_AMOUNT", "currency": "USD"}
```

---

Made with ♥ by Caio Vinicius.
