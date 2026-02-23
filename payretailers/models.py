from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, field_validator, model_validator
from enum import Enum
from .utils import validate_personal_id
from .exceptions import ValidationError

class CountryEnum(str, Enum):
    AR = "AR"
    BR = "BR"
    CL = "CL"
    CO = "CO"
    CR = "CR"
    EC = "EC"
    SV = "SV"
    MX = "MX"
    PA = "PA"
    PE = "PE"
    GT = "GT"
    # African countries
    BF = "BF"
    CM = "CM"
    CI = "CI"
    GH = "GH"
    KE = "KE"
    RW = "RW"
    SN = "SN"
    TZ = "TZ"
    UG = "UG"
    NG = "NG"
    ZA = "ZA"

class CurrencyEnum(str, Enum):
    ARS = "ARS"
    BRL = "BRL"
    CLP = "CLP"
    COP = "COP"
    CRC = "CRC"
    USD = "USD"
    MXN = "MXN"
    PEN = "PEN"
    GTQ = "GTQ"
    # African Currencies
    RW = "RW"
    TZS = "TZS"
    UGX = "UGX"
    XOF = "XOF"
    XAF = "XAF"
    GHS = "GHS"
    KES = "KES"
    NGN = "NGN"
    ZAR = "ZAR"

    # Global/Crypto
    EUR = "EUR"
    USDT = "USDT"
    USDC = "USDC"

class LanguageEnum(str, Enum):
    EN = "EN"
    ES = "ES"
    PT = "PT"

class Customer(BaseModel):
    first_name: Optional[str] = Field(None, alias="firstName")
    last_name: Optional[str] = Field(None, alias="lastName")
    email: str
    personal_id: Optional[str] = Field(None, alias="personalId")
    country: CountryEnum
    phone: Optional[str] = None
    device_id: Optional[str] = Field(None, alias="deviceId")
    ip: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    zip_code: Optional[str] = Field(None, alias="zip")

    @model_validator(mode='after')
    def validate_personal_id_match(self):
        country = self.country
        personal_id = self.personal_id

        if country and personal_id:
            try:
                validate_personal_id(country.value, personal_id)
            except ValidationError as e:
                raise ValueError(str(e))
        return self

class TransactionRequest(BaseModel):
    amount: Union[str, int, float]
    currency: CurrencyEnum
    payment_method_tag_name: Optional[str] = Field(None, alias="paymentMethodTagName")
    description: str
    tracking_id: str = Field(..., alias="trackingId")
    notification_url: str = Field(..., alias="notificationUrl")
    return_url: Optional[str] = Field(None, alias="returnUrl")
    language: LanguageEnum = LanguageEnum.ES
    test_mode: bool = Field(False, alias="testMode")
    customer: Customer

    @field_validator('amount', mode='before')
    def stringify_amount(cls, v):
        return str(v)

    class Config:
        populate_by_name = True

class PaywallRequest(BaseModel):
    amount: Union[str, int, float]
    currency: CurrencyEnum
    description: str
    tracking_id: str = Field(..., alias="trackingId")
    notification_url: str = Field(..., alias="notificationUrl")
    return_url: Optional[str] = Field(None, alias="returnUrl")
    payment_channel_type_code: Optional[str] = Field(None, alias="paymentChannelTypeCode")
    language: LanguageEnum = LanguageEnum.ES
    test_mode: bool = Field(False, alias="testMode")
    customer: Customer

    @field_validator('amount', mode='before')
    def stringify_amount(cls, v):
        return str(v)

    class Config:
        populate_by_name = True

class PayoutRequest(BaseModel):
    amount: float
    currency_code: CurrencyEnum = Field(..., alias="currencyCode")
    country: CountryEnum
    bank_name: str = Field(..., alias="bankName")
    account_number: str = Field(..., alias="accountNumber")
    account_agency_number: Optional[str] = Field("-", alias="accountAgencyNumber")
    payout_account_type_code: str = Field("-", alias="payoutAccountTypeCode")
    beneficiary_first_name: str = Field(..., alias="beneficiaryFirstName")
    beneficiary_last_name: str = Field(..., alias="beneficiaryLastName")
    document_type: str = Field(..., alias="documentType")
    document_number: str = Field(..., alias="documentNumber")
    email: str
    city: Optional[str] = None
    external_reference: Optional[str] = Field(None, alias="externalReference")
    notification_url: Optional[str] = Field(None, alias="NotificationUrl")
    payment_reason: Optional[str] = Field(None, alias="PaymentReason")
    recipient_pix_key: Optional[str] = Field(None, alias="recipientPixKey")
    test_mode: bool = Field(False, alias="testMode")

    class Config:
        populate_by_name = True
