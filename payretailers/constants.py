from .models import CountryEnum

# Sandbox Payment Method Tags per Country
SANDBOX_PAYMENT_METHODS = {
    CountryEnum.AR: ["ONLINE", "CASH"],
    CountryEnum.BR: ["ONLINE", "PIX", "BOLETO"],
    CountryEnum.CL: ["ONLINE", "CREDIT_CARD", "CASH"],
    CountryEnum.CO: ["ONLINE", "CREDIT_CARD", "CASH"],
    CountryEnum.CR: ["ONLINE", "CREDIT_CARD", "CASH"],
    CountryEnum.EC: ["ONLINE", "CREDIT_CARD", "CASH"],
    CountryEnum.MX: ["ONLINE", "CREDIT_CARD", "CASH"],
    CountryEnum.PE: ["ONLINE", "CREDIT_CARD", "CASH"],
    # Defaults for others if needed, using safe subset
}

def get_sandbox_methods_for_country(country_code: CountryEnum) -> list[str]:
    return SANDBOX_PAYMENT_METHODS.get(country_code, ["ONLINE"])
