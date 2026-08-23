-- ============================================================
-- SolutecAI Dashboard — função reutilizável de categoria de risco
-- Usada pela stored procedure e pelas views para classificar anomalias.
-- ============================================================

USE solutec_db;

DROP FUNCTION IF EXISTS fn_categoria_risco;

DELIMITER $$
CREATE FUNCTION fn_categoria_risco(score DECIMAL(6,4))
RETURNS VARCHAR(10)
DETERMINISTIC
NO SQL
BEGIN
  IF score >= 0.7 THEN
    RETURN 'ALTO';
  ELSEIF score >= 0.4 THEN
    RETURN 'MÉDIO';
  ELSE
    RETURN 'BAIXO';
  END IF;
END$$
DELIMITER ;
