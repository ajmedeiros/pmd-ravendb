## Executando os testes

Os testes serão realizados no *cluster* criado na etapa anterior, rodando em uma máquina com as seguintes configurações:

>I5 3570K @3.8Ghz<br>
8gb ddr3<br>
13gb ssd (~7gb livres para o Docker)<br>
Linux Mint 19.1 - Cinnamon<br>

Configuração por nó:
> 2 Cores @3.8Ghz - compartilhado<br>
512mb ddr3<br>
7gb ssd - compartilhado com outros nós<br>
ravendb/ravendb:4.2.1

Configuração do cluster:
> 3 nós locais<br>
fator de replicação: 3<br>
nível de consistência: quórum (n/2 + 1)*<br>

<sub>* O RavenDB utiliza por padrão o algoritmo de quórum Raft. Não encontrei na documentação como alterar as configurações do algoritmo de quórum. Por padrão, ele está setado como (n/2)+1 nós, então os testes serão executados com essa configuração.<br>
Ref: https://ravendb.net/docs/article-page/4.2/python/glossary/raft-algorithm</sub>

### Falha nos nós e eleição do líder

Começaremos com um teste bem básico, sem sequer termos construído e populado nosso banco de dados ainda. Apenas para verificar o comportamento do RavenDB em caso de falha de nós e como o mesmo se recupera. Nossa topologia no momento se encontra exatamente igual à representada pela Figura 4, acima.

Primeiro, vamos desconectar o nó A, que é o atual líder. Essa etapa pode variar de acordo com a ordem em que você executou os passos anteriores, mas ainda assim deve ser muito simples.

1. Execute o comando <b>docker ps</b>.
2. Pegue o nome ou o *id* do *container* que é o atual líder.
<br><sub> > No meu caso, mapeei os nós de acordo com as portas, para facilitar a visualização (8080->A .. 8082->C)
3. Execute o comando <b>docker kill \<nome ou id do container></b>.

    docker kill stupefied_varahamihira

Volte para o *browser*, agora o nó A foi desconectado e não é possível acessá-lo pelo endereço http://172.17.0.2:8080. <br>
Acesse, então, o nó B: http://172.17.0.3:8080. O resultado deve ser algo parecido com o seguinte:

![Topologia com A off](/assets/A_off.png)<br>Figura 5 - Topologia com novo líder e nó A desconectado

Como estamos rodando o *Cluster* locamelmente, a eleição do novo líder é quase instantânea, mas, é possível acessar a página de logs em *Cluster > Admin logs* e ver, no meio do monte de erros de falha de conexão, que assim que a conexão com A foi perdida (*timeout*) o nó B iniciou um quórum de eleição de novo líder.

#### Reiniciando o nó A

Para subir o nó A novamente, basta executar o comando <b>docker start \<nome ou id do container></b> no terminal:

    docker start stupefied_varahamihira

Verá que o nó A voltou e já sincronizou com o restante do *Cluster* (cheque o *Admin logs*), mas o nó B continua como líder. Isso é padrão do RavenDB e provavelmente pode ser configurado, mas não faz parte do escopo desse projeto.<br>
<sub>Ref: https://ravendb.net/docs/article-page/4.2/python/server/clustering/rachis/cluster-topology</sub>

#### Cluster com apenas um nó funcionando

Continuando com testes básicos, agora iremos desconectar dois nós e ver o que acontece quando apenas um nó do *Cluster* está respondendo. Para isso, execute o comando <b>docker kill</b> em dois *containers* e mantenha apenas um rodando. Cheque que apenas um *container* está rodando com o comando <b>docker ps</b>.

Agora, temos um cenário como abaixo:

![B e C off](/assets/B_C_off.png)<br>Figura 6 - Topologia com apenas um nó conectado

O nó A aparentemente está 'travado' na votação, mas, na verdade, ele está continuadamente mandando requisições de votação para a eleição de um novo líder aos nós B e C, porém, como ambos estão desconectados e não respondem, o nó A não sabe o que fazer.<br>
Isso ocorre porque o quórum do RavenDB é baseado na maioria (n/2 + 1), ou seja, são necessários dois nós responderem, nesse caso, para que seja tomada uma ação. Veremos mais a frente como esse mesmo cenário se comporta para requisições de leitura/escrita.

### Populando o banco com amostras aleatórias

Inicie novamente todos os nós com o comando <b>docker start</b>.<br>
O primeiro passo é criar nosso banco de dados. Para isso, vá em *Databases > New Database*. Mantenha as configurações padrão e o fator de replicação em 3.

![Criando novo bd](/assets/new_db.png)<br>Figura 7 - Criando um novo banco de dados

Se tudo ocorreu bem, o resultado deve ser o seguinte:

![Novo bd](/assets/bd_pmd.png)<br>Figura 8 - Banco de dados criado e sincronizado com o *Cluster*

### Teste 1 - Beta

#### Populando o banco com o Python

O primeiro passo é instalar a biblioteca do RavenDB para o Python. O processo de instalação é razoavelmente fácil então não será coberto aqui.<br>
[Official RavenDB client/lib](https://github.com/ravendb/ravendb-python-client/tree/v4.0) - Instalação oficial

Para simplificar nossos testes, iremos popular o banco com apenas um tipo de documento, em uma única coleção. Porém, para testar as capacidades de busca, escrita e armazenamento, iremos utilizar um documento com um bom número de propriedades.

Para não perdermos tempo gerando dados aleatórios, gerei uma base de arquivos no site https://www.json-generator.com/ e iremos fazer a inserção no banco por *batch*. Os dados se encontram em /raw_json.

> A partir de agora não detalharemos tanto o passo a passo e os termos, pois o foco do teste são as métricas obtidas e não o entendimento total da reprodução do mesmo.<br>
> Se você clonou este repositório e seguiu o passo a passo até aqui, é bem provável que consiga reproduzir os testes a seguir sem muita dificuldade.

Para popular o banco com as amostras em `/raw_json` você deve executar, com o python3, o código que está em `/bin/store.py`. 

A primeira execução de testes é linear, então na linha `27 - batch_job (data, i)` ainda não estão sendo criadas threads para escritas concorrentes. Faremos isso mais para frente.

Como esse primeiro teste foi apenas uma experiência, deixei passar muita coisa, pois o RavenDB apaga os logs de tempo em tempo e não é possível fazer download das métricas ou acessar o fonte das mesmas (o que é bem bizarro). Aparentemente as métricas são mantidas apenas localmente (no *browser* de quem acessa) e não no servidor, o que dificulta muito a coleta das métricas.<br>
<sub>Ref: https://ravendb.net/docs/article-page/4.2/csharp/server/administration/statistics</sub>

#### Métricas teste 1

Após a execução completar, ~14500 documentos foram inseridos.

CLIENTE

    TEMPO POR REQUISIÇÃO (LATÊNCIA)
        MÉDIA:      0.03432780481207s
        MEDIANA:    0.034312248229981s
        MAX:        0.610070705413818s
        MIN:        0.009292364120483s
        DESVIO:     0.015870559451379s

    TEMPO TOTAL DAS REQUISIÇÕES:            497.753169775009s
    TEMPO DE EXECUÇÃO TOTAL DO ALGORITMO:   501.223156690598s

    REQUISIÇÕES ENVIADAS:       14500
    REQUISIÇÕES SUCEDIDAS:      14500



SERVIDOR - NÓ B (Líder)<br>
<sub>O RavenDB não salva e eu não printei nesse teste - mas lembro dos seguintes números</sub>

    REQUISIÇÕES RECEBIDAS:  14500
    REQUISIÇÕES ESCRITAS:   14500

    THROUGHPUT (WRITE):     20/s ~ 37/s 
    THROUGHPUT (READ):      0/s

![Tempo de resposta para cada requisição](/results/teste1_tempo_por_req.png)<br>Figura 1 - Gráfico com o tempo de resposta, medido no cliente, por cada requisição

### Falha nos nós e recuperação de informação

### Testes --

## Autores

- **Antonio Medeiros**: [ajmedeiros](https://github.com/ajmedeiros)
- **Daniel Davoli**: [davolli](https://github.com/davolli)