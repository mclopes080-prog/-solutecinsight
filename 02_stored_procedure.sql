-- ============================================================
-- SolutecAI Dashboard — stored procedure de indicadores + paginação
-- Depende de fn_categoria_risco (criada em 04_function.sql). A referência
-- só é resolvida em tempo de execução, então a ordem de criação dos
-- arquivos (01..05) pode ser seguida normalmente.
-- ============================================================

USE solutec_db;

DROP PROCEDURE IF EXISTS sp_dashboard_indicadores;

DELIMITER $$
CREATE PROCEDURE sp_dashboard_indicadores(
  IN p_inicio DATE,
  IN p_fim    DATE,
  IN p_limite INT,
  IN p_offset INT
)
BEGIN
  -- 1) Indicadores agregados do período
  SELECT
    COUNT(*)                                   AS total_vendas,
    COALESCE(SUM(v.valor_total), 0)            AS receita_total,
    COALESCE(ROUND(AVG(v.valor_total), 2), 0)  AS ticket_medio,
    (
      SELECT p.nome
      FROM vendas v2
      JOIN produtos p ON p.id = v2.produto_id
      WHERE v2.data_venda BETWEEN p_inicio AND p_fim
      GROUP BY p.id, p.nome
      ORDER BY SUM(v2.quantidade) DESC
      LIMIT 1
    ) AS produto_mais_vendido
  FROM vendas v
  WHERE v.data_venda BETWEEN p_inicio AND p_fim;

  -- 2) Lista paginada de anomalias detectadas no período
  SELECT
    a.id_anomalia,
    a.tipo,
    a.descricao,
    a.score,
    a.data_ref,
    a.resolvida,
    fn_categoria_risco(a.score) AS categoria_risco
  FROM anomalias_detectadas a
  WHERE a.data_ref BETWEEN p_inicio AND p_fim
  ORDER BY a.data_ref DESC
  LIMIT p_limite OFFSET p_offset;
END$$
DELIMITER ;
