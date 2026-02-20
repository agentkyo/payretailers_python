# PayRetailers Python SDK

[English](README.md) | [Español](README.es.md) | [Português](README.pt.md) | [简体中文](README.zh.md)

Open Source Python SDK, разработанный для ускорения интеграции с **PayRetailers**. Сделано с любовью, чтобы помочь вам обрабатывать платежи быстро и безопасно.

Готов к использованию в продакшене, типизирован и полностью документирован.

- **Git-репозиторий**: [agentkyo/payretailers_python](https://github.com/agentkyo/payretailers_python)
- **Мейнтейнер**: agentkyo
- **Контакты**: caioviniciusxd@gmail.com | integrations@payretailers.com

---

## Особенности

- **Поддержка множества стран**: Специализированные клиенты для Бразилии, Мексики, Колумбии, Чили, Аргентины, Перу, Эквадора, Коста-Рики и других.
- **Умная валидация**: Автоматическая проверка налоговых идентификаторов (CPF, CURP, RUT и т.д.) и обязательных полей.
- **Интеграция H2H**: Встроенная поддержка транзакций Host-to-Host (где доступно).
- **Надежная обработка ошибок**: Понятные исключения и автоматические повторные попытки при сетевых проблемах.
- **Безопасность типов**: Полная типизация с использованием моделей Pydantic.
- **Управление окружением**: Легкое переключение между Sandbox и Production.

## Установка

```bash
pip install requests pydantic httpx tenacity
```

## Быстрый старт

### 1. Инициализация клиента

Выберите специализированный клиент для вашей целевой страны.

```python
from payretailers import PayRetailersBrazil

# Инициализация для Бразилии (Sandbox)
client = PayRetailersBrazil(
    shop_id="ВАШ_SHOP_ID",
    secret_key="ВАШ_SECRET_KEY",
    subscription_key="ВАШ_SUBSCRIPTION_KEY",
    sandbox=True  # Установите False для Production
)
```

### 2. Создание транзакции

SDK автоматически обрабатывает валюту по умолчанию и валидацию.

```python
import uuid

try:
    transaction = client.create_transaction(
        amount=100.00,  # BRL по умолчанию для клиента Бразилии
        description="Премиум подписка",
        tracking_id=uuid.uuid4().hex,
        notification_url="https://your-domain.com/webhook",
        customer_email="customer@example.com",
        customer_first_name="Иван",
        customer_last_name="Иванов",
        customer_personal_id="123.456.789-00",  # Требуется валидный CPF
        payment_method_tag="PIX"  # Опционально: Предварительный выбор метода оплаты
    )

    print(f"Транзакция создана: {transaction.get('id')}")
    print(f"URL оплаты: {transaction.get('url')}")

except Exception as e:
    print(f"Ошибка при создании транзакции: {e}")
```

### 3. Проверка статуса

```python
transaction_id = "ID_ТРАНЗАКЦИИ_ИЗ_ОТВЕТА"
status = client.get_transaction(transaction_id)
print(f"Текущий статус: {status.get('status')}")
```

## Поддерживаемые страны

SDK предоставляет специализированные классы для региональных настроек по умолчанию:

| Страна | Класс | Валюта по умолчанию |
| :--- | :--- | :--- |
| **Бразилия** | `PayRetailersBrazil` | BRL |
| **Мексика** | `PayRetailersMexico` | MXN |
| **Чили** | `PayRetailersChile` | CLP |
| **Колумбия** | `PayRetailersColombia` | COP |
| **Аргентина** | `PayRetailersArgentina` | ARS |
| **Перу** | `PayRetailersPeru` | PEN |
| **Эквадор** | `PayRetailersEcuador` | USD |

Для других стран используйте `PayRetailersCountryClient` с соответствующими перечислениями (enum).

## Расширенное использование

### Переопределение валюты
Вы можете обрабатывать транзакции в других валютах (например, USD) независимо от клиента страны.

```python
transaction = client.create_transaction(
    amount=50.00,
    currency="USD",
    # ... другие поля
)
```

### Интеграция H2H (Host-to-Host)
SDK автоматически пытается получить информацию H2H для поддерживаемых методов оплаты в Production. Если она доступна, ключи, такие как `bank_account` или `pdf_link`, будут присутствовать в ответе в поле `h2h`.

---

Сделано с ♥ от Caio Vinicius.
