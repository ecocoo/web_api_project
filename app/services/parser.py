import httpx
from typing import List, Dict

CBR_URL = "https://www.cbr-xml-daily.ru/daily_json.js"

class RatesParser:
    def __init__(self):
        self.url = CBR_URL

    async def fetch_rates(self) -> List[Dict]:
        
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(self.url)
            response.raise_for_status()
            data = response.json()

        rates = []
        valute_dict = data.get("Valute", {})

        for currency_info in valute_dict.values():
            rates.append({
                "code": currency_info["CharCode"],
                "name": currency_info["Name"],
                "value": currency_info["Value"],
            })

        return rates