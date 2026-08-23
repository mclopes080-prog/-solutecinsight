// SolutecAI Dashboard — lógica do painel analítico.
// Cada função tem uma única responsabilidade: buscar dados, renderizar,
// filtrar ou inicializar. Nenhum acesso ao DOM usa "!" — sempre guard com if.

interface Indicador {
  total_vendas: number;
  receita_total: string;
  ticket_medio: string;
  produto_mais_vendido: string | null;
}

interface Anomalia {
  id_anomalia: number;
  tipo: string;
  descricao: string;
  score: string;
  data_ref: string;
  categoria_risco: string;
  resolvida: number;
}

interface Filtros {
  inicio: string;
  fim: string;
  limite: number;
  offset: number;
}

interface RespostaApi {
  indicadores: Indicador;
  anomalias: Anomalia[];
}

let offsetAtual = 0;
const ITENS_POR_PAGINA = 10;

function ehRespostaValida(dados: unknown): dados is RespostaApi {
  if (typeof dados !== 'object' || dados === null) {
    return false;
  }
  return 'indicadores' in dados && 'anomalias' in dados;
}

function montarQueryString(filtros: Filtros): string {
  const params = new URLSearchParams({
    inicio: filtros.inicio,
    fim: filtros.fim,
    limite: String(filtros.limite),
    offset: String(filtros.offset),
  });
  return params.toString();
}

// [BUSCA] async, fetch, try/catch, retorna dados ou null
async function buscarIndicadores(filtros: Filtros): Promise<Indicador | null> {
  try {
    const resposta = await fetch(`api.php?${montarQueryString(filtros)}`);
    if (!resposta.ok) {
      return null;
    }
    const dados: unknown = await resposta.json();
    if (!ehRespostaValida(dados)) {
      return null;
    }
    return dados.indicadores;
  } catch (erro) {
    console.error('Falha ao buscar indicadores:', erro);
    return null;
  }
}

// [BUSCA] async, fetch, try/catch
async function buscarAnomalias(filtros: Filtros): Promise<Anomalia[]> {
  try {
    const resposta = await fetch(`api.php?${montarQueryString(filtros)}`);
    if (!resposta.ok) {
      return [];
    }
    const dados: unknown = await resposta.json();
    if (!ehRespostaValida(dados)) {
      return [];
    }
    return dados.anomalias;
  } catch (erro) {
    console.error('Falha ao buscar anomalias:', erro);
    return [];
  }
}

function formatarMoeda(valor: string | number): string {
  const numero = typeof valor === 'string' ? Number(valor) : valor;
  if (Number.isNaN(numero)) {
    return 'R$ 0,00';
  }
  return numero.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}

// [RENDER] só renderiza cards — sem fetch, sem lógica de negócio
function renderizarIndicadores(indicador: Indicador | null): void {
  const elVendas = document.getElementById('card-vendas');
  if (elVendas) {
    elVendas.textContent = indicador ? String(indicador.total_vendas) : '-';
  }

  const elReceita = document.getElementById('card-receita');
  if (elReceita) {
    elReceita.textContent = indicador ? formatarMoeda(indicador.receita_total) : '-';
  }

  const elTicket = document.getElementById('card-ticket');
  if (elTicket) {
    elTicket.textContent = indicador ? formatarMoeda(indicador.ticket_medio) : '-';
  }

  const elProduto = document.getElementById('card-produto-top');
  if (elProduto) {
    elProduto.textContent = indicador && indicador.produto_mais_vendido ? indicador.produto_mais_vendido : '-';
  }
}

function classeBadgeRisco(categoria: string): string {
  if (categoria === 'ALTO') {
    return 'badge bg-danger';
  }
  if (categoria === 'MÉDIO') {
    return 'badge bg-warning text-dark';
  }
  return 'badge bg-success';
}

function classeLinhaRisco(categoria: string): string {
  if (categoria === 'ALTO') {
    return 'risco-alto';
  }
  if (categoria === 'MÉDIO') {
    return 'risco-medio';
  }
  return 'risco-baixo';
}

function badgeTipo(tipo: string): string {
  const icone = tipo === 'PICO_VOLUME' ? '📈' : '📉';
  const rotulo = tipo === 'PICO_VOLUME' ? 'Pico de Volume' : 'Queda de Receita';
  return `<span class="badge bg-secondary">${icone} ${rotulo}</span>`;
}

// [RENDER] renderiza lista de anomalias
function renderizarAnomalias(anomalias: Anomalia[]): void {
  const corpoTabela = document.getElementById('tabela-anomalias-corpo');
  if (!corpoTabela) {
    return;
  }

  const elContadorAnomalias = document.getElementById('card-anomalias');
  if (elContadorAnomalias) {
    elContadorAnomalias.textContent = String(anomalias.length);
  }

  corpoTabela.innerHTML = '';

  if (anomalias.length === 0) {
    const linhaVazia = document.createElement('tr');
    linhaVazia.innerHTML = '<td colspan="5" class="text-center text-muted">Nenhuma anomalia no período.</td>';
    corpoTabela.appendChild(linhaVazia);
    return;
  }

  for (const anomalia of anomalias) {
    const linha = document.createElement('tr');
    linha.className = classeLinhaRisco(anomalia.categoria_risco);
    linha.innerHTML = `
      <td>${anomalia.data_ref}</td>
      <td>${badgeTipo(anomalia.tipo)}</td>
      <td class="col-descricao">${anomalia.descricao}</td>
      <td><span class="${classeBadgeRisco(anomalia.categoria_risco)}">${anomalia.categoria_risco}</span></td>
      <td class="col-score">${Number(anomalia.score).toFixed(2)}</td>
    `;
    corpoTabela.appendChild(linha);
  }
}

// [HIGHER-ORDER] filtro por nível de risco
const filtrarPorRisco = (nivel: string) => (anomalias: Anomalia[]): Anomalia[] =>
  nivel === 'TODOS' ? anomalias : anomalias.filter((a) => a.categoria_risco === nivel);

function obterFiltrosDaTela(): Filtros {
  const inputInicio = document.getElementById('filtro-inicio');
  const inputFim = document.getElementById('filtro-fim');

  const inicioPadrao = new Date(Date.now() - 90 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10);
  const fimPadrao = new Date().toISOString().slice(0, 10);

  const inicio = inputInicio instanceof HTMLInputElement && inputInicio.value ? inputInicio.value : inicioPadrao;
  const fim = inputFim instanceof HTMLInputElement && inputFim.value ? inputFim.value : fimPadrao;

  return { inicio, fim, limite: ITENS_POR_PAGINA, offset: offsetAtual };
}

let ultimasAnomalias: Anomalia[] = [];

function aplicarFiltroDeRisco(): void {
  const seletorRisco = document.getElementById('filtro-risco');
  const nivel = seletorRisco instanceof HTMLSelectElement ? seletorRisco.value : 'TODOS';
  renderizarAnomalias(filtrarPorRisco(nivel)(ultimasAnomalias));
}

// [INIT] inicializa tudo
async function init(): Promise<void> {
  const filtros = obterFiltrosDaTela();
  const [indicador, anomalias] = await Promise.all([
    buscarIndicadores(filtros),
    buscarAnomalias(filtros),
  ]);

  ultimasAnomalias = anomalias;

  renderizarIndicadores(indicador);
  aplicarFiltroDeRisco();

  const elPagina = document.getElementById('indicador-pagina');
  if (elPagina) {
    elPagina.textContent = `Página ${offsetAtual / ITENS_POR_PAGINA + 1}`;
  }
}

function configurarEventos(): void {
  const btnFiltrar = document.getElementById('btn-filtrar');
  if (btnFiltrar) {
    btnFiltrar.addEventListener('click', () => {
      offsetAtual = 0;
      void init();
    });
  }

  const seletorRisco = document.getElementById('filtro-risco');
  if (seletorRisco) {
    seletorRisco.addEventListener('change', aplicarFiltroDeRisco);
  }

  const btnAnterior = document.getElementById('btn-anterior');
  if (btnAnterior) {
    btnAnterior.addEventListener('click', () => {
      offsetAtual = Math.max(0, offsetAtual - ITENS_POR_PAGINA);
      void init();
    });
  }

  const btnProximo = document.getElementById('btn-proximo');
  if (btnProximo) {
    btnProximo.addEventListener('click', () => {
      offsetAtual += ITENS_POR_PAGINA;
      void init();
    });
  }
}

document.addEventListener('DOMContentLoaded', () => {
  configurarEventos();
  void init();
});
