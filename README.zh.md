# PayRetailers Python SDK

[English](README.md) | [Español](README.es.md) | [Português](README.pt.md) | [Русский](README.ru.md)

专为简化 **PayRetailers** 集成而设计的开源 Python SDK。用心打造，助您快速安全地处理支付。

生产就绪，类型安全，文档齐全。

- **Git 仓库**: [agentkyo/payretailers_python](https://github.com/agentkyo/payretailers_python)
- **维护者**: agentkyo
- **联系方式**: caioviniciusxd@gmail.com | integrations@payretailers.com

---

## 功能特性

- **多国支持**: 专为巴西、墨西哥、哥伦比亚、智利、阿根廷、秘鲁、厄瓜多尔、哥斯达黎加等国定制的客户端。
- **智能验证**: 自动验证税务 ID（CPF, CURP, RUT 等）和必填字段。
- **H2H 集成**: 内置支持 Host-to-Host 交易（如可用）。
- **强大的错误处理**: 清晰的异常处理和网络问题的自动重试。
- **类型安全**: 基于 Pydantic 模型构建，完全类型化。
- **环境管理**: 无缝切换沙盒（Sandbox）和生产（Production）环境。

## 安装

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh

uv sync

uv run brazil.py // example 
```

## 快速开始

### 1. 初始化客户端

选择适合您目标国家的专用客户端。

```python
from payretailers import PayRetailersBrazil

# 初始化巴西客户端 (Sandbox)
client = PayRetailersBrazil(
    shop_id="YOUR_SHOP_ID",
    secret_key="YOUR_SECRET_KEY",
    subscription_key="YOUR_SUBSCRIPTION_KEY",
    sandbox=True  # 生产环境请设为 False
)
```

### 2. 创建交易

SDK 会为您处理默认货币和验证。

```python
import uuid

try:
    transaction = client.create_transaction(
        amount=100.00,  # 巴西客户端默认为 BRL
        description="高级订阅",
        tracking_id=uuid.uuid4().hex,
        notification_url="https://your-domain.com/webhook",
        customer_email="customer@example.com",
        customer_first_name="John",
        customer_last_name="Doe",
        customer_personal_id="123.456.789-00",  # 需要有效的 CPF
        payment_method_tag="PIX"  # 可选：预选支付方式
    )

    print(f"交易已创建: {transaction.get('id')}")
    print(f"支付链接: {transaction.get('url')}")

except Exception as e:
    print(f"创建交易失败: {e}")
```

### 3. 查询状态

```python
transaction_id = "TRANS_ID_FROM_RESPONSE"
status = client.get_transaction(transaction_id)
print(f"当前状态: {status.get('status')}")
```

## 支持的国家

SDK 为特定区域默认设置提供了专用类：

| 国家 | 类 | 默认货币 |
| :--- | :--- | :--- |
| **巴西** | `PayRetailersBrazil` | BRL |
| **墨西哥** | `PayRetailersMexico` | MXN |
| **智利** | `PayRetailersChile` | CLP |
| **哥伦比亚** | `PayRetailersColombia` | COP |
| **阿根廷** | `PayRetailersArgentina` | ARS |
| **秘鲁** | `PayRetailersPeru` | PEN |
| **厄瓜多尔** | `PayRetailersEcuador` | USD |

对于其他国家，请使用 `PayRetailersCountryClient` 并指定相应的枚举（Enum）。

## 高级用法

### 覆盖货币
您可以独立于国家客户端，使用其他货币（如 USD）处理交易。

```python
transaction = client.create_transaction(
    amount=50.00,
    currency="USD",
    # ... 其他字段
)
```

### H2H 集成 (Host-to-Host)
SDK 会自动尝试在生产环境中获取支持支付方式的 H2H 落地信息。如果可用，`bank_account` 或 `pdf_link` 等键将出现在响应的 `h2h` 字段下。

---

## 沙盒 (Sandbox) 响应示例

### 巴西 (BRL)
**交易:**
```json
{"uid": "...", "status": "PENDING", "amount": 1000, "currency": "BRL", "paymentMethod": {"name": "PIX", "paymentMethodTag": "PIX"}}
```
**Paywall:**
```json
{"uid": "...", "amount": 1500, "currency": "BRL", "totalAmount": 15, "form": {"action": "https://api-sandbox.payretailers.com/payments/v2/public/paywalls/landing/..."}}
```

### 墨西哥 (MXN)
**交易:**
```json
{"uid": "...", "status": "PENDING", "amount": 1000, "currency": "USD", "billing": {"currency": "MXN", "amount": 1000}}
```

### 哥伦比亚 (COP)
**交易:**
```json
{"uid": "...", "status": "PENDING", "amount": 10000, "currency": "COP"}
```

### 智利 (CLP)
**交易:**
```json
{"uid": "...", "status": "PENDING", "amount": 1000, "currency": "CLP"}
```

### 阿根廷 (ARS)
**交易:**
```json
{"uid": "...", "status": "PENDING", "amount": 1000, "currency": "ARS"}
```

### 秘鲁 (PEN)
**交易:**
```json
{"uid": "...", "status": "PENDING", "amount": 1000, "currency": "PEN"}
```

### 厄瓜多尔 (USD)
**交易:**
```json
{"uid": "...", "status": "FAILED", "message": "TRANSACTION_MIN_AMOUNT", "currency": "USD"}
```

---

由 Caio Vinicius 用 ♥ 制作。
