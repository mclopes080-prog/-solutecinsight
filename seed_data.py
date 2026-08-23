"""
SolutecAI — geração de dados sintéticos de vendas.

Popula a tabela `vendas` com ~90 dias de histórico, usando os produtos reais
já cadastrados na loja. A maioria dos dias tem volume normal; alguns dias
recebem anomalias reais (pico de volume ou queda de receita) para que o
modelo de Isolation Forest tenha o que detectar.

Uso: python seed_data.py
"""

import random
from datetime import date, timedelta

import pymysql

DB_HOST = '100.72.104.123'
DB_NAME = 'solutec_db'
DB_USER = 'solutec_remote'
DB_PASS = 'solutec123'
DB_PORT = 3306

DIAS_HISTORICO = 90
MIN_ANOMALIAS = 5
MAX_ANOMALIAS = 8


def conectar():
    """Abre uma conexão com o MariaDB do projeto."""
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        port=DB_PORT,
        charset='utf8mb4',
    )


def buscar_produtos(conn):
    """Retorna a lista de (id, preco) dos produtos já cadastrados na loja."""
    with conn.cursor() as cur:
        cur.execute("SELECT id, preco FROM produtos")
        return cur.fetchall()


def escolher_dias_anomalos(dias):
    """Sorteia entre MIN_ANOMALIAS e MAX_ANOMALIAS dias do período para receber anomalias."""
    quantidade = random.randint(MIN_ANOMALIAS, MAX_ANOMALIAS)
    return set(random.sample(dias, quantidade))


def gerar_vendas_normais(produtos):
    """Gera as vendas de um dia comum: 3 a 8 transações com valores próximos do preço de tabela."""
    vendas = []
    for _ in range(random.randint(3, 8)):
        produto_id, preco = random.choice(produtos)
        quantidade = random.randint(1, 3)
        variacao = random.uniform(0.95, 1.05)
        valor_total = round(float(preco) * quantidade * variacao, 2)
        vendas.append((produto_id, quantidade, valor_total))
    return vendas


def gerar_vendas_pico_volume(produtos):
    """Gera as vendas de um dia com pico de volume: ~3x mais transações que o normal."""
    vendas = []
    for _ in range(random.randint(18, 24)):
        produto_id, preco = random.choice(produtos)
        quantidade = random.randint(2, 5)
        valor_total = round(float(preco) * quantidade * random.uniform(0.95, 1.05), 2)
        vendas.append((produto_id, quantidade, valor_total))
    return vendas


def gerar_vendas_queda_receita(produtos):
    """Gera as vendas de um dia com queda de receita: poucas transações e valores bem baixos."""
    vendas = []
    for _ in range(random.randint(1, 2)):
        produto_id, preco = random.choice(produtos)
        quantidade = 1
        valor_total = round(float(preco) * 0.2 * random.uniform(0.9, 1.1), 2)
        vendas.append((produto_id, quantidade, valor_total))
    return vendas


def gerar_vendas_do_dia(produtos, anomalo):
    """Decide o tipo de dia (normal ou anômalo) e retorna a lista de vendas geradas."""
    if not anomalo:
        return gerar_vendas_normais(produtos)
    if random.random() < 0.5:
        return gerar_vendas_pico_volume(produtos)
    return gerar_vendas_queda_receita(produtos)


def inserir_vendas(conn, vendas_por_dia):
    """Insere na tabela vendas a lista de (dia, produto_id, quantidade, valor_total)."""
    total_inserido = 0
    with conn.cursor() as cur:
        for dia, produto_id, quantidade, valor_total in vendas_por_dia:
            cur.execute(
                "INSERT INTO vendas (produto_id, quantidade, valor_total, data_venda) "
                "VALUES (%s, %s, %s, %s)",
                (produto_id, quantidade, valor_total, dia),
            )
            total_inserido += 1
    conn.commit()
    return total_inserido


def main():
    conn = conectar()
    try:
        produtos = buscar_produtos(conn)
        if not produtos:
            raise RuntimeError('Tabela produtos está vazia — rode banco.sql da loja antes do seed.')

        hoje = date.today()
        dias = [hoje - timedelta(days=i) for i in range(DIAS_HISTORICO)]
        dias_anomalos = escolher_dias_anomalos(dias)

        vendas_por_dia = []
        for dia in dias:
            for produto_id, quantidade, valor_total in gerar_vendas_do_dia(produtos, dia in dias_anomalos):
                vendas_por_dia.append((dia, produto_id, quantidade, valor_total))

        total_inserido = inserir_vendas(conn, vendas_por_dia)
        print(
            f"Seed concluído: {total_inserido} vendas inseridas em {DIAS_HISTORICO} dias "
            f"({len(dias_anomalos)} dias anômalos)."
        )
    finally:
        conn.close()


if __name__ == '__main__':
    main()
