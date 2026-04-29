# Etapa Inicial - MySQL

## 1. Papel do MySQL no TCC

Para a parte relacional do trabalho, o MySQL pode ser usado como referencia de banco tradicional baseado em:

- esquema rigido;
- linguagem SQL padronizada;
- integridade relacional;
- ampla adocao em sistemas web e corporativos.

Isso ajuda no TCC porque permite relacionar vulnerabilidades bem documentadas com testes praticos de desempenho e seguranca.

## 2. Vulnerabilidades que valem priorizar no MySQL

### 2.1 Injecao SQL

E a vulnerabilidade mais classica em bancos relacionais. Ela normalmente surge quando a aplicacao concatena entrada do usuario diretamente na query.

Pontos para discutir no texto:

- falha nao esta no MySQL isoladamente, mas no uso inseguro da aplicacao;
- impacto pode incluir leitura, alteracao ou exclusao indevida de dados;
- mitigacao principal: consultas parametrizadas e validacao de entrada.

### 2.2 Falhas de autenticacao

Casos relevantes:

- senhas fracas;
- reutilizacao de credenciais;
- contas sem rotacao;
- usuarios com acesso remoto desnecessario.

### 2.3 Privilegios excessivos

Muito comum em sistemas academicos e pequenos projetos:

- usuario da aplicacao com permissao `DROP`, `ALTER` ou acesso total;
- falta de separacao entre usuario de leitura e escrita;
- uso do usuario `root` na aplicacao.

### 2.4 Configuracao insegura

Exemplos de pontos para citar:

- portas expostas sem restricao;
- ausencia de TLS;
- logs insuficientes;
- backup sem protecao;
- banco acessivel externamente sem necessidade.

### 2.5 Criptografia e protecao de dados

Mesmo quando a injecao nao ocorre, a exposicao de dados sensiveis cresce se houver:

- dados em repouso sem protecao;
- trafego sem criptografia;
- armazenamento de senha sem hash forte na camada da aplicacao.

## 3. Recorte experimental recomendado

Para nao deixar o TCC amplo demais, vale trabalhar com um mesmo mini-cenario nos dois bancos:

- cadastro de usuarios;
- autenticacao;
- consulta de produtos;
- registro de acessos;
- operacoes de insercao, consulta e atualizacao.

Esse recorte permite medir desempenho e discutir seguranca ao mesmo tempo.

## 4. Metricas para levantamento grafico

Para comparar MySQL e MongoDB com justica, use as mesmas operacoes e o mesmo volume de dados.

### 4.1 Metricas principais

- tempo medio de insercao;
- tempo medio de consulta por chave;
- tempo medio de consulta com filtro;
- tempo medio de atualizacao;
- throughput em operacoes por segundo;
- uso medio de CPU;
- uso medio de memoria;
- taxa de sucesso das operacoes;
- tempo medio de resposta em autenticacao.

### 4.2 Volumes sugeridos

- 100 registros;
- 1.000 registros;
- 10.000 registros;
- 100.000 registros.

Isso costuma ser suficiente para gerar graficos com crescimento visivel sem exigir infraestrutura pesada.

## 5. Graficos recomendados para o TCC

### Grafico 1 - Tempo medio de insercao

- eixo X: volume de dados;
- eixo Y: tempo medio em ms;
- series: MySQL e MongoDB.

### Grafico 2 - Tempo medio de consulta por identificador

- eixo X: volume de dados;
- eixo Y: tempo medio em ms;
- series: MySQL e MongoDB.

### Grafico 3 - Tempo medio de atualizacao

- eixo X: volume de dados;
- eixo Y: tempo medio em ms;
- series: MySQL e MongoDB.

### Grafico 4 - Throughput

- eixo X: tipo de operacao;
- eixo Y: operacoes por segundo;
- series: MySQL e MongoDB.

### Grafico 5 - Consumo de recursos

- eixo X: banco de dados;
- eixo Y: valor medio;
- series separadas para CPU e memoria.

## 6. Como ligar desempenho ao tema de vulnerabilidade

Esse ponto e importante: o tema principal do TCC e vulnerabilidade, nao benchmark puro.

Entao o desempenho deve entrar como apoio analitico, por exemplo:

- impacto de configuracoes seguras no tempo de resposta;
- diferenca entre operacoes simples e operacoes com validacoes mais rigorosas;
- efeito de indices e modelagem sobre exposicao e desempenho;
- custo de controles adicionais de seguranca.

Uma abordagem boa e separar:

- analise de seguranca: quais vulnerabilidades sao mais provaveis e mais criticas;
- analise de desempenho: como cada modelo responde sob carga semelhante;
- sintese comparativa: seguranca, desempenho e trade-offs.

## 7. Hipotese inicial para o texto

Uma hipotese defensavel para o TCC e:

"Embora o MySQL apresente maior maturidade em mecanismos de controle e integridade, sua ampla utilizacao em aplicacoes tradicionais o torna fortemente associado a falhas classicas de injecao SQL e privilegios excessivos. Em contrapartida, o MongoDB tende a oferecer maior flexibilidade estrutural, mas introduz riscos especificos ligados a consultas dinamicas e configuracoes inseguras. Assim, a exposicao a vulnerabilidades depende menos do modelo de banco isoladamente e mais da combinacao entre arquitetura, configuracao e praticas de desenvolvimento."

## 8. Proximo passo pratico

Nesta etapa do MySQL, o ideal e voce executar:

1. criacao do banco e das tabelas;
2. carga inicial de dados;
3. medicao de insercao, leitura e atualizacao;
4. registro dos resultados na planilha padrao;
5. repeticao futura do mesmo roteiro no MongoDB.

## 9. O que voce ja pode escrever no TCC

Com base nesta etapa, ja da para desenvolver:

- a subsecao de MySQL na fundamentacao teorica;
- a parte metodologica dos testes;
- a definicao das metricas e dos graficos comparativos;
- a justificativa do recorte experimental.
