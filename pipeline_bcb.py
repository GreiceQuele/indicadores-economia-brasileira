import requests
import pandas as pd
import sqlite3

# 1. Definindo cabeçalho para simular acesso via navegador (evita bloqueio do BCB)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# Endpoints da API do Banco Central
url_selic = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.4390/dados?formato=json"
url_ipca = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados?formato=json"

try:
    # Coleta os dados passando o cabeçalho de autenticação/navegador
    resposta_selic = requests.get(url_selic, headers=headers, timeout=10)
    resposta_ipca = requests.get(url_ipca, headers=headers, timeout=10)

    print(f"Status requisição Selic: {resposta_selic.status_code}")
    print(f"Status requisição IPCA:  {resposta_ipca.status_code}")

    if resposta_selic.status_code == 200 and resposta_ipca.status_code == 200:
        # ==========================================
        # ETAPA 1 & 2: CONVERSÃO E LIMPEZA (Pandas)
        # ==========================================
        df_selic = pd.DataFrame(resposta_selic.json())
        df_ipca = pd.DataFrame(resposta_ipca.json())
        
        # Renomeia colunas
        df_selic = df_selic.rename(columns={"valor": "taxa_selic"})
        df_ipca = df_ipca.rename(columns={"valor": "taxa_ipca"})

        # Converte datas de texto para Datetime
        df_selic["data"] = pd.to_datetime(df_selic["data"], format="%d/%m/%Y")
        df_ipca["data"] = pd.to_datetime(df_ipca["data"], format="%d/%m/%Y")

        # Converte valores de texto para float
        df_selic["taxa_selic"] = df_selic["taxa_selic"].astype(float)
        df_ipca["taxa_ipca"] = df_ipca["taxa_ipca"].astype(float)

        # Junta as duas tabelas pela data
        df_consolidado = pd.merge(df_selic, df_ipca, on="data", how="inner")

        # ==========================================
        # ETAPA 3: CARGA (Salvando no Banco SQL)
        # ==========================================
        conexao = sqlite3.connect("inteligencia_macro.db")
        df_consolidado.to_sql("indicadores_mensais", conexao, if_exists="replace", index=False)
        conexao.close()

        print("\n🎉 SUCESSO! Pipeline executado do início ao fim e banco SQLite atualizado.")
        print("--- Últimos 5 meses consolidados ---")
        print(df_consolidado.tail(5))

    else:
        print("\n❌ Erro na resposta do Banco Central:")
        print(f"   - Selic: {resposta_selic.status_code}")
        print(f"   - IPCA:  {resposta_ipca.status_code}")

except Exception as e:
    print(f"\n❌ Ocorreu uma falha na conexão ou execução: {e}")