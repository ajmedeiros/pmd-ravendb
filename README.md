# Processamento Massivo de Dados - RavenDB

Repositório do projeto da disciplina, contendo os fontes e instruções.

## Sobre o projeto

Nesse repositório você encontrará todo o desenvolvimento do projeto da disciplina, sendo todas as instruções e códigos a seguir replicáveis na sua máquina local.
O banco escolhido para esse projeto foi o RavenDB: um banco open source, NoSQL, orientado a documentos.

* [github/ravendb](https://github.com/ravendb/ravendb)

## Instalando o RavenDB no Linux (Ubuntu 19.04)*

As instruções a seguir foram executadas no Ubuntu 19.04, mas devem funcionar, com algumas pequenas modificações necessárias, para qualquer distribuição Linux, em especial as baseadas em Debian (Ubuntu, Mint).

<sub>* A segunda parte desse passo a passo foi feita no Linux Mint 19.1.</sub>

### Download e instalação do RavenDB

#### Faça o download do RavenDB. A versão utilizada nesse projeto é 4.2.0*.

* [ravendb/download](https://ravendb.net/download)

<sub>* A versão utilizada no Docker é 4.2.1</sub>

#### Vá até o diretório onde o arquivo foi baixado e extraia seu conteúdo.

Por padrão, o diretório é $HOME/Downloads
    
    cd $HOME/Downloads

#### Extraia o conteúdo do arquivo baixado.

    tar -xf RavenDB-4.2.0-linux-x64.tar.bz2

Execute o comando ls para verificar que a extração ocorreu de fato:

    ls | grep RavenDB

Como nós baixamos os binários, já é possível utilizar o banco, basta entrar no diretório e executar o script de inicialização:

    cd RavenDB/
    ./run.sh

Feito isso, o RavenDB já estará rodando localmente na sua máquina.

#### [Opcional] Mude o diretório da instação.

    sudo mv $HOME/Downloads/RavenDB -t /usr/local/bin

#### Abra e execute novamente o RavenDB

    cd /usr/local/bin/RavenDB
    ./run.sh

### Configurando o RavenDB

Abra o console do RavenDB no seu browser:

    http://127.0.0.1:porta/wizard/index.html


Como este é um ambiente para aprendizado e testes, não precisamos nos preocupar com segurança, então, no passo 1, selecione Unsecure.

No passo 2, deixe como está, não é necessário mexer em nada por enquanto.

Reinicie o RavenDB e agora poderá acessar o banco de fato.

### Criando um Banco de Dados

O RavenDB possui uma ferramenta para popular um banco de testes automaticamente, pela própria interface. Basta ir em *Databases* e criar um novo banco com a opção de população automático.

### Realizando consultas

Dentro do próprio *studio* do RavenDB também é possível realizar as consultas nele. Como o propósito deste projeto não é analisar individualmente as consultas, não iremos abordar essa questão a fundo, mas recomendo executar algumas *queries* e se familiarizar com o RavenDB. Mais para frente iremos realizar consultas em massa utilizando alguma linguagem de programação.

## Executando o RavenDB no Docker

Para realizarmos testes de replicação e consistência, iremos primeiro rodar o RavenDB em alguns *containers* do Docker, para simular um *cluster*. Se você não faz ideia do que é o Docker, pode imaginar que estaremos simulando uma máquina, com sistema operacional e tudo, dentro do próprio computador, onde cada *container* roda isoladamente. Dessa forma, n *containers* representam n nós do RavenDB.

#### Instalando o Docker

Não cobriremos detalhadamente o funcionamento do Docker nem a sua configuração, mas se seguir os passos descritos aqui, conseguirá reproduzir fielmente o teste, que é o objetivo deste passo a passo.

É bem possível que o repositório do Docker já esteja presente na sua máquina, então, para instalá-lo, basta digitar os seguites comandos no terminal do Ubuntu:

    sudo apt-get update
    sudo apt-get install docker-ce docker-ce-cli containerd.io

Para verificar se o Docker foi corretamente instalado, digite no terminal:

    docker --version

Esse comando deve retornar algo parecido com o seguinte:

    Docker version 18.09.7, build 2d0083d

Se os comandos acima falharem, recomendo seguir as instruções oficiais:
* [Get Docker CE for Ubuntu](https://docs.docker.com/install/linux/docker-ce/ubuntu/)

### Inicializando os *containers*

O primeiro passo é inicializar os *containers* que serão utilizados para os testes. Nesse caso, utilizaremos 3 *containers* apenas, pois o limite da licença *free* é de 3 nós no *Cluster*. 

No terminal, execute os seguintes comandos:

    docker run -d --memory=512m --memory-swap=512m -p 8080:8080 -p 38880:38888 ravendb/ravendb
    docker run -d --memory=512m --memory-swap=512m -p 8081:8080 -p 38881:38888 ravendb/ravendb
    docker run -d --memory=512m --memory-swap=512m -p 8082:8080 -p 38882:38888 ravendb/ravendb


> O que esse comando está fazendo é dizendo ao docker para mapear as portas 808X do seu computador para a porta 8080 do *container*. O mesmo ocorre para as portas 3888X para a porta 38888. As portas 8080 e 38888 são padrões do RavenDB. As flags --memory e --memory-swap limitam o uso de memória do *container* para 512mb e não permitem que o *container* utilize a memória *swap*. A flag -d apenas diz para executar o docker em segundo plano e não é relevante nesse momento.
>> Limitamos a memória porque o objetivo desse teste é, principalmente, testar a replicação e consistência do RavenDB dado as características do *Cluster* e o teste de estresse. A proposta do RavenDB é ser performático em qualquer ambiente. Como o próprio criador enfatiza, o RavenDB pode rodar até mesmo num Raspberry PI. Então, para podermos aumentar o número de nós no *Cluster* sem precisar nos precuparmos com os recursos computacionais locais, podemos diminuir os recursos de cada *container*.

>> Porém, se memória não é um problema para você, então pode remover as flags ou aumentar o valor da memória disponível por *container*.

> A partir de agora, para abstrair um pouco do Docker, chamaremos cada *container* de nó, mas representam a mesma coisa nesse contexto. 

Para verificar que todos os nós foram criados e estão rodando, digite o seguinte comando no terminal:

    docker ps


O resultado desse comando deve ser algo parecido com o seguinte:

```
CONTAINER ID        IMAGE               COMMAND                  CREATED              STATUS                        PORTS                                                       NAMES
02cda896dec3        ravendb/ravendb     "/bin/sh -c /opt/Rav…"   About a minute ago   Up About a minute (healthy)   161/tcp, 0.0.0.0:8082->8080/tcp, 0.0.0.0:38882->38888/tcp   quirky_panini
e3699c1f3e12        ravendb/ravendb     "/bin/sh -c /opt/Rav…"   About a minute ago   Up About a minute (healthy)   161/tcp, 0.0.0.0:8081->8080/tcp, 0.0.0.0:38881->38888/tcp   festive_nash
c55ba0222c14        ravendb/ravendb     "/bin/sh -c /opt/Rav…"   14 minutes ago       Up 14 minutes (healthy)       161/tcp, 0.0.0.0:8080->8080/tcp, 0.0.0.0:38880->38888/tcp   stupefied_varahamihira

```

### Acessando um nó no *browser*

Primeiro precisamos saber o IP de cada nó. O Docker nos dá isso, basta executar o seguinte comando:

    docker network inspect bridge

O resultado esperado são IPs na faixa de 172.17.0.2 .. 172.17.0.4

Para acessar a interface de cada nó através do seu *browser*, basta digitar o seguinte endereço nele:

    http://172.17.0.X:8080

Porém, não mexa em nada ainda, pois precisamos configurar o nosso *cluster*.

### Configurando o primeiro nó do Cluster

Para o primeiro nó do *Cluster*, que será o líder, faremos uma inicialização bem simples, muito parecido com o que fizemos anteriormente. 

1. No *browser*, digite o IP do servidor que será o líder.

2. Na primeira tela, selecione *Unsecure*.

3. Na seguda tela, preencha apenas o IP do *Server* com o IP do *container* e ative a opção "Create new cluster":

    ![Primeiro nó - Segunda Tela](/assets/no1_tela2.png)<br>Figura 1 - Configurando o primeiro nó

4. Clique em *Next* e reinicie o servidor.

Pronto! Temos um *Cluster* local do RavenDB com apenas um servidor (nó) nele.


### Adicionando um novo nó ao Cluster

> Antes de mais nada, é necessário uma licença do RavenDB para poder criar um *cluster*. Obtenha uma licença grátis de desenvolvedor, dentro do *studio* do RavenDB mesmo, indo em *notifications > get a license*. Preencha corretamente seus dados e selecione a licença de *developer*. Em alguns minutos a mesma será enviada para o e-mail cadastrado, copie a licença, vá em *notifications > register* e cole. 

![Licença](/assets/license.png)<br>Figura 2 - Adquirindo uma licença *free*

Tendo registrado a licença, podemos agora adicionar os nós criados ao nosso *Cluster*.

1. Abra, no *browser*, o servidor que deseja adicionar ao *Cluster*.

2. Na primeira tela, selecione *Unsecure*.

3. Na segunda tela, preencha apenas o IP do servidor com o IP do *container* e <b>NÃO</b> ative a opção "Create a new cluster"!

4. Clique em *Next* e reinicie o servidor.

5. Volte para o primeiro servidor, que é o líder do *Cluster*.

6. Vá para *Manage Server > Cluster*.

7. Clique em "Add Node to cluster", e em "Server url" preencha o IP do *container* do nó que quer adicionar, juntamente com a porta, e em "Tag" dê uma letra de identificação ao nó. 

8. Clique em "Test Connection" para assegurar que a conexão está correta e adicione o nó ao *Cluster*.

    ![Add node](/assets/add_node.png)<br>Figura 3 - Adicionando um novo nó ao *Cluster*

9. Repita os mesmos passos para os outros nós que desejar adicionar ao *Cluster*.

10. Novamente, para economizar recursos computacionais locais e padronizar, clique em *Operations > Reassign Cores* e coloque "Cores to use = 2".

11. Ao final, o *Cluster* deve ficar parecido com o seguinte:

    ![Final topology](/assets/final_topology.png)<br>Figura 4 - Topologia do *Cluster*

E então temos um *cluster* com três nós pronto para os testes.

## Autores

- **Antonio Medeiros**: [ajmedeiros](https://github.com/ajmedeiros)
- **Daniel Davoli**: [davolli](https://github.com/davolli)