# TCC - Vulnerabilidades em Bancos de Dados Relacionais e Nao Relacionais

Este repositorio concentra a parte pratica do TCC com foco em:

- analise de vulnerabilidades em MySQL e MongoDB;
- montagem de ambiente controlado para testes;
- coleta de metricas de desempenho para comparacao grafica.

## Estrutura inicial

- `docs/mysql-etapa-inicial.md`: recorte do MySQL para o TCC, vulnerabilidades, cenarios e plano de graficos.
- `docs/benchmark-mysql.md`: como executar o benchmark e gerar os graficos.
- `docs/mongodb-etapa-inicial.md`: recorte do MongoDB para o TCC, vulnerabilidades, cenarios e plano de graficos.
- `docs/benchmark-mongodb.md`: como executar o benchmark e gerar os graficos.
- `bench/docker-compose.yml`: ambiente minimo de laboratorio com MySQL.
- `bench/mysql/schema.sql`: esquema inicial para testes.
- `bench/mysql/seed.sql`: dados basicos para popular o banco.
- `bench/scripts/mysql_benchmark.py`: coleta de metricas em CSV.
- `bench/scripts/plot_mysql_results.py`: gera graficos PNG a partir do CSV.
- `bench/scripts/mongodb_benchmark.py`: coleta de metricas em CSV para MongoDB.
- `bench/scripts/plot_mongodb_results.py`: gera graficos PNG a partir do CSV do MongoDB.
- `bench/templates/coleta-desempenho.csv`: modelo para registrar resultados.

## Objetivo desta etapa

Nesta primeira fase, o foco e estruturar o estudo do MySQL para que os mesmos testes possam ser repetidos depois no MongoDB, mantendo comparabilidade.
