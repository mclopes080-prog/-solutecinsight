-- ============================================================
-- SolutecAI Dashboard — views analíticas
-- View 1 usa 2 CTEs encadeadas (agregação diária + desvio/zscore).
-- View 2 consolida produtos + vendas + anomalias_detectadas.
-- ============================================================

USE solutec_db;

-- View 1: resumo diário de vendas com desvio em relação à média (zscore)
CREATE OR REPLACE VIEW vw_resumo_vendas AS
WITH vendas_diarias AS (
  SELECT
    data_venda,
    SUM(quantidade)  AS total_quantidade,
    SUM(valor_total) AS total_receita,
    COUNT(*)         AS num_transacoes
  FROM vendas
  GROUP BY data_venda
),
desvios AS (
  SELECT
    data_venda,
    total_quantidade,
    total_receita,
    num_transacoes,
    AVG(total_receita) OVER ()    AS media_receita,
    STDDEV(total_receita) OVER () AS desvio_receita
  FROM vendas_diarias
)
SELECT
  data_venda,
  total_quantidade,
  total_receita,
  num_transacoes,
  ROUND(media_receita, 2)  AS media_receita,
  ROUND(desvio_receita, 2) AS desvio_receita,
  ROUND((total_receita - media_receita) / NULLIF(desvio_receita, 0), 4) AS zscore
FROM desvios;

-- View 2: consolida produtos + vendas + anomalias detectadas no dia da venda.
-- As agregações de vendas e de anomalias são pré-calculadas em subconsultas
-- para não multiplicar valores quando um produto tem várias vendas no mesmo
-- dia de uma anomalia (join direto por data causaria fan-out nas somas).
CREATE OR REPLACE VIEW vw_produtos_vendas AS
SELECT
  p.id                             AS id_produto,
  p.nome                           AS produto_nome,
  p.categoria,
  p.preco                          AS preco_unitario,
  COALESCE(vs.total_vendido, 0)    AS total_vendido,
  COALESCE(vs.receita_total, 0)    AS receita_total,
  COALESCE(an.anomalias_count, 0)  AS anomalias_count
FROM produtos p
LEFT JOIN (
  SELECT produto_id,
         SUM(quantidade)  AS total_vendido,
         SUM(valor_total) AS receita_total
  FROM vendas
  GROUP BY produto_id
) vs ON vs.produto_id = p.id
LEFT JOIN (
  SELECT v.produto_id, COUNT(DISTINCT a.id_anomalia) AS anomalias_count
  FROM vendas v
  JOIN anomalias_detectadas a ON a.data_ref = v.data_venda
  GROUP BY v.produto_id
) an ON an.produto_id = p.id;
