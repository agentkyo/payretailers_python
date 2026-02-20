import logging
from typing import Optional, Dict, Any, Union
from .client import PayRetailersClient
from .models import TransactionRequest, PaywallRequest, Customer, CountryEnum, CurrencyEnum, LanguageEnum

class PayRetailersCountryClient:
    """
    Base wrapper for country-specific operations.
    """
    def __init__(self,
                 shop_id: str,
                 secret_key: str,
                 subscription_key: str,
                 country_code: CountryEnum,
                 default_currency: CurrencyEnum,
                 sandbox: bool = False,
                 log_level: int = logging.DEBUG,
                 max_retries: int = 3):
        self._client = PayRetailersClient(
            shop_id,
            secret_key,
            subscription_key,
            sandbox=sandbox,
            log_level=log_level,
            max_retries=max_retries
        )
        self._country_code = country_code
        self._default_currency = default_currency
        self.sandbox = sandbox
        self._cached_payment_methods = None

    @property
    def base_url(self):
        return self._client.base_url

    def _fetch_payment_methods_tags(self) -> set:
        """Fetch and cache payment method tags."""
        if self._cached_payment_methods is None:
            methods = self._client.get_payment_methods(country=self._country_code.value, currency=self._default_currency.value)
            # Flatten list to get tags
            self._cached_payment_methods = {
                m.get("paymentMethodTag")
                for m in methods.get("list", [])
                if m.get("paymentMethodTag")
            }
        return self._cached_payment_methods

    def _validate_payment_method_tag(self, tag: Optional[str]) -> str:
        """
        Validates the payment method tag.
        - If missing: Recommends valid tags.
        - If provided: Checks validity (Sandbox: Static check, Prod: Api check).
        """
        if self.sandbox:
            from .constants import get_sandbox_methods_for_country
            valid_tags = get_sandbox_methods_for_country(self._country_code)

            if not tag:
                raise ValueError(
                    f"Payment Method Tag is required for Sandbox. "
                    f"Available tags for {self._country_code.value}: {', '.join(valid_tags)}"
                )

            if tag not in valid_tags:
                 raise ValueError(
                    f"Invalid Payment Method Tag '{tag}' for {self._country_code.value} Sandbox. "
                    f"Available: {', '.join(valid_tags)}"
                )
            return tag
        else:
            # Production
            prod_tags = self._fetch_payment_methods_tags()

            if not tag:
                tags_list = ", ".join(sorted(prod_tags))
                raise ValueError(
                    f"Payment Method Tag is required. "
                    f"Active methods found for {self._country_code.value}: {tags_list}"
                )

            if tag not in prod_tags:
                 tags_list = ", ".join(sorted(prod_tags))
                 raise ValueError(
                    f"Invalid Payment Method Tag '{tag}'. "
                    f"Active methods for {self._country_code.value} are: {tags_list}"
                )
            return tag

    def _prepare_customer(self,
                          first_name: str,
                          last_name: str,
                          email: str,
                          personal_id: str,
                          phone: Optional[str] = None,
                          address: Optional[str] = None,
                          city: Optional[str] = None,
                          **kwargs) -> Customer:

        return Customer(
            firstName=first_name,
            lastName=last_name,
            email=email,
            personalId=personal_id,
            country=self._country_code,
            phone=phone,
            address=address,
            city=city,
            **kwargs
        )

    def create_transaction(self,
                           amount: int,
                           description: str,
                           tracking_id: str,
                           notification_url: str,
                           customer_email: str,
                           customer_first_name: Optional[str] = None,
                           customer_last_name: Optional[str] = None,
                           customer_personal_id: Optional[str] = None,
                           currency: Optional[Union[str, CurrencyEnum]] = None,
                           phone: Optional[str] = None,
                           payment_method_tag: Optional[str] = None,
                           return_url: Optional[str] = None,
                           language: LanguageEnum = LanguageEnum.ES,
                           test_mode: bool = False,
                           **customer_kwargs) -> Dict[str, Any]:
        """
        Simplified transaction creation.
        """
        # Logging warning for missing fields
        from .logger import logger
        if not customer_first_name or not customer_last_name or not customer_personal_id:
             logger.warning(
                 f"Creating transaction with missing Customer info (first_name, last_name, or personal_id). "
                 f"Status 'missing_info' expected. "
                 f"Consider providing these fields to increase conversion."
             )

        # Support for users who might still provide payment_method_tag_name in kwargs (bc)
        if payment_method_tag is None:
            payment_method_tag = customer_kwargs.pop('payment_method_tag_name', None)

        # Validate Tag
        validated_tag = self._validate_payment_method_tag(payment_method_tag)

        # Determine currency: explicit > default
        if currency is None:
            use_currency = self._default_currency
        else:
            # If string passed, ensure it matches allowed or cast to enum if strict
            use_currency = currency

        customer = self._prepare_customer(
            first_name=customer_first_name,
            last_name=customer_last_name,
            email=customer_email,
            personal_id=customer_personal_id,
            phone=phone,
            **customer_kwargs
        )

        request = TransactionRequest(
            amount=amount,
            currency=use_currency,
            description=description,
            trackingId=tracking_id,
            notificationUrl=notification_url,
            customer=customer,
            paymentMethodTagName=validated_tag,
            returnUrl=return_url,
            language=language,
            testMode=test_mode
        )

        return self._client.create_transaction(request)

    def create_paywall(self,
                       amount: int,
                       description: str,
                       tracking_id: str,
                       notification_url: str,
                       customer_email: str,
                       customer_first_name: Optional[str] = None,
                       customer_last_name: Optional[str] = None,
                       customer_personal_id: Optional[str] = None,
                       currency: Optional[Union[str, CurrencyEnum]] = None,
                       phone: Optional[str] = None,
                       payment_channel_type_code: Optional[str] = None,
                       return_url: Optional[str] = None,
                       language: LanguageEnum = LanguageEnum.ES,
                       test_mode: bool = False,
                       **customer_kwargs) -> Dict[str, Any]:

        # Logging warning for missing fields
        from .logger import logger
        if not customer_first_name or not customer_last_name or not customer_personal_id:
             logger.warning(
                 f"Creating paywall with missing Customer info. "
                 f"Status 'missing_info' expected. "
                 f"Consider providing these fields to increase conversion."
             )

        if currency is None:
            use_currency = self._default_currency
        else:
            use_currency = currency

        customer = self._prepare_customer(
            first_name=customer_first_name,
            last_name=customer_last_name,
            email=customer_email,
            personal_id=customer_personal_id,
            phone=phone,
            **customer_kwargs
        )

        request = PaywallRequest(
            amount=amount,
            currency=use_currency,
            description=description,
            trackingId=tracking_id,
            notificationUrl=notification_url,
            customer=customer,
            paymentChannelTypeCode=payment_channel_type_code,
            returnUrl=return_url,
            language=language,
            testMode=test_mode
        )

        return self._client.create_paywall(request)

    # Delegate other methods
    def get_transaction(self, uid: str):
        return self._client.get_transaction(uid)

    def get_transaction_by_tracking_id(self, tracking_id: str):
        return self._client.get_transaction_by_tracking_id(tracking_id)

    def get_paywall_by_uid(self, uid: str):
        return self._client.get_paywall_by_uid(uid)

    def get_paywall_by_tracking_id(self, tracking_id: str):
        return self._client.get_paywall_by_tracking_id(tracking_id)

    def get_payment_methods(self, channel: Optional[str] = None, country: Optional[str] = None, currency: Optional[str] = None) -> Dict[str, Any]:
        """
        Get available payment methods.
        Defaults to the client's country and currency if not specified.
        """
        use_country = country if country else self._country_code
        use_currency = currency if currency else self._default_currency
        return self._client.get_payment_methods(country=use_country, currency=use_currency, channel=channel)

    def get_shop_balance(self):
        return self._client.get_shop_balance()


class PayRetailersBrazil(PayRetailersCountryClient):
    def __init__(self, shop_id: str, secret_key: str, subscription_key: str, sandbox: bool = False, log_level: int = logging.DEBUG, max_retries: int = 3):
        super().__init__(shop_id, secret_key, subscription_key, CountryEnum.BR, CurrencyEnum.BRL, sandbox, log_level, max_retries)

class PayRetailersArgentina(PayRetailersCountryClient):
    def __init__(self, shop_id: str, secret_key: str, subscription_key: str, sandbox: bool = False, log_level: int = logging.DEBUG, max_retries: int = 3):
        super().__init__(shop_id, secret_key, subscription_key, CountryEnum.AR, CurrencyEnum.ARS, sandbox, log_level, max_retries)

class PayRetailersChile(PayRetailersCountryClient):
    def __init__(self, shop_id: str, secret_key: str, subscription_key: str, sandbox: bool = False, log_level: int = logging.DEBUG, max_retries: int = 3):
        super().__init__(shop_id, secret_key, subscription_key, CountryEnum.CL, CurrencyEnum.CLP, sandbox, log_level, max_retries)

class PayRetailersColombia(PayRetailersCountryClient):
    def __init__(self, shop_id: str, secret_key: str, subscription_key: str, sandbox: bool = False, log_level: int = logging.DEBUG, max_retries: int = 3):
        super().__init__(shop_id, secret_key, subscription_key, CountryEnum.CO, CurrencyEnum.COP, sandbox, log_level, max_retries)

class PayRetailersMexico(PayRetailersCountryClient):
    def __init__(self, shop_id: str, secret_key: str, subscription_key: str, sandbox: bool = False, log_level: int = logging.DEBUG, max_retries: int = 3):
        super().__init__(shop_id, secret_key, subscription_key, CountryEnum.MX, CurrencyEnum.MXN, sandbox, log_level, max_retries)

class PayRetailersPeru(PayRetailersCountryClient):
    def __init__(self, shop_id: str, secret_key: str, subscription_key: str, sandbox: bool = False, log_level: int = logging.DEBUG, max_retries: int = 3):
        super().__init__(shop_id, secret_key, subscription_key, CountryEnum.PE, CurrencyEnum.PEN, sandbox, log_level, max_retries)

class PayRetailersEcuador(PayRetailersCountryClient):
    def __init__(self, shop_id: str, secret_key: str, subscription_key: str, sandbox: bool = False, log_level: int = logging.DEBUG, max_retries: int = 3):
        super().__init__(shop_id, secret_key, subscription_key, CountryEnum.EC, CurrencyEnum.USD, sandbox, log_level, max_retries)
