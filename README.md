# SolutecAI — Dashboard com Detecção de Anomalias

Dashboard analítico de vendas da Solutec Segurança Eletrônica com detecção automática de anomalias via Machine Learning, automação com n8n e alertas via Telegram.

---

## Estrutura do Projeto

```
solutecinsight/
├── ai/
│   ├── app.py              # API Flask (porta 5000)
│   ├── model.py            # Modelo Isolation Forest (funções puras)
│   ├── seed_data.py        # Gera dados de demo no banco
│   └── requirements.txt    # Dependências Python
├── n8n/
│   └── solutec_workflow.json  # Workflow de automação
├── sql/
│   ├── 01_tabelas.sql      # Tabelas: vendas, anomalias_detectadas
│   ├── 02_stored_procedure.sql  # sp_dashboard_indicadores
│   ├── 03_trigger.sql      # tg_venda_valor_positivo
│   ├── 04_function.sql     # fn_categoria_risco
│   └── 05_views.sql        # vw_resumo_vendas, vw_produtos_vendas
└── README.md

solutec/
└── dashboard/
    ├── api.php             # Endpoint JSON (chama a SP via PDO)
    ├── index.php           # Dashboard HTML/CSS
    ├── tsconfig.json       # Configuração TypeScript strict
    └── ts/
        └── dashboard.ts    # TypeScript (compilar antes de usar)
```

---

## Pré-requisitos

- XAMPP (Apache + MySQL/MariaDB)
- Python 3.10+
- Node.js 18+ (para o n8n)
- TypeScript: `npm install -g typescript`
- n8n: `npm install -g n8n`

---

## Setup — Siga Esta Ordem

### 1. Banco de Dados

Abra o terminal na pasta `solutecinsight/` e execute os SQLs em ordem:

```bash
mysql -u root solutec_db < sql/01_tabelas.sql
mysql -u root solutec_db < sql/02_stored_procedure.sql
mysql -u root solutec_db < sql/03_trigger.sql
mysql -u root solutec_db < sql/04_function.sql --default-character-set=utf8mb4
mysql -u root solutec_db < sql/05_views.sql
```

> **Atenção:** o arquivo `04_function.sql` **obrigatoriamente** precisa do flag `--default-character-set=utf8mb4` por causa do acento em `MÉDIO`. Sem ele, o texto fica corrompido no banco.

---

### 2. Dados de Demo

Instale as dependências Python e gere os dados:

```bash
cd ai
pip install -r requirements.txt
python seed_data.py
```

Isso insere ~90 dias de vendas sintéticas no banco, com 7-8 anomalias injetadas para o modelo detectar.

---

### 3. API de IA (Flask)

Inicie o servidor Flask em um terminal separado e **deixe ele rodando**:

```bash
cd ai
python app.py
```

Verifique se está funcionando acessando no navegador:
```
http://localhost:5000/health
```
Deve retornar: `{"status": "ok", "servico": "SolutecAI"}`

---

### 4. Dashboard PHP

- Coloque a pasta `solutec/` dentro do `htdocs` do XAMPP
- Certifique-se que Apache e MySQL estão **ON** no painel do XAMPP
- Acesse no navegador:

```
http://localhost/solutec/dashboard/
```

---

### 5. Compilar TypeScript

Dentro da pasta `dashboard/`, execute:

```bash
cd solutec/dashboard
tsc
```

Isso gera o `dashboard.js` a partir do `dashboard.ts`. Zero erros esperados.

---

### 6. n8n — Automação

**Iniciar o n8n:**
```bash
n8n start
```
Acesse: `http://localhost:5678`

**Configurar credenciais antes de importar o workflow:**

1. Settings → Credentials → Add Credential → **Telegram API**
   - Access Token: seu Bot Token do @BotFather

2. Settings → Credentials → Add Credential → **MySQL**
   - Host: `localhost`
   - Database: `solutec_db`
   - User: `root`
   - Password: *(sua senha do MySQL)*
   - Port: `3306`

**Importar o workflow:**

1. Workflows → Add Workflow → Import from File
2. Selecione `n8n/solutec_workflow.json`
3. Vincule as credenciais nos nodes de Telegram e MySQL
4. Atualize o **Chat ID** no node de Telegram com o seu ID
5. Salve (Ctrl+S)

**Testar:**

Clique em **Execute Workflow** para rodar manualmente. O Telegram deve receber uma mensagem com o relatório de anomalias.

---

## Credenciais de Desenvolvimento

```
Host MySQL:   localhost
Database:     solutec_db
User:         root
Port:         3306
```

---

## Tecnologias Utilizadas

| Camada | Tecnologia |
|---|---|
| Backend | PHP 8.x procedural + PDO |
| Banco de Dados | MariaDB / MySQL |
| Frontend | TypeScript (strict) + Bootstrap 5 |
| Machine Learning | Python + scikit-learn (Isolation Forest) |
| API de IA | Flask 3.0 |
| Automação | n8n |
| Notificações | Telegram Bot API |

---

## Anomalias Detectadas

O modelo identifica dois tipos de anomalia nas vendas diárias:

- **PICO_VOLUME** — quantidade vendida muito acima do padrão (possível fraude ou promoção indevida)
- **QUEDA_RECEITA** — receita muito abaixo do padrão (possível erro de precificação ou falta de estoque)

O algoritmo utilizado é o **Isolation Forest** com `contamination=0.08`, calibrado para o volume de dados do sistema.
