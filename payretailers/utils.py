import re
from .exceptions import ValidationError

# Regex patterns per country for Personal ID
PERSONAL_ID_REGEX = {
    "BR": r"^[0-9]{3}\.?[0-9]{3}\.?[0-9]{3}\-?[0-9]{2}$",
    "AR": r"^[0-9]{2}\.?[0-9]{3}\.?[0-9]{3}$",
    "CR": r"^[1-9]-?[0-9]{4}-?[0-9]{4}$",
    "MX": r"^([A-Z][AEIOUX][A-Z]{2}\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])[HM](?:AS|B[CS]|C[CLMSH]|D[FG]|G[TR]|HG|JC|M[CNS]|N[ETL]|OC|PL|Q[TR]|S[PLR]|T[CSL]|VZ|YN|ZS)[B-DF-HJ-NP-TV-Z]{3}[A-Z\d])(\d)$",
    "CL": r"^\d{2}\.\d{3}\.\d{3}-[0-9kK]$",
    "PE": r"(^\d{8}-\d{1}$)|(^\d{9}$)",
    "CO": r"^[0-9]{1}\.?[0-9]{3}\.?[0-9]{3}.?[0-9]{3}|[0-9]{3}\.?[0-9]{3}$",
    "EC": r"^[0-9]{10}$",
    "PA": r"^(?:\d{1,2}-\d{2,3}-\d{4}|\d{7,9})$",
    "GT": r"(^\d{4}\s?\d{5}\s?\d{4}$)|(^\d{4}-?\d{5}-?\d{4}$)"
}

def validate_personal_id(country_code: str, personal_id: str) -> bool:
    """
    Validates a personal ID against the country's regex pattern.

    Args:
        country_code: 2-letter ISO country code.
        personal_id: The ID string to validate.

    Returns:
        True if valid or if no regex is defined for the country.
        Raises ValidationError if invalid.
    """
    regex = PERSONAL_ID_REGEX.get(country_code.upper())
    if not regex:
        return True # No specific validation for this country defined yet

    if not re.match(regex, personal_id):
         raise ValidationError(f"Invalid Personal ID '{personal_id}' for country '{country_code}'. Expected format regex: {regex}")
    return True

def normalize_country_code(country: str) -> str:
    """Normalizes country code to uppercase."""
    return country.strip().upper() if country else country
