import os
import uuid
from payretailers import PayRetailersEcuador
from dotenv import load_dotenv

load_dotenv()

client = PayRetailersEcuador(
    shop_id=os.getenv("SHOP_ID"),
    secret_key=os.getenv("SECRET_KEY"),
    subscription_key="1aa4e605bd5b405fba6061b55e52f4cd",
    sandbox=True
)

transaction = client.create_transaction(
    amount=100000,
    description="Transaction Test Ecuador",
    tracking_id=uuid.uuid4().hex,
    notification_url="https://webhook.site/d6b645c9-6c80-46c1-b2df-4cb5f6310f20",
    customer_first_name="Test",
    customer_last_name="Ecuador",
    customer_email="test_ec@example.com",
    customer_personal_id="1234567890",
    payment_method_tag="CREDIT_CARD"
)
print(f"Transaction Created: {transaction}")

status = client.get_transaction(transaction['uid'])
print(f"Transaction Status: {status}")

paywall = client.create_paywall(
    amount=150000,
    description="Paywall Test Ecuador",
    tracking_id=uuid.uuid4().hex,
    notification_url="https://webhook.site/d6b645c9-6c80-46c1-b2df-4cb5f6310f20",
    customer_first_name="Test",
    customer_last_name="Ecuador Paywall",
    customer_email="test_ec_pw@example.com",
    customer_personal_id="1234567890"
)
print(f"Paywall Created: {paywall}")
