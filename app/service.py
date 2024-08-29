import requests
from typing import Dict

class CNPJService:
    def consultar_cnpj(self, cnpj: str) -> Dict:
        url = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}"
        try:
            response = requests.get(url)
            response.raise_for_status()  # Levanta um erro para códigos de status 4xx/5xx
            data = response.json()
            # Extrair apenas os campos desejados
            return {
                "cnpj": data.get("cnpj"),
                "razao_social": data.get("razao_social"),
                "opcao_pelo_simples": data.get("opcao_pelo_simples"),
                "opcao_pelo_mei": data.get("opcao_pelo_mei")
            }
        except requests.exceptions.HTTPError as http_err:
            # Captura erros HTTP (por exemplo, 404, 500) e inclui a mensagem de erro
            return {"error": f"HTTP error occurred: {http_err}"}
        except requests.exceptions.RequestException as req_err:
            # Captura erros de rede ou problemas de solicitação
            return {"error": f"Request error occurred: {req_err}"}
