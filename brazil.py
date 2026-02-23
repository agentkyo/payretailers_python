import os
import uuid
from payretailers import PayRetailersBrazil
from dotenv import load_dotenv

load_dotenv()

client = PayRetailersBrazil(
    shop_id=os.getenv("SHOP_ID"),
    secret_key=os.getenv("SECRET_KEY"),
    subscription_key="1aa4e605bd5b405fba6061b55e52f4cd",
    sandbox=True
)

transaction = client.create_transaction(
    amount=1000,
    description="Transaction Test Brazil",
    tracking_id=uuid.uuid4().hex,
    notification_url="https://webhook.site/d6b645c9-6c80-46c1-b2df-4cb5f6310f20",
    customer_first_name="Teste",
    customer_last_name="Brasil",
    customer_email="test_br@example.com",
    customer_personal_id="12345678900",
    payment_method_tag="PIX"
)
print(f"Transaction Created: {transaction}")

status = client.get_transaction(transaction['uid'])
print(f"Transaction Status: {status}")

paywall = client.create_paywall(
    amount=1500,
    description="Paywall Test Brazil",
    tracking_id=uuid.uuid4().hex,
    notification_url="https://webhook.site/d6b645c9-6c80-46c1-b2df-4cb5f6310f20",
    customer_first_name="Teste",
    customer_last_name="Brasil Paywall",
    customer_email="test_br_pw@example.com",
    customer_personal_id="12345678900"
)
print(f"Paywall Created: {paywall}")
