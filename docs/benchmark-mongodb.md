# Benchmark MongoDB

## Objetivo

Gerar um CSV padronizado com metricas de desempenho do MongoDB para uso nos graficos do TCC.

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

## Preparacao

1. Suba o MongoDB:

```powershell
docker compose -f bench/docker-compose.yml up -d mongodb
```

2. Instale as dependencias Python:

```powershell
pip install -r bench/requirements.txt
```

## Execucao padrao

```powershell
python bench/scripts/mongodb_benchmark.py
```

Isso executa:

- volumes `100`, `1000` e `10000`;
- `5` repeticoes por operacao.

## Exemplos uteis

Executar um teste maior:

```powershell
python bench/scripts/mongodb_benchmark.py --volumes 100 1000 10000 100000 --repeat 5
```

Salvar em arquivo especifico:

```powershell
python bench/scripts/mongodb_benchmark.py --output bench/results/mongodb_teste_01.csv
```

## Saida

Os resultados sao gravados em `bench/results/` com nome semelhante a:

```text
mongodb_benchmark_20260426_160000.csv
```

## Gerar graficos automaticamente

```powershell
python bench/scripts/plot_mongodb_results.py --input bench/results/mongodb_benchmark_20260426_160000.csv
```

Os PNGs sao gerados em `bench/results/plots/` ou no diretorio informado em `--output-dir`.

## Graficos produzidos

- `mongodb_tempo_medio.png`;
- `mongodb_throughput_medio.png`;
- `mongodb_recursos_medios.png`.

## Observacao metodologica

Para manter comparabilidade com o MySQL depois, use:

- os mesmos volumes;
- as mesmas quantidades de repeticao;
- operacoes equivalentes;
- o mesmo ambiente de hardware.

No ambiente deste projeto, o container de laboratorio expoe a porta `27018` no host para evitar conflito com instalacoes locais na `27017`.
