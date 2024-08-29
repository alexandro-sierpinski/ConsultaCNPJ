from typing import List, Dict
import pandas as pd
from service import CNPJService
import os
import platform
import time

class CNPJModel:
    def __init__(self):
        self.service = CNPJService()
        self.pasta_base = os.path.join(self.obter_pasta_documentos(), "Consulta de CNPJ")

    def validar_cnpj(self, cnpj: str) -> bool:
        cnpj = ''.join(filter(str.isdigit, cnpj))
        return len(cnpj) == 14 and cnpj.isdigit()

    def consultar_cnpj(self, cnpj: str) -> Dict:
        if self.validar_cnpj(cnpj):
            try:
                resultado = self.service.consultar_cnpj(cnpj)
                if 'error' in resultado:
                    print(f"Erro ao consultar o CNPJ {cnpj}: {resultado['error']}")
                return resultado
            except Exception as e:
                print(f"Erro ao consultar o CNPJ {cnpj}: {e}")
        return {"error": f"CNPJ {cnpj} não encontrado na API Minha Receita"}

    def processar_xlsx(self, file_path: str) -> List[Dict]:
        try:
            df = pd.read_excel(file_path, engine='openpyxl')
            print("Colunas encontradas:", df.columns)  # Adiciona para depuração
            if df.empty:
                raise ValueError("O arquivo XLSX está vazio.")

            # Extrai todos os valores não nulos e os considera como CNPJs
            cnpjs = df.apply(lambda x: x.dropna().astype(str).tolist(), axis=1).explode().tolist()
            cnpjs = [cnpj for cnpj in cnpjs if self.validar_cnpj(cnpj)]  # Filtra apenas CNPJs válidos
        except Exception as e:
            print(f"Erro ao processar o arquivo XLSX: {e}")
            return []

        resultados = []
        cnpjs_erro = []  # Lista para armazenar CNPJs que deram erro
        for cnpj in cnpjs:
            # print(f"Consultando CNPJ: {cnpj}")
            resultado = self.consultar_cnpj(cnpj)
            if 'error' in resultado:
                cnpjs_erro.append(cnpj)
            # print(f"Resultado para CNPJ {cnpj}: {resultado}")
            print(f"Resultado para CNPJ {cnpj}: {resultado}")
            resultados.append(resultado)
            time.sleep(1)  # Atraso de 1 segundo entre as consultas
        
        # Salvar o log de erros
        self.salvar_log_erro(cnpjs_erro)
        return resultados

    def obter_pasta_documentos(self) -> str:
        """Obtém o caminho da pasta Documentos do usuário."""
        home = os.path.expanduser("~")
        sistema = platform.system()
        if sistema == "Windows":
            return os.path.join(home, "Documents")
        elif sistema == "Linux":
            return os.path.join(home, "Documents")
        elif sistema == "Darwin":  # macOS
            return os.path.join(home, "Documents")
        else:
            raise EnvironmentError("Sistema operacional não suportado")

    def criar_pastas(self):
        """Cria a estrutura de pastas necessária."""
        if not os.path.exists(self.pasta_base):
            os.makedirs(self.pasta_base)
        if not os.path.exists(os.path.join(self.pasta_base, "Resultado XLSX")):
            os.makedirs(os.path.join(self.pasta_base, "Resultado XLSX"))
        if not os.path.exists(os.path.join(self.pasta_base, "Log de erros de CNPJ")):
            os.makedirs(os.path.join(self.pasta_base, "Log de erros de CNPJ"))

    def salvar_resultados_em_xlsx(self, resultados: List[Dict], nome_arquivo: str):
        """Salva os resultados em um arquivo .xlsx na pasta Documentos."""
        self.criar_pastas()  # Garante que a estrutura de pastas esteja criada
        df = pd.DataFrame(resultados)
        if not all(col in df.columns for col in ['cnpj', 'razao_social', 'opcao_pelo_simples', 'opcao_pelo_mei']):
            raise KeyError("Alguns campos necessários estão ausentes nos resultados.")
        df = df[['cnpj', 'razao_social', 'opcao_pelo_simples', 'opcao_pelo_mei']]
        caminho_arquivo = os.path.join(self.pasta_base, "Resultado XLSX", nome_arquivo)
        try:
            df.to_excel(caminho_arquivo, index=False, engine='openpyxl')
            print(f"Arquivo salvo em: {caminho_arquivo}")
        except Exception as e:
            print(f"Erro ao salvar o arquivo: {e}")

    def salvar_log_erro(self, cnpjs_erro: List[str]):
        """Salva o log de CNPJs que deram erro em um arquivo TXT."""
        if not cnpjs_erro:
            print("Nenhum erro para registrar.")
            return  # Não cria o log se não houver erros

        caminho_log = os.path.join(self.pasta_base, "Log de erros de CNPJ", "log.txt")
        try:
            with open(caminho_log, 'w') as f:
                for cnpj in cnpjs_erro:
                    f.write(f"{cnpj}: CNPJ não encontrado na API Minha Receita\n")
            print(f"Log de erros salvo em: {caminho_log}")
        except Exception as e:
            print(f"Erro ao salvar o log de erros: {e}")

    def salvar_resultado_unico_em_xlsx(self, resultado: Dict, nome_arquivo: str):
        """Salva um único resultado em um arquivo .xlsx na pasta Documentos."""
        self.criar_pastas()  # Garante que a estrutura de pastas esteja criada
        df = pd.DataFrame([resultado])
        if not all(col in df.columns for col in ['cnpj', 'razao_social', 'opcao_pelo_simples', 'opcao_pelo_mei']):
            raise KeyError("Alguns campos necessários estão ausentes no resultado.")
        df = df[['cnpj', 'razao_social', 'opcao_pelo_simples', 'opcao_pelo_mei']]
        caminho_arquivo = os.path.join(self.pasta_base, "Resultado XLSX", nome_arquivo)
        try:
            df.to_excel(caminho_arquivo, index=False, engine='openpyxl')
            print(f"Arquivo salvo em: {caminho_arquivo}")
        except Exception as e:
            print(f"Erro ao salvar o arquivo: {e}")
