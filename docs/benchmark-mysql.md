# Benchmark MySQL

## Objetivo

Gerar um CSV padronizado com metricas de desempenho do MySQL para uso nos graficos do TCC.

## O que o script mede

- `insert`: insercao em lote de produtos;
- `select_id`: consultas por identificador;
- `select_filtro`: consultas com filtro por categoria e faixa de preco;
- `update`: atualizacao de estoque.

Para cada execucao, o script registra:

- tempo em milissegundos;
- throughput em operacoes por segundo;
- uso de CPU do container;
- uso de memoria do container.

Se o `docker stats` nao estiver disponivel, o benchmark continua rodando e marca a observacao `docker_stats_indisponivel` no CSV.

## Preparacao

1. Suba o MySQL:

```powershell
docker compose -f bench/docker-compose.yml up -d
```

2. Instale a dependencia Python:

```powershell
pip install -r bench/requirements.txt
```

## Execucao padrao

```powershell
python bench/scripts/mysql_benchmark.py
```

Isso executa:

- volumes `100`, `1000` e `10000`;
- `5` repeticoes por operacao.

## Exemplos uteis

Executar um teste mais rapido:

```powershell
python bench/scripts/mysql_benchmark.py --volumes 100 1000 --repeat 3
```

Salvar em arquivo especifico:

```powershell
python bench/scripts/mysql_benchmark.py --output bench/results/mysql_teste_01.csv
```

## Saida

Os resultados sao gravados em `bench/results/` com nome semelhante a:

```text
mysql_benchmark_20260426_142500.csv
```

## Gerar graficos automaticamente

```powershell
python bench/scripts/plot_mysql_results.py --input bench/results/mysql_benchmark_20260426_142500.csv
```

Os PNGs sao gerados em `bench/results/plots/`.

## Graficos produzidos

- `mysql_tempo_medio.png`;
- `mysql_throughput_medio.png`;
- `mysql_recursos_medios.png`.

## Alternativa manual

Se preferir, voce tambem pode importar o CSV no Excel, Google Sheets ou Python e gerar:

- grafico de linhas para `tempo_ms` por `volume_registros`;
- grafico de colunas para `throughput_ops_s` por operacao;
- grafico de colunas para `cpu_percent` e `memoria_mb`.

## Observacao metodologica

Para manter comparabilidade com o MongoDB depois, use:

- os mesmos volumes;
- as mesmas quantidades de repeticao;
- operacoes equivalentes;
- o mesmo ambiente de hardware.

Se preferir usar um MySQL ja instalado fora do Docker, ajuste `--host`, `--port`, `--user`, `--password` e `--database`.

No ambiente deste projeto, o container de laboratorio expoe a porta `3307` no host para evitar conflito com instalacoes locais de MySQL na `3306`.
