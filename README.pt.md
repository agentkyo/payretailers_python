# PayRetailers Python SDK

[English](README.md) | [Español](README.es.md) | [Русский](README.ru.md) | [简体中文](README.zh.md)

SDK Python Open Source projetado para agilizar a integração com a **PayRetailers**. Feito com amor para ajudar você a processar pagamentos de forma rápida e segura.

Pronto para produção, type-safe e totalmente documentado.

- **Repositório Git**: [agentkyo/payretailers_python](https://github.com/agentkyo/payretailers_python)
- **Mantenedor**: agentkyo
- **Contato**: caioviniciusxd@gmail.com | integrations@payretailers.com

---

## Funcionalidades

- **Suporte Multi-País**: Clientes especializados para Brasil, México, Colômbia, Chile, Argentina, Peru, Equador, Costa Rica e mais.
- **Validação Inteligente**: Validação automática para IDs fiscais (CPF, CURP, RUT, etc.) e campos obrigatórios.
- **Integração H2H**: Suporte embutido para transações Host-to-Host onde disponível.
- **Tratamento Robusto de Erros**: Exceções claras e retentativas automáticas para problemas de rede.
- **Segurança de Tipos**: Totalmente tipado com modelos Pydantic.
- **Gerenciamento de Ambientes**: Mudança simples entre Sandbox e Produção.

## Instalação

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh

uv sync

uv run brazil.py // example 
```

## Começo Rápido

### 1. Inicializar o Cliente

Selecione o cliente especializado para seu país alvo.

```python
from payretailers import PayRetailersBrazil

# Inicializar para Brasil (Sandbox)
client = PayRetailersBrazil(
    shop_id="SEU_SHOP_ID",
    secret_key="SUA_SECRET_KEY",
    subscription_key="SUA_SUBSCRIPTION_KEY",
    sandbox=True  # Defina como False para Produção
)
```

### 2. Criar uma Transação

O SDK lida com os padrões de moeda e validação para você.

```python
import uuid

try:
    transaction = client.create_transaction(
        amount=100.00,  # BRL por padrão para o cliente Brasil
        description="Assinatura Premium",
        tracking_id=uuid.uuid4().hex,
        notification_url="https://seu-dominio.com/webhook",
        customer_email="cliente@exemplo.com",
        customer_first_name="João",
        customer_last_name="Silva",
        customer_personal_id="123.456.789-00",  # CPF válido obrigatório
        payment_method_tag="PIX"  # Opcional: Pré-selecionar método de pagamento
    )

    print(f"Transação Criada: {transaction.get('id')}")
    print(f"URL de Pagamento: {transaction.get('url')}")

except Exception as e:
    print(f"Erro ao criar transação: {e}")
```

### 3. Verificar Status

```python
transaction_id = "ID_DA_TRANSACAO_NA_RESPOSTA"
status = client.get_transaction(transaction_id)
print(f"Status Atual: {status.get('status')}")
```

## Países Suportados

O SDK fornece classes especializadas para padrões regionais:

| País | Classe | Moeda Padrão |
| :--- | :--- | :--- |
| **Brasil** | `PayRetailersBrazil` | BRL |
| **México** | `PayRetailersMexico` | MXN |
| **Chile** | `PayRetailersChile` | CLP |
| **Colômbia** | `PayRetailersColombia` | COP |
| **Argentina** | `PayRetailersArgentina` | ARS |
| **Peru** | `PayRetailersPeru` | PEN |
| **Equador** | `PayRetailersEcuador` | USD |

Para outros países, use `PayRetailersCountryClient` com os enums específicos.

## Uso Avançado

### Sobrescrever Moeda
Você pode processar transações em outras moedas (ex. USD) independentemente do cliente do país.

```python
transaction = client.create_transaction(
    amount=50.00,
    currency="USD",
    # ... outros campos
)
```

### Integração H2H (Host-to-Host)
O SDK tenta automaticamente buscar informações de landing H2H para métodos de pagamento suportados em Produção. Se disponível, chaves como `bank_account` ou `pdf_link` estarão presentes na resposta sob `h2h`.

---

## Exemplos de Resposta em Sandbox

### Brasil (BRL)
**Transação:**
```json
{"uid": "...", "status": "PENDING", "amount": 1000, "currency": "BRL", "paymentMethod": {"name": "PIX", "paymentMethodTag": "PIX"}}
```
**Paywall:**
```json
{"uid": "...", "amount": 1500, "currency": "BRL", "totalAmount": 15, "form": {"action": "https://api-sandbox.payretailers.com/payments/v2/public/paywalls/landing/..."}}
```

### México (MXN)
**Transação:**
```json
{"uid": "...", "status": "PENDING", "amount": 1000, "currency": "USD", "billing": {"currency": "MXN", "amount": 1000}}
```

### Colômbia (COP)
**Transação:**
```json
{"uid": "...", "status": "PENDING", "amount": 10000, "currency": "COP"}
```

### Chile (CLP)
**Transação:**
```json
{"uid": "...", "status": "PENDING", "amount": 1000, "currency": "CLP"}
```

### Argentina (ARS)
**Transação:**
```json
{"uid": "...", "status": "PENDING", "amount": 1000, "currency": "ARS"}
```

### Peru (PEN)
**Transação:**
```json
{"uid": "...", "status": "PENDING", "amount": 1000, "currency": "PEN"}
```

### Equador (USD)
**Transação:**
```json
{"uid": "...", "status": "FAILED", "message": "TRANSACTION_MIN_AMOUNT", "currency": "USD"}
```

---

Feito com ♥ por Caio Vinicius.
