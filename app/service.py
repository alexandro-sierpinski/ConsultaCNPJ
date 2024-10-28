import requests
import aiohttp
from typing import Dict

class CNPJService:
    async def consultar_cnpj(self, cnpj: str) -> Dict:
        url = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    response.raise_for_status()  # Levanta um erro para códigos de status 4xx/5xx
                    data = await response.json()
                    # Extrair apenas os campos desejados
                    return {
                        "cnpj": data.get("cnpj") if data.get("cnpj") else False,
                        "razao_social": data.get("razao_social") if data.get("razao_social") else False,
                        "opcao_pelo_simples": data.get("opcao_pelo_simples") if data.get(
                            "opcao_pelo_simples") else False,
                        "opcao_pelo_mei": data.get("opcao_pelo_mei") if data.get("opcao_pelo_mei") else False
                    }

        except aiohttp.ClientResponseError as http_err:
            # Captura erros HTTP (por exemplo, 404, 500) e inclui a mensagem de erro
            return {"error": f"HTTP error occurred: {http_err}"}
        except aiohttp.ClientError as req_err:
            # Captura erros de rede ou problemas de solicitação
            return {"error": f"Request error occurred: {req_err}"}
