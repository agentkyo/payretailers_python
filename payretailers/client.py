import os
import json
import base64
import httpx
from tenacity import Retrying, stop_after_attempt, wait_exponential, retry_if_exception_type, before_sleep_log
import logging
from typing import Union, Dict, Any, Optional
from .logger import logger
from .exceptions import get_exception_for_code, APIConnectionError, AuthenticationError, PayRetailersError
from .models import TransactionRequest, PaywallRequest, PayoutRequest
import time
from dotenv import load_dotenv

load_dotenv()

BLACKLIST_FILE = "payretailers_h2h_cache.json"
BLACKLIST_DURATION = 86400  # 24 hours in seconds

class PayRetailersClient:
    """
    Main client for interacting with the Payretailers API.
    """
    PRODUCTION_URL = "https://api.payretailers.com/payments/v2/"
    SANDBOX_URL = "https://api-sandbox.payretailers.com/payments/v2/"

    def __init__(self,
                 shop_id: str,
                 secret_key: str,
                 subscription_key: str,
                 sandbox: bool = False,
                 log_level: int = logging.DEBUG,
                 max_retries: int = 3):

        self.shop_id = shop_id
        self.secret_key = secret_key
        self.subscription_key = subscription_key
        self.sandbox = sandbox
        self.base_url = self.SANDBOX_URL if sandbox else self.PRODUCTION_URL
        self.auth_header = self._generate_auth_header()
        logger.setLevel(log_level)
        self.max_retries = max_retries
        self.client = httpx.Client(
            base_url=self.base_url,
            headers={
                "accept": "application/json",
                "content-type": "application/json",
                "Ocp-Apim-Subscription-Key": self.subscription_key,
                "authorization": self.auth_header
            },
            timeout=30.0 # Default timeout
        )

        self.blacklist = self._load_blacklist_cache()

    def _load_blacklist_cache(self) -> Dict[str, float]:
        """Loads the H2H blacklist from a local JSON file."""
        if os.path.exists(BLACKLIST_FILE):
            try:
                with open(BLACKLIST_FILE, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {}

    def _save_blacklist_cache(self):
        """Saves the H2H blacklist to a local JSON file."""
        try:
            with open(BLACKLIST_FILE, "w") as f:
                json.dump(self.blacklist, f)
        except IOError as e:
            logger.warning(f"Failed to save H2H blacklist cache: {e}")

    def get_landing_info(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves landing info for a transaction (H2H integration).
        Endpoint: public/transactions/landing-info/{TransactionID}

        NOTE: This method is NOT available in Sandbox.
        """
        if self.sandbox:
            logger.warning("get_landing_info is NOT available in Sandbox environment.")
            return None

        try:
            response_json = self._send_request("GET", f"public/transactions/landing-info/{transaction_id}")
            return response_json
        except Exception as e:
             raise e

    def _generate_auth_header(self) -> str:
        credentials = f"{self.shop_id}:{self.secret_key}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded_credentials}"

    def _send_request(self, method: str, endpoint: str, payload: Optional[Dict] = None, params: Optional[Dict] = None):
        """
        Sends HTTP request with retry logic using Tenacity.
        """
        full_url_for_logging = f"{self.base_url}{endpoint}"
        retry_strategy = Retrying(
            stop=stop_after_attempt(self.max_retries),
            wait=wait_exponential(multiplier=1, min=4, max=10),
            retry=retry_if_exception_type((httpx.RequestError, httpx.TimeoutException, httpx.HTTPStatusError)),
            before_sleep=before_sleep_log(logger, logging.WARNING),
            reraise=True # Re-raise the last exception if retries are exhausted
        )

        logger.debug(f"Sending {method} request to {full_url_for_logging}")

        if payload:
            logger.debug(f"Payload: {json.dumps(payload, default=str)}")

        response = None # Initialize response to ensure it's defined

        try:
            for attempt in retry_strategy:
                with attempt:
                    try:
                        if method.upper() == "GET":
                            response = self.client.get(endpoint, params=params)
                        elif method.upper() == "POST":
                            response = self.client.post(endpoint, json=payload)
                        elif method.upper() == "PUT":
                            response = self.client.put(endpoint, json=payload)
                        elif method.upper() == "PATCH":
                            response = self.client.patch(endpoint, json=payload)
                        else:
                            raise ValueError(f"Invalid HTTP method: {method}")

                        if 500 <= response.status_code < 600:
                            response.raise_for_status()
                        break
                    except httpx.HTTPStatusError as e:
                        if 400 <= e.response.status_code < 500:
                            response = e.response
                            raise
                        raise
        except (httpx.RequestError, httpx.TimeoutException) as e:

            logger.error(f"Request to {full_url_for_logging} failed after {self.max_retries} attempts due to connection error: {e}")
            raise APIConnectionError(f"PayRetailers API Unreachable: {e}")
        except httpx.HTTPStatusError as e:
            response = e.response
            logger.error(f"Request to {full_url_for_logging} failed with status {response.status_code} after {self.max_retries} attempts: {e}")
        if response is None:
            raise APIConnectionError("No response received from PayRetailers API after all attempts.")

        logger.info(f"Response Status Code: {response.status_code}")
        logger.info(f"Response Body: {response.text}")

        if not response.is_success:
            self._handle_error(response)

        return response.json()

    def _handle_error(self, response):
        """Parses error response and raises appropriate exception."""
        try:
            error_data = response.json()
            code = error_data.get("code") or error_data.get("error_code") or str(response.status_code)
            message = error_data.get("message") or error_data.get("description") or response.text
        except ValueError:
            code = str(response.status_code)
            message = response.text

        logger.error(f"API Error. Code: {code}, Message: {message}")

        if response.status_code == 401:
            raise AuthenticationError(f"Authentication failed: {message}", code=code, status_code=response.status_code)

        raise get_exception_for_code(code, message, status_code=response.status_code)

    def create_transaction(self, request: Union[TransactionRequest, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Creates a new transaction.

        Args:
            request: A TransactionRequest model or a dictionary.
        """
        if isinstance(request, dict):
            request_model = TransactionRequest(**request)
        else:
            request_model = request

        payload = request_model.model_dump(by_alias=True)
        response = self._send_request("POST", "transactions", payload=payload)

        status = response.get("status")
        if isinstance(status, str) and status.upper() == "MISSING_INFO":
            logger.warning(
                "Transaction created with status 'MISSING_INFO'. "
                "The payer data provided was insufficient or invalid. "
                "Please provide full customer details (first_name, last_name, personal_id) "
                "to increase conversion rates."
            )

        payment_method = payload.get("paymentMethodTagName")
        is_transaction_valid = False
        if isinstance(status, str):
            status_upper = status.upper()
            if status_upper in ["PENDING", "MISSING_INFO"]:
                is_transaction_valid = True
            elif status_upper == "FAILED":
                logger.error(f"Transaction failed creation. Status: {status}. Message: {response.get('message')}")
        if is_transaction_valid and payment_method and not self.sandbox:
            is_blacklisted = False
            if payment_method in self.blacklist:
                expiry = self.blacklist[payment_method]
                if time.time() < expiry:
                    is_blacklisted = True
                    logger.debug(f"Payment method '{payment_method}' is in H2H blacklist. Skipping landing info.")
                else:
                    del self.blacklist[payment_method]
                    self._save_blacklist_cache()

            if not is_blacklisted:
                transaction_id = response.get("id") or response.get("uid")
                if transaction_id:
                    try:
                        landing_info = self.get_landing_info(transaction_id)
                        if landing_info:
                             response["h2h"] = landing_info
                             if payment_method in self.blacklist:
                                 del self.blacklist[payment_method]
                                 self._save_blacklist_cache()
                    except Exception as e:
                        logger.warning(f"Failed to fetch Landing Info for '{payment_method}'. Adding to blacklist. Error: {e}")
                        # Add to blacklist
                        self.blacklist[payment_method] = time.time() + BLACKLIST_DURATION
                        self._save_blacklist_cache()
        elif self.sandbox and payment_method:
             logger.warning("H2H Integration (Get Landing Info) skipped in Sandbox mode.")

        return response

    def create_paywall(self, request: Union[PaywallRequest, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Creates a new paywall.
        """
        if isinstance(request, dict):
            request_model = PaywallRequest(**request)
        else:
            request_model = request

        payload = request_model.model_dump(by_alias=True)
        return self._send_request("POST", "paywalls", payload=payload)

    def create_payout(self, request: Union[PayoutRequest, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Creates a new payout.
        """
        if isinstance(request, dict):
            request_model = PayoutRequest(**request)
        else:
            request_model = request

        payload = request_model.model_dump(by_alias=True)
        return self._send_request("POST", "payout", payload=payload)

    def get_transaction(self, uid: str) -> Dict[str, Any]:
        """Retrieve transaction by UID."""
        return self._send_request("GET", f"transactions/{uid}")

    def get_transaction_by_tracking_id(self, tracking_id: str) -> Dict[str, Any]:
        """Retrieve transaction by Tracking ID."""
        return self._send_request("GET", "transactions", params={"trackingId": tracking_id})

    def get_paywall_by_uid(self, uid: str) -> Dict[str, Any]:
        """Retrieve Paywall by UID."""
        return self._send_request("GET", f"paywalls/{uid}")

    def get_paywall_by_tracking_id(self, tracking_id: str) -> Dict[str, Any]:
        """
        Retrieve Paywall by Tracking ID.
        """
        return self._send_request("GET", "paywalls", params={"trackingId": tracking_id})

    def get_payout_details(self, external_reference: str) -> Dict[str, Any]:
        """
        Get Payout Details.
        Endpoint: payout/{externalReference}
        """
        return self._send_request("GET", f"payout/{external_reference}")

    def get_payment_methods(self, country: Optional[str] = None, currency: Optional[str] = None, channel: Optional[str] = None) -> Dict[str, Any]:
        """
        Get available payment methods.
        All parameters are optional filters.
        """
        params = {}
        if country:
            params["country"] = country
        if currency:
            params["currency"] = currency
        if channel:
            params["channel"] = channel

        return self._send_request("GET", "paymentMethods", params=params)

    def get_shop_balance(self) -> Dict[str, Any]:
        """Get shop balance."""
        if self.sandbox:
            logger.warning("get_shop_balance is NOT available in Sandbox environment.")
        return self._send_request("GET", "shop-balance")

    def close(self):
        """Closes the HTTPX client connection pool."""
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
