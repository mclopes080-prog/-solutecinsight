"""
SolutecAI — modelo de detecção de anomalias em vendas.

Programação funcional: cada função recebe dados e retorna dados novos.
Nenhuma função usa `global`, nenhuma modifica o argumento recebido e cada
uma tem exatamente uma responsabilidade.
"""

import pandas as pd
from sklearn.ensemble import IsolationForest

COLUNAS_FEATURES = ['total_quantidade', 'total_receita', 'num_transacoes']


def carregar_dados(conn) -> pd.DataFrame:
    # [FUNCIONAL] função pura — sem side effects (a leitura em si é a borda de I/O)
    query = """
        SELECT data_venda,
               SUM(quantidade)  AS total_quantidade,
               SUM(valor_total) AS total_receita,
               COUNT(*)         AS num_transacoes
        FROM vendas
        GROUP BY data_venda
        ORDER BY data_venda
    """
    return pd.read_sql(query, conn)


def treinar_modelo(dados: pd.DataFrame) -> IsolationForest:
    # [FUNCIONAL] função pura — sem side effects
    features = dados[COLUNAS_FEATURES].copy()
    modelo = IsolationForest(contamination=0.08, random_state=42)
    modelo.fit(features)
    return modelo


def normalizar_score(score_bruto: float) -> float:
    # [FUNCIONAL] função pura — sem side effects
    # decision_function do Isolation Forest varia tipicamente entre -0.5 e 0.5;
    # inverte e recorta para a faixa 0 (normal) .. 1 (muito anômalo), compatível
    # com os limiares usados por fn_categoria_risco no banco.
    normalizado = 0.5 - score_bruto
    return round(min(1.0, max(0.0, normalizado)), 4)


def classificar_tipo(quantidade: float, receita: float, media_quantidade: float, media_receita: float) -> str:
    # [FUNCIONAL] função pura — sem side effects
    # score < -0.1 já foi filtrado por quem chama; aqui só decidimos o tipo:
    # receita bem abaixo da média → queda de receita; caso contrário, tratamos
    # como pico de volume (quantidade/transações acima do padrão).
    if receita < media_receita * 0.5:
        return 'QUEDA_RECEITA'
    return 'PICO_VOLUME'


def formatar_descricao(tipo: str, quantidade: float, receita: float, media_quantidade: float, media_receita: float) -> str:
    # [FUNCIONAL] função pura — sem side effects
    if tipo == 'QUEDA_RECEITA':
        return f"Queda de receita: R$ {receita:.2f} no dia (média R$ {media_receita:.2f})"
    return f"Pico de volume: {int(quantidade)} unidades vendidas no dia (média {media_quantidade:.1f})"


def detectar_anomalias(modelo: IsolationForest, dados: pd.DataFrame) -> list[dict]:
    # [FUNCIONAL] função pura — sem side effects
    dados_avaliados = dados.copy()
    features = dados_avaliados[COLUNAS_FEATURES]
    dados_avaliados['score_bruto'] = modelo.decision_function(features)
    dados_avaliados['eh_anomalia'] = modelo.predict(features)

    media_quantidade = dados_avaliados['total_quantidade'].mean()
    media_receita = dados_avaliados['total_receita'].mean()

    anomalias = []
    for _, linha in dados_avaliados[dados_avaliados['eh_anomalia'] == -1].iterrows():
        tipo = classificar_tipo(linha['total_quantidade'], linha['total_receita'], media_quantidade, media_receita)
        anomalias.append({
            'data_ref': pd.Timestamp(linha['data_venda']).strftime('%Y-%m-%d'),
            'tipo': tipo,
            'score': normalizar_score(linha['score_bruto']),
            'quantidade': int(linha['total_quantidade']),
            'receita': float(linha['total_receita']),
            'descricao': formatar_descricao(tipo, linha['total_quantidade'], linha['total_receita'], media_quantidade, media_receita),
        })
    return anomalias


def filtrar_por_periodo(anomalias: list[dict], data_inicio: str, data_fim: str) -> list[dict]:
    # [FUNCIONAL] função pura — sem side effects
    return [a for a in anomalias if data_inicio <= a['data_ref'] <= data_fim]


def formatar_relatorio(anomalias: list[dict]) -> str:
    # [FUNCIONAL] função pura — sem side effects
    if not anomalias:
        return "Nenhuma anomalia detectada no período."
    linhas = [
        f"- {a['data_ref']} [{a['tipo']}] {a['descricao']} (score {a['score']})"
        for a in anomalias
    ]
    return "\n".join(linhas)
