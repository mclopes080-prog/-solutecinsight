-- ============================================================
-- SolutecAI Dashboard — novas tabelas
-- Adicionadas por cima do banco existente da loja (solutec_db).
-- Não altera nenhuma tabela já existente (produtos, clientes, pedidos).
-- ============================================================

USE solutec_db;

-- Tabela de vendas (registros gerados pelo seed / usados pelo dashboard)
CREATE TABLE IF NOT EXISTS vendas (
  id_venda     INT AUTO_INCREMENT PRIMARY KEY,
  produto_id   INT NOT NULL,
  quantidade   INT NOT NULL DEFAULT 1,
  valor_total  DECIMAL(10,2) NOT NULL,
  data_venda   DATE NOT NULL,
  CONSTRAINT fk_venda_produto FOREIGN KEY (produto_id) REFERENCES produtos(id)
);

-- Tabela de anomalias detectadas pelo modelo de ML
CREATE TABLE IF NOT EXISTS anomalias_detectadas (
  id_anomalia  INT AUTO_INCREMENT PRIMARY KEY,
  tipo         ENUM('PICO_VOLUME','QUEDA_RECEITA') NOT NULL,
  descricao    VARCHAR(255) NOT NULL,
  score        DECIMAL(6,4) NOT NULL,
  data_ref     DATE NOT NULL,
  detectada_em DATETIME DEFAULT CURRENT_TIMESTAMP,
  resolvida    TINYINT(1) DEFAULT 0,
  CONSTRAINT uq_anomalia_tipo_data UNIQUE (tipo, data_ref)
);

-- Índices de apoio às consultas do dashboard (período + junções)
CREATE INDEX idx_vendas_data ON vendas(data_venda);
CREATE INDEX idx_anomalias_data ON anomalias_detectadas(data_ref);
