<?php
// Endpoint JSON do dashboard: executa a stored procedure sp_dashboard_indicadores
// e devolve os indicadores agregados + a lista paginada de anomalias.
header('Content-Type: application/json; charset=utf-8');
require_once '../includes/db.php';

try {
    $inicio = isset($_GET['inicio']) ? $_GET['inicio'] : date('Y-m-d', strtotime('-90 days'));
    $fim    = isset($_GET['fim'])    ? $_GET['fim']    : date('Y-m-d');
    $limite = isset($_GET['limite']) ? (int) $_GET['limite'] : 10;
    $offset = isset($_GET['offset']) ? (int) $_GET['offset'] : 0;

    $padraoData = '/^\d{4}-\d{2}-\d{2}$/';
    if (!preg_match($padraoData, $inicio) || !preg_match($padraoData, $fim)) {
        throw new Exception('Datas inválidas. Use o formato YYYY-MM-DD.');
    }

    if ($limite < 1 || $limite > 100) {
        $limite = 10;
    }
    if ($offset < 0) {
        $offset = 0;
    }

    $stmt = $pdo->prepare('CALL sp_dashboard_indicadores(?, ?, ?, ?)');
    $stmt->execute([$inicio, $fim, $limite, $offset]);

    $indicadoresRows = $stmt->fetchAll(PDO::FETCH_ASSOC);
    $indicadores = $indicadoresRows[0] ?? [
        'total_vendas' => 0,
        'receita_total' => 0,
        'ticket_medio' => 0,
        'produto_mais_vendido' => null,
    ];

    $anomalias = [];
    if ($stmt->nextRowset()) {
        $anomalias = $stmt->fetchAll(PDO::FETCH_ASSOC);
    }

    // PDO/MySQL fecha o cursor da CALL só depois de consumir todos os rowsets
    $stmt->closeCursor();

    echo json_encode([
        'indicadores' => $indicadores,
        'anomalias' => $anomalias,
    ], JSON_UNESCAPED_UNICODE);
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode(['erro' => $e->getMessage()], JSON_UNESCAPED_UNICODE);
}
