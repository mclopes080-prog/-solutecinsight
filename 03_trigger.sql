-- ============================================================
-- SolutecAI Dashboard — trigger de integridade em vendas
-- Garante que updates nunca deixem valor_total ou quantidade inválidos.
-- ============================================================

USE solutec_db;

DROP TRIGGER IF EXISTS tg_venda_valor_positivo;

DELIMITER $$
CREATE TRIGGER tg_venda_valor_positivo
BEFORE UPDATE ON vendas
FOR EACH ROW
BEGIN
  IF NEW.valor_total <= 0 THEN
    SET NEW.valor_total = ABS(NEW.valor_total);
  END IF;
  IF NEW.quantidade <= 0 THEN
    SET NEW.quantidade = 1;
  END IF;
END$$
DELIMITER ;
