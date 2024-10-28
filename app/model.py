from typing import List, Dict
import pandas as pd
import asyncio
import os
import platform

from app.service import CNPJService


class CNPJModel:
    def __init__(self):
        self.service = CNPJService()
        self.pasta_base = os.path.join(self.obter_pasta_documentos(), "Consulta de CNPJ")
        self.criar_pastas()  # Garante que as pastas sejam criadas ao instanciar a classe

    def validar_cnpj(self, cnpj: str) -> bool:
        cnpj = ''.join(filter(str.isdigit, cnpj))
        print(len(cnpj) == 14 and cnpj.isdigit())
        return len(cnpj) == 14 and cnpj.isdigit()

    async def consultar_cnpj(self, cnpj: str) -> Dict:
        """Consulta um CNPJ de forma assíncrona usando o serviço CNPJService."""
        if self.validar_cnpj(cnpj):
            try:
                resultado = await self.service.consultar_cnpj(cnpj)
                if 'error' in resultado:
                    print(f"Erro ao consultar o CNPJ {cnpj}: {resultado['error']}")
                return resultado
            except Exception as e:
                print(f"Erro ao consultar o CNPJ {cnpj}: {e}")
        return {"error": f"CNPJ {cnpj} não encontrado na API Brasil"}

    async def processar_xlsx(self, file_path: str) -> List[Dict]:
        """Processa um arquivo XLSX contendo CNPJs de forma assíncrona."""
        try:
            # Carrega o arquivo Excel
            df = pd.read_excel(file_path, engine='openpyxl', header=None, dtype=str)

            # Aplica a formatação para preencher com zeros à esquerda em todas as colunas
            # Você pode ajustar o range de colunas conforme necessário, ou especificar diretamente as colunas que devem ser alteradas
            df = df.applymap(lambda x: x.zfill(14) if pd.notnull(x) and x.isdigit() and len(x) < 14 else x)

            # Agora o DataFrame `df` terá todos os valores com menos de 14 dígitos preenchidos com zeros à esquerda.
            print("Colunas encontradas:", df.columns)
            if df.empty:
                raise ValueError("O arquivo XLSX está vazio.")

            # Extrai todos os valores não nulos e os considera como CNPJs
            cnpjs = df.apply(lambda x: x.dropna().astype(str).tolist(), axis=1).explode().tolist()
            cnpjs = [cnpj for cnpj in cnpjs if self.validar_cnpj(cnpj)]
        except Exception as e:
            print(f"Erro ao processar o arquivo XLSX: {e}")
            return []

        resultados = []
        cnpjs_erro = []  # Lista para armazenar CNPJs que deram erro

        # Cria uma lista de tarefas para consultar todos os CNPJs assíncronamente
        tasks = [self.consultar_cnpj(cnpj) for cnpj in cnpjs]
        for idx, resultado in enumerate(await asyncio.gather(*tasks)):
            cnpj = cnpjs[idx]
            if 'error' in resultado:
                cnpjs_erro.append(cnpj)
            print(f"Resultado para CNPJ {cnpj}: {resultado}")
            resultados.append(resultado)
        
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
        try:
            if not os.path.exists(self.pasta_base):
                os.makedirs(self.pasta_base)
            if not os.path.exists(os.path.join(self.pasta_base, "Resultado XLSX")):
                os.makedirs(os.path.join(self.pasta_base, "Resultado XLSX"))
            if not os.path.exists(os.path.join(self.pasta_base, "Log de erros de CNPJ")):
                os.makedirs(os.path.join(self.pasta_base, "Log de erros de CNPJ"))
        except Exception as e:
            print(f"Erro ao criar pastas: {e}")

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
