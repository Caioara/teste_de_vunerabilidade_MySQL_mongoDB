# Etapa Inicial - MongoDB

## 1. Papel do MongoDB no TCC

Para a parte nao relacional do trabalho, o MongoDB pode ser usado como referencia de banco orientado a documentos baseado em:

- estrutura flexivel em documentos JSON-like;
- ausencia de esquema rigidamente fixo;
- escalabilidade horizontal;
- forte uso em aplicacoes web modernas e sistemas distribuidos.

Isso ajuda no TCC porque permite contrastar a flexibilidade do modelo NoSQL com os riscos de seguranca e comportamento de desempenho observados no MySQL.

## 2. Vulnerabilidades que valem priorizar no MongoDB

### 2.1 NoSQL Injection

E a vulnerabilidade mais classica em bancos nao relacionais orientados a documentos. Ela costuma surgir quando a aplicacao monta filtros dinamicos diretamente a partir da entrada do usuario.

Pontos para discutir no texto:

- a falha normalmente esta na aplicacao, nao apenas no banco;
- o impacto pode incluir bypass de autenticacao e leitura indevida;
- mitigacao principal: validacao de entrada e montagem segura de queries.

### 2.2 Falhas de autenticacao e exposicao indevida

Casos relevantes:

- servico exposto sem controle de acesso;
- usuarios com credenciais padrao;
- autenticacao desabilitada em ambiente improprio;
- acesso remoto sem restricao de rede.

### 2.3 Permissoes excessivas

Exemplos comuns:

- usuario da aplicacao com privilegios administrativos;
- ausencia de segregacao entre leitura e escrita;
- uso desnecessario de conta root.

### 2.4 Configuracao insegura

Exemplos de pontos para citar:

- porta exposta publicamente;
- ausencia de TLS;
- logs insuficientes;
- backups desprotegidos;
- replicacao configurada sem endurecimento de seguranca.

### 2.5 Protecao de dados

Mesmo sem exploracao direta de injecao, a exposicao aumenta quando houver:

- dados sensiveis sem criptografia adequada;
- trafego em texto claro;
- hashes fracos de senha na camada da aplicacao.

## 3. Recorte experimental recomendado

Para manter comparabilidade com o MySQL, vale usar o mesmo mini-cenario:

- cadastro de usuarios;
- autenticacao;
- consulta de produtos;
- registro de acessos;
- operacoes de insercao, consulta e atualizacao.

## 4. Metricas para levantamento grafico

Use as mesmas metricas do MySQL:

- tempo medio de insercao;
- tempo medio de consulta por identificador;
- tempo medio de consulta com filtro;
- tempo medio de atualizacao;
- throughput em operacoes por segundo;
- uso medio de CPU;
- uso medio de memoria;
- taxa de sucesso das operacoes;
- tempo medio de resposta em autenticacao.

## 5. Hipotese inicial para o texto

Uma hipotese defensavel para esta etapa e:

"Embora o MongoDB ofereca maior flexibilidade estrutural e boa adaptacao a dados semi-estruturados, essa mesma flexibilidade pode ampliar riscos de seguranca quando filtros e documentos sao montados de forma insegura pela aplicacao. Assim, o desempenho e a superficie de ataque do MongoDB devem ser avaliados em conjunto, especialmente em cenarios com consultas dinamicas e crescimento do volume de dados."

## 6. Proximo passo pratico

Nesta etapa do MongoDB, o ideal e executar:

1. criacao da base e das colecoes;
2. carga inicial de documentos;
3. medicao de insercao, leitura e atualizacao;
4. registro dos resultados na planilha padrao;
5. comparacao posterior com o MySQL.
