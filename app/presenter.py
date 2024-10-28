import asyncio
from model import CNPJModel

class CNPJPresenter:
    def __init__(self, view):
        self.view = view
        self.model = CNPJModel()

    async def on_check_clicked(self, e):
        cnpj = self.view.cnpj_input.value
        if cnpj:
            # Exibir indicador de carregamento
            self.view.show_loading("Consultando CNPJ...")
            
            # Chama a função consultar_cnpj de forma assíncrona
            resultado = await self.model.consultar_cnpj(cnpj)
            print("Resultado da consulta:", resultado)
            
            # Ocultar indicador de carregamento
            self.view.hide_loading()

            if 'error' not in resultado:
                # Salva o resultado em um arquivo .xlsx na pasta Documentos
                self.model.salvar_resultado_unico_em_xlsx(
                    resultado,
                    nome_arquivo="resultado_cnpj.xlsx"
                )
            else:
                print("Erro ao consultar o CNPJ:", resultado['error'])
        else:
            print("Nenhum CNPJ informado.")

    async def on_file_picked(self, e):
        if e.files:
            for file in e.files:
                if file.name.endswith(".xlsx"):
                    file_path = file.path
                    print(f"Processando arquivo: {file_path}")
                    
                    # Exibir indicador de carregamento
                    self.view.show_loading("Processando arquivo...")
                    
                    # Chama a função processar_xlsx de forma assíncrona
                    resultados = await self.model.processar_xlsx(file_path)
                    print("Resultados das consultas em lote:", resultados)
                    
                    # Ocultar indicador de carregamento
                    self.view.hide_loading()

                    if resultados:
                        self.model.salvar_resultados_em_xlsx(
                            resultados,
                            nome_arquivo="resultado_consulta.xlsx"
                        )
                    else:
                        print("Nenhum resultado para salvar.")
                else:
                    print(f"Arquivo não suportado: {file.name}")

    def run_on_check_clicked(self, e):
        # Método para encapsular a chamada assíncrona usando asyncio
        asyncio.run(self.on_check_clicked(e))

    def run_on_file_picked(self, e):
        # Método para encapsular a chamada assíncrona usando asyncio
        asyncio.run(self.on_file_picked(e))
