"""
SolutecAI — API Flask que expõe o modelo de detecção de anomalias.

GET  /health   -> healthcheck simples (usado pelo n8n antes de chamar /predict)
POST /predict  -> recebe {"data_inicio": "YYYY-MM-DD", "data_fim": "YYYY-MM-DD"},
                  treina o Isolation Forest com todo o histórico de vendas,
                  filtra as anomalias para o período pedido, grava as novas
                  anomalias em anomalias_detectadas e devolve o relatório.
"""

import pymysql
from flask import Flask, jsonify, request

import model

DB_HOST = '100.72.104.123'
DB_NAME = 'solutec_db'
DB_USER = 'solutec_remote'
DB_PASS = 'solutec123'
DB_PORT = 3306

app = Flask(__name__)


def conectar_banco():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        port=DB_PORT,
        charset='utf8mb4',
    )


def salvar_anomalias(conn, anomalias):
    """Grava as anomalias detectadas em anomalias_detectadas, ignorando duplicatas (mesmo tipo + data_ref)."""
    with conn.cursor() as cur:
        for anomalia in anomalias:
            cur.execute(
                """
                INSERT INTO anomalias_detectadas (tipo, descricao, score, data_ref)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    descricao = VALUES(descricao),
                    score = VALUES(score)
                """,
                (anomalia['tipo'], anomalia['descricao'], anomalia['score'], anomalia['data_ref']),
            )
    conn.commit()


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'servico': 'SolutecAI'})


@app.route('/predict', methods=['POST'])
def predict():
    body = request.get_json(silent=True) or {}
    data_inicio = body.get('data_inicio')
    data_fim = body.get('data_fim')

    if not data_inicio or not data_fim:
        return jsonify({'erro': 'Informe data_inicio e data_fim no corpo da requisição.'}), 400

    conn = None
    try:
        conn = conectar_banco()
        dados = model.carregar_dados(conn)

        if dados.empty:
            return jsonify({'anomalias': [], 'total': 0, 'relatorio': 'Sem dados de vendas para treinar o modelo.'})

        modelo_treinado = model.treinar_modelo(dados)
        todas_anomalias = model.detectar_anomalias(modelo_treinado, dados)
        anomalias_do_periodo = model.filtrar_por_periodo(todas_anomalias, data_inicio, data_fim)

        salvar_anomalias(conn, anomalias_do_periodo)

        return jsonify({
            'anomalias': anomalias_do_periodo,
            'total': len(anomalias_do_periodo),
            'relatorio': model.formatar_relatorio(anomalias_do_periodo),
        })
    except Exception as erro:
        return jsonify({'erro': str(erro)}), 500
    finally:
        if conn is not None:
            conn.close()


if __name__ == '__main__':
    app.run(port=5000, debug=True)
