# Processamento Massivo de Dados - RavenDB

Repositório do projeto da disciplina, contendo os fontes e instruções.

## Sobre o projeto

Nesse repositório você encontrará todo o desenvolvimento do projeto da disciplina, sendo todas as instruções e códigos a seguir replicáveis na sua máquina local.
O banco escolhido para esse projeto foi o RavenDB: um banco open source, NOSQL, orientado a documentos.

* [github/ravendb](https://github.com/ravendb/ravendb)

## Instalando no Linux (Ubuntu 19.04)

As instruções a seguir foram executadas no Ubuntu 19.04, mas devem funcionar para qualquer distribuição Linux, em especial as baseadas em Debian (Ubuntu, Mint).

### Download e instalação do RavenDB

#### Faça o download do RavenDB. A versão utilizada nesse projeto é 4.2.0.

* [ravendb/download](https://ravendb.net/download)

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

### Realizando consultas

## Executando o RavenDB no Docker

### Adicionando um novo nó ao Cluster

## Running the tests -- TEMPLATE

Explain how to run the automated tests for this system

### Break down into end to end tests

Explain what these tests test and why

```
Give an example
```

### And coding style tests

Explain what these tests test and why

```
Give an example
```

## Deployment

Add additional notes about how to deploy this on a live system

## Built With

* [Dropwizard](http://www.dropwizard.io/1.0.2/docs/) - The web framework used
* [Maven](https://maven.apache.org/) - Dependency Management
* [ROME](https://rometools.github.io/rome/) - Used to generate RSS Feeds

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags). 

## Authors

* **Billie Thompson** - *Initial work* - [PurpleBooth](https://github.com/PurpleBooth)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Hat tip to anyone whose code was used
* Inspiration
* etc

