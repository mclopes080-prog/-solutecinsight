<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>SolutecAI — Dashboard de Vendas</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        :root {
            --sc-bg: #0d1117;
            --sc-sidebar: #161b22;
            --sc-accent: #00ff88;
            --sc-alerta: #ff6b35;
            --sc-texto: #e6edf3;
            --sc-borda: #30363d;
        }
        body {
            background-color: var(--sc-bg);
            color: var(--sc-texto);
            min-height: 100vh;
        }
        .sc-sidebar {
            background-color: var(--sc-sidebar);
            min-height: 100vh;
            border-right: 1px solid var(--sc-borda);
        }
        .sc-sidebar .navbar-brand {
            color: var(--sc-accent);
            font-weight: bold;
            font-size: 1.3rem;
        }
        .sc-sidebar a.nav-link {
            color: var(--sc-texto);
            border-radius: 6px;
        }
        .sc-sidebar a.nav-link.active,
        .sc-sidebar a.nav-link:hover {
            background-color: rgba(0, 255, 136, 0.1);
            color: var(--sc-accent);
        }
        .sc-card {
            background-color: var(--sc-sidebar);
            border: 1px solid var(--sc-borda);
            border-radius: 10px;
        }
        .sc-card .sc-card-label {
            color: #8b949e;
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }
        .sc-card .sc-card-valor {
            font-size: 1.6rem;
            font-weight: 700;
            color: var(--sc-texto);
        }
        .sc-card.sc-card-alerta .sc-card-valor {
            color: var(--sc-alerta);
        }
        .form-control, .form-select {
            background-color: #0d1117;
            border: 1px solid var(--sc-borda);
            color: var(--sc-texto);
        }
        .form-control:focus, .form-select:focus {
            background-color: #0d1117;
            color: var(--sc-texto);
            border-color: var(--sc-accent);
            box-shadow: 0 0 0 0.2rem rgba(0, 255, 136, 0.15);
        }
        .btn-sc-primary {
            background-color: var(--sc-accent);
            border-color: var(--sc-accent);
            color: #0d1117;
            font-weight: 600;
        }
        .btn-sc-primary:hover {
            background-color: #00e07a;
            color: #0d1117;
        }
        table.sc-tabela {
            --bs-table-bg: transparent;
            --bs-table-color: var(--sc-texto);
            color: var(--sc-texto);
        }
        table.sc-tabela th {
            color: #8b949e;
            border-bottom: 1px solid var(--sc-borda);
            font-size: 0.8rem;
            text-transform: uppercase;
            background-color: transparent;
            padding: 0.9rem 0.75rem;
        }
        table.sc-tabela td {
            border-bottom: 1px solid var(--sc-borda);
            vertical-align: middle;
            background-color: transparent;
            padding: 1rem 0.75rem;
            font-size: 0.95rem;
        }
        table.sc-tabela tbody tr {
            border-left: 4px solid transparent;
            transition: background-color 0.15s ease;
        }
        table.sc-tabela tbody tr:hover {
            background-color: rgba(255, 255, 255, 0.03) !important;
        }
        table.sc-tabela tbody tr.risco-alto {
            border-left-color: #f85149;
        }
        table.sc-tabela tbody tr.risco-medio {
            border-left-color: #ffc107;
        }
        table.sc-tabela tbody tr.risco-baixo {
            border-left-color: #3fb950;
        }
        table.sc-tabela .badge {
            font-size: 0.78rem;
            padding: 0.45em 0.7em;
        }
        table.sc-tabela .col-descricao {
            max-width: 420px;
            white-space: normal;
            line-height: 1.4;
        }
        table.sc-tabela .col-score {
            font-variant-numeric: tabular-nums;
            font-weight: 600;
        }
        .text-muted {
            color: #8b949e !important;
        }
    </style>
</head>
<body>
<div class="d-flex">
    <nav class="sc-sidebar d-flex flex-column p-3" style="width: 240px;">
        <a class="navbar-brand mb-4" href="../index.php">Solutec<span style="color:#e6edf3;">AI</span></a>
        <ul class="nav nav-pills flex-column mb-auto">
            <li class="nav-item mb-1">
                <a href="index.php" class="nav-link active">Dashboard</a>
            </li>
            <li class="nav-item mb-1">
                <a href="../index.php" class="nav-link" target="_blank" rel="noopener noreferrer">Voltar para a loja</a>
            </li>
        </ul>
        <hr style="border-color: var(--sc-borda);">
        <small class="text-muted">Solutec Segurança Eletrônica</small>
    </nav>

    <main class="flex-fill p-4">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h1 class="h3 mb-0">Painel de Vendas &amp; Anomalias</h1>
        </div>

        <div class="sc-card p-3 mb-4">
            <div class="row g-2 align-items-end">
                <div class="col-auto">
                    <label for="filtro-inicio" class="form-label small text-muted mb-1">Início</label>
                    <input type="date" id="filtro-inicio" class="form-control form-control-sm">
                </div>
                <div class="col-auto">
                    <label for="filtro-fim" class="form-label small text-muted mb-1">Fim</label>
                    <input type="date" id="filtro-fim" class="form-control form-control-sm">
                </div>
                <div class="col-auto">
                    <label for="filtro-risco" class="form-label small text-muted mb-1">Risco</label>
                    <select id="filtro-risco" class="form-select form-select-sm">
                        <option value="TODOS">Todos</option>
                        <option value="ALTO">Alto</option>
                        <option value="MÉDIO">Médio</option>
                        <option value="BAIXO">Baixo</option>
                    </select>
                </div>
                <div class="col-auto">
                    <button id="btn-filtrar" class="btn btn-sc-primary btn-sm">Filtrar</button>
                </div>
            </div>
        </div>

        <div class="row g-3 mb-4">
            <div class="col-6 col-lg-3">
                <div class="sc-card p-3">
                    <div class="sc-card-label">Total de Vendas</div>
                    <div class="sc-card-valor" id="card-vendas">-</div>
                </div>
            </div>
            <div class="col-6 col-lg-3">
                <div class="sc-card p-3">
                    <div class="sc-card-label">Receita Total</div>
                    <div class="sc-card-valor" id="card-receita">-</div>
                </div>
            </div>
            <div class="col-6 col-lg-3">
                <div class="sc-card p-3">
                    <div class="sc-card-label">Ticket Médio</div>
                    <div class="sc-card-valor" id="card-ticket">-</div>
                </div>
            </div>
            <div class="col-6 col-lg-3">
                <div class="sc-card p-3 sc-card-alerta">
                    <div class="sc-card-label">Anomalias Detectadas</div>
                    <div class="sc-card-valor" id="card-anomalias">-</div>
                </div>
            </div>
        </div>

        <div class="sc-card p-3 mb-3">
            <div class="text-muted small mb-2">Produto mais vendido no período: <span id="card-produto-top">-</span></div>
        </div>

        <div class="sc-card p-3">
            <div class="d-flex justify-content-between align-items-center mb-3">
                <h2 class="h6 mb-0">Anomalias Detectadas</h2>
                <div class="d-flex align-items-center gap-2">
                    <button id="btn-anterior" class="btn btn-outline-light btn-sm">&laquo; Anterior</button>
                    <span id="indicador-pagina" class="small text-muted">Página 1</span>
                    <button id="btn-proximo" class="btn btn-outline-light btn-sm">Próximo &raquo;</button>
                </div>
            </div>
            <div class="table-responsive">
                <table class="table sc-tabela mb-0">
                    <thead>
                        <tr>
                            <th>Data</th>
                            <th>Tipo</th>
                            <th>Descrição</th>
                            <th>Risco</th>
                            <th>Score</th>
                        </tr>
                    </thead>
                    <tbody id="tabela-anomalias-corpo">
                        <tr><td colspan="5" class="text-center text-muted">Carregando...</td></tr>
                    </tbody>
                </table>
            </div>
        </div>
    </main>
</div>

<script src="dashboard.js"></script>
</body>
</html>
