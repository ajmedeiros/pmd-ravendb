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

![Topologia com A off](/assets/A_off.png)<br>Figura 1 - Topologia com novo líder e nó A desconectado

Como estamos rodando o *Cluster* locamelmente, a eleição do novo líder é quase instantânea, mas, é possível acessar a página de logs em *Cluster > Admin logs* e ver, no meio do monte de erros de falha de conexão, que assim que a conexão com A foi perdida (*timeout*) o nó B iniciou um quórum de eleição de novo líder.

#### Reiniciando o nó A

Para subir o nó A novamente, basta executar o comando <b>docker start \<nome ou id do container></b> no terminal:

    docker start stupefied_varahamihira

Verá que o nó A voltou e já sincronizou com o restante do *Cluster* (cheque o *Admin logs*), mas o nó B continua como líder. Isso é padrão do RavenDB e provavelmente pode ser configurado, mas não faz parte do escopo desse projeto.<br>
<sub>Ref: https://ravendb.net/docs/article-page/4.2/python/server/clustering/rachis/cluster-topology</sub>

#### Cluster com apenas um nó funcionando

Continuando com testes básicos, agora iremos desconectar dois nós e ver o que acontece quando apenas um nó do *Cluster* está respondendo. Para isso, execute o comando <b>docker kill</b> em dois *containers* e mantenha apenas um rodando. Cheque que apenas um *container* está rodando com o comando <b>docker ps</b>.

Agora, temos um cenário como abaixo:

![B e C off](/assets/B_C_off.png)<br>Figura 2 - Topologia com apenas um nó conectado

O nó A aparentemente está 'travado' na votação, mas, na verdade, ele está continuadamente mandando requisições de votação para a eleição de um novo líder aos nós B e C, porém, como ambos estão desconectados e não respondem, o nó A não sabe o que fazer.<br>
Isso ocorre porque o quórum do RavenDB é baseado na maioria (n/2 + 1), ou seja, são necessários dois nós responderem, nesse caso, para que seja tomada uma ação. Veremos mais a frente como esse mesmo cenário se comporta para requisições de leitura/escrita.

### Populando o banco com amostras aleatórias

Inicie novamente todos os nós com o comando <b>docker start</b>.<br>
O primeiro passo é criar nosso banco de dados. Para isso, vá em *Databases > New Database*. Mantenha as configurações padrão e o fator de replicação em 3.

![Criando novo bd](/assets/new_db.png)<br>Figura 3 - Criando um novo banco de dados

Se tudo ocorreu bem, o resultado deve ser o seguinte:

![Novo bd](/assets/bd_pmd.png)<br>Figura 4 - Banco de dados criado e sincronizado com o *Cluster*

### Teste 0 - Beta

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

#### Métricas teste 0 - populando o banco

Após a execução completar, ~14500 documentos foram inseridos.

##### CLIENTE

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


![Tempo de resposta para cada requisição](/results/teste1_tempo_por_req.png)<br>Figura 5 - Gráfico com o tempo de resposta, medido no cliente, por cada requisição


##### SERVIDOR - NÓ B (Líder)<br>
<sub>O RavenDB não salva e eu não printei nesse teste - mas lembro dos seguintes números</sub>

    REQUISIÇÕES RECEBIDAS:  14500
    REQUISIÇÕES ESCRITAS:   14500

    THROUGHPUT (WRITE):     20/s ~ 37/s 
    THROUGHPUT (READ):      0/s

##### CLUSTER (BD)

                    NÓ A            NÓ B            NÓ C
    DISK USED       912.31MB        912.56MB        912.43MB
    DOCUMENTS       14532           14532           14532

### Falha nos nós e recuperação de informação

Vamos testar agora o que acontece no caso de um nó falhar completamente e precisar ser substituído por outro nó.<br>
Para isso, iremos matar um *container* e removê-lo do disco e, em seguida, subir um novo *container* com as mesmas especificações e checar a sincronização.

<sub>Obs: Primeiro, vou remover alguns documentos do banco, pois inserindo 14.500 documentos ocupou mais espaço no disco do que eu esperava e estou tendo alguns problemas! :p </sub>

Faremos um script em Python para isso também e pegaremos algumas métricas!

#### Métricas teste 0 - deletando 4.500 documentos

A princípio, tentei deletar os documentos criando uma *thread* para cada requisição. Mas deu problema de exceção do Python e não consegui resolver, então executei o código sequencialmente mesmo.

Após executar o código `/bin/delete.py`:

##### CLIENTE

    TEMPO POR REQUISIÇÃO (LATÊNCIA)
        MÉDIA:      0.029972391446432s
        MEDIANA:    0.029481291770935s
        MAX:        0.127013206481934s
        MIN:        0.011135578155518s
        DESVIO:     0.009958278400284s

    TEMPO TOTAL DAS REQUISIÇÕES:            134.875761508942s
    TEMPO DE EXECUÇÃO TOTAL DO ALGORITMO:   N/A

    REQUISIÇÕES ENVIADAS:       4500
    REQUISIÇÕES SUCEDIDAS:      4500

![Tempo de resposta para cada requisição - delete](/results/teste1_tempo_por_req_del.png)<br>Figura 6 - Gráfico com o tempo de resposta, medido no cliente, por cada requisição - *delete*

##### CLUSTER (BD)

                    NÓ A            NÓ B            NÓ C
    DISK USED       656.56MB        656.31MB        656.47MB
    DB SIZE         328.12MB        328.06MB        328.06MB
    DOCUMENTS       10140           10140           10140

Não consegui captar erros nos logs do RavenDB, mas está estranho o número de documentos restantes no banco. Supondo que todas operações de deletar um documento fossem bem sucedidas, esperava-se 10032 documentos no banco. Como o RavenDB utiliza um algoritmo diferente para realizar a operação de deletar documentos, talvez alguns documentos dentro do banco possuam metadados sobre os que foram deletados, e por isso foram gerados mais documentos, porque o RavenDB marca com *tombstones* os documentos deletados. Mas é apenas uma suposição, porque não consegui encontrar referências que comprovassem o que houve, ou se ocorreu algum erro de fato.

Para a minha decepção, a quantidade de disco usada pelos *containers* do RavenDB não diminuiu. Enquanto as operações de *delete* estavam acontecendo, o tamanho total do banco diminuiu, mas, ao fim das operações, voltou ao tamanho que estava ~900mb.<br>
Cada nó possui 512mb de arquivos temporários que não consegui descobrir o que é, já que a documentação do RavenDB é bem fraca. Imagino que sejam *backups* automáticos para a recuperação dos dados. Talvez expirem depois de algum tempo ou reiniciando todo o *Cluster*.<br>
<sub>Ref: https://ravendb.net/docs/article-page/4.1/csharp/server/storage/directory-structure</sub> 

#### Dashboard dos servidores (nós)

![Dashboard B](/results/del_dash_B_3.png)<br>Figura 7 - *Dashboard* do nó B

Nada de muito especial na *dashboard* do nó B. Como as requisições de *delete* foram sequenciais também, esse era o comportamento esperado.


Nas *dashboards* dos nós A e C, não houveram requisições, pois acredito que o algoritmo do RavenDB priorize o nó líder, dado que todos os nós empatariam no *speed test* (balanceador selecionado para esse projeto - *fastest node*), pois possuem a mesma configuração. E como a comunicação entre os servidores é feita internamente, não é mostrado nos gráficos da *dashboard* como a troca de informações entre os nós é feita. Mas é possível ver as requisições por *batch* de dados nos *logs* do RavenDB.

Porém, como é possível ver na figura a seguir, em um momento o nó A recebe algumas requisições. Acredito que, por um curto período de tempo, o nó B ficou sobrecarregado e o balanceador de carga jogou uma requisição para o nó A.

![Dashboard A](/results/del_dash_A.png)<br>Figura 8 - *Dashboard* do nó A

## Testes de estresse

Com tudo pronto, agora rodaremos o que nos interessa, que é o teste de estresse do banco, nos permitindo colher as métricas do banco no seu uso extremo bem como verificar sua capacidade.

Acredito que o código esteja legível, então não vou explicá-lo. Configure apenas as flags globais que estão em maiúsculo `URLS`, `DATABASE` etc.

Aqui colocarei apenas as métricas - prints para os nós e estatísticas locais para o cliente.

### Consultas utilizadas

#### Consulta de leitura (*query*)

```python
query_random = "FROM Agregadoes WHERE Agregado.name >= \"" + str (random.choice(string.ascii_uppercase)) + "\" SELECT Agregado "

query_result = list(session.query(object_type=Agregado).raw_query(query_random))
```

#### Consulta de escrita (*update*)

```python
with store.open_session() as session: 
load_random = "agregadoes/" + str (1 + int (random.random() * 10000)) + "-B"
load_result = session.load(load_random, object_type = Agregado)

if isinstance(load_result, Agregado):
    load_result.Agregado["about"] = randomString (int (random.random() * 200)) + "\r\n"
    session.save_changes()
```

### Teste 1

> Um pouco decepcionante, pois o nó líder não aguentou a carga e foram realizadas, em média, menos de duas operações por thread.<br>
Para o próximo teste (teste - 2), atualizei a RAM do nó líder para 1024mb.

#### Cliente

    Threads de leitura:     80
    Threads de escrita:     20 

    BATCH (total req por thread) LEITURA:
        MÉDIA:      1.3625
        MEDIANA:    
        MAX:        
        MIN:        
        DESVIO:     
        
    TEMPO POR REQUISIÇÃO LEITURA (LATÊNCIA)
        MÉDIA:      124.799708589501s
        MEDIANA:    124.024944067001s
        MAX:        211.265622138977s
        MIN:        6.53380560874939s
        DESVIO:     52.7056179415961s

    REQUISIÇÕES ENVIADAS:       109
    REQUISIÇÕES SUCEDIDAS:      109

![Stress 1 - Read](/results/stress1_read.png)<br>Figura 9 - Latência por *query* do teste 1

Pela figura fica claro que quanto mais sobrecarregado o *Cluster*, dado o número de conexões simultâneas, maior o tempo de resposta para cada *query*. Para ficar mais claro, a query 1 inicia antes da query 109.


    BATCH (total req por thread) ESCRITA:
        MÉDIA:      16.7
        MEDIANA:    2
        MAX:        296
        MIN:        2
        DESVIO:     65.74039854

    TEMPO POR REQUISIÇÃO ESCRITA (LATÊNCIA)
        MÉDIA:      5.50575593916956s
        MEDIANA:    0.028679251670837s
        MAX:        77.2490684986115s
        MIN:        0.012414693832398s
        DESVIO:     18.1728424793919s

    REQUISIÇÕES ENVIADAS:       344
    REQUISIÇÕES SUCEDIDAS:      334

![Stress 1 - Write](/results/stress1_write.png)<br>Figura 10 - Latência por *update* do teste 1

Para esse caso, imagino que as requisições de update só iniciaram depois das de leitura, quando as de leitura já estavam no final, por gargalo tanto da máquina quanto do nó líder. Depois de um tempo, conforme as leituras foram terminando, o tempo de resposta ficou muito baixo e só foi aumentar no final, quando imagino que também tenha acumulado algumas requisições de update.

--------------------

### Teste 2

Agora, com o nó líder utilizando 1024mb de memória. Os outros nós continuam com a mesma configuração.<br>
Também aumentei o tempo de estresse de 90s para 180s e coletei algumas métricas a mais.

Teste falhou. A memória do nó C (membro) encheu e o mesmo ficava requisitando votação (creio que para realizar o *speed test* e fazer o balanceamento de carga). Porém como o mesmo não tinha memória para fazer o processamento, ficou "travado" nisso. Como iria demorar demais, abortei.

Troquei o balaceamento de carga de *speed test* para *none*. Vou executar o mesmo teste.

Mesmo problema, devido ao alto número de requisições e conexões simultâneas, o nó B falhou. E por algum motivo os nós A e C não estão recebendo as requisições que vão para B. Investiguei os logs para tentar descobrir o erro, mas não encontrei nada, apenas o erro que o nó B não estava respondendo (*timeout*).

Outro teste, todos os nós com 1024mb de memória e sem configurar balanceador. Porém acredito que agora possa dar problema de sobrecarga no meu computador local.

O mesmo problema persiste. Dessa vez o nó A estourou a memória (1024mb) e parou de responder. Porém, as requisições não estão sendo redistribuídas aos nós B ou C.

------------

### Teste 3

Apenas com o intuito de colher dados, reiniciei todos os *containers* e realizei um último teste com menos threads e liberei mais memória para os *containers*.

    Nó A (líder)
        Número de vCPUs: 4
        Memória: 2000mb

    Nó B
        Número de vCPUs: 2
        Memória: 1500mb

    Nó C
        Número de CPUs: 2
        Memória: 1500mb            

    ---------------------------------------------

    LOGS DO CLIENTE (Python)

    Tempo de execução:      318s
    Threads de leitura:     16
    Threads de escrita:     4    
        
    TEMPO POR REQUISIÇÃO LEITURA (LATÊNCIA)
        MÉDIA:      12.5423633009576s
        MEDIANA:    11.3065989017487s
        MAX:        31.3795788288116s
        MIN:        0.560620069503784s
        DESVIO:     8.16045930903834s

    REQUISIÇÕES ENVIADAS:       391
    REQUISIÇÕES SUCEDIDAS:      391
    FALHAS:                     0

![Stress 1 - Read](/results/stress3_read.png)<br>Figura 11 - Latência por *query* do teste 3

    TEMPO POR REQUISIÇÃO ESCRITA (LATÊNCIA)
        MÉDIA:      1.54696673405798s
        MEDIANA:    1.4964097738266s
        MAX:        3.87301421165466s
        MIN:        0.05821967124939s
        DESVIO:     0.636615012660566s

    REQUISIÇÕES ENVIADAS:       788
    REQUISIÇÕES SUCEDIDAS:      760
    FALHAS:                     28

![Stress 1 - Write](/results/stress3_write.png)<br>Figura 12 - Latência por *update* do teste 3

-----------------------

    LOGS DO CLUSTER (RavenDB/databases/pmd/metrics)

    NÓ A

    "PutsPerSec":{  
         "Current":2.0,
         "Count":907,
         "MeanRate":0.7,
         "OneMinuteRate":2.5,
         "FiveMinuteRate":2.5,
         "FifteenMinuteRate":1.0
    }

![Stress 3 - Nó A1](/results/teste3-dashA1.png)<br>Figura 13 - Dashboard do nó A
![Stress 3 - Nó A2](/results/teste3-dashA2.png)<br>Figura 14 - Dashboard do nó A
![Stress 3 - Nó A2](/results/teste3-dashA3.png)<br>Figura 15 - Dashboard do nó A

-----------------------

    NÓ B

    "Requests":{  
      "RequestsPerSec":{  
         "Current":6.0,
         "Count":2682,
         "MeanRate":2.2,
         "OneMinuteRate":6.7,
         "FiveMinuteRate":6.4,
         "FifteenMinuteRate":3.0
      },
      "ConcurrentRequestsCount":0,
      "AverageDuration":1038.2963722584097
    }

    "PutsPerSec":{  
         "Current":2.0,
         "Count":905,
         "MeanRate":0.8,
         "OneMinuteRate":2.5,
         "FiveMinuteRate":2.5,
         "FifteenMinuteRate":1.0
      }

![Stress 3 - Nó B1](/results/teste3-dashB1.png)<br>Figura 16 - Dashboard do nó B
![Stress 3 - Nó B2](/results/teste3-dashB2.png)<br>Figura 17 - Dashboard do nó B
![Stress 3 - Nó B3](/results/teste3-dashB3.png)<br>Figura 18 - Dashboard do nó B

------------------

    NÓ C

      "PutsPerSec":{  
         "Current":2.0,
         "Count":901,
         "MeanRate":0.8,
         "OneMinuteRate":2.5,
         "FiveMinuteRate":2.5,
         "FifteenMinuteRate":1.0
      }

![Stress 3 - Nó C1](/results/teste3-dashC1.png)<br>Figura 19 - Dashboard do nó C
![Stress 3 - Nó C2](/results/teste3-dashC2.png)<br>Figura 20 - Dashboard do nó C
![Stress 3 - Nó C3](/results/teste3-dashC3.png)<br>Figura 21 - Dashboard do nó C


-----------

### Teste 4

Mesmas configurações do teste 3, porém com 800 threads de leitura e 200 de escrita: falha.<br>
Sobrecarrega a memória dos nós e os mesmos param de responder.

        self, "Failed to establish a new connection: %s" % e)
        urllib3.exceptions.NewConnectionError: <urllib3.connection.HTTPConnection object at 0x7fa47c6d97f0>:
        Failed to establish a new connection: [Errno 24] Too many open files

![Stress 4 - Dash A](/results/dashA-quebrado.png)<br>Figura 22 - Dashboard do nó A
![Stress 4 - Dash B](/results/dashB-quebrado.png)<br>Figura 23 - Dashboard do nó B
![Stress 4 - Dash C](/results/dashC-quebrado.png)<br>Figura 24 - Dashboard do nó C

## Autores

- **Antonio Medeiros**: [ajmedeiros](https://github.com/ajmedeiros)
- **Daniel Davoli**: [davolli](https://github.com/davolli)