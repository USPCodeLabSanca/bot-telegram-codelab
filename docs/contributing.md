# Como contribuir?

Este documento visa criar convenções que mantenham o projeto padronizado e tornem a contribuição intuitiva, permitindo a sua expansão ao longo do tempo.

Espera-se que o projeto seja periodicamente assumido por grupos pequenos. Dessa forma, a facilidade de comunicação torna desnecessária a criação de regras rígidas; apenas boas práticas que orientem o desenvolvimento, sendo inspiradas na forma como se iniciou o projeto.

## Fluxo de contribuição

Há duas branches principais que existem fixas no projeto:

- **Develop:** Aglomera novas features, correções de bugs e todos os commits e PRs de um ciclo de desenvolvimento
- **Main:** Recebe as versões estáveis e testadas de cada ciclo, sendo dela que se colocará o código em produção

Assim, o grupo que estiver desenvolvendo novas funcionalidades para o bot ficará livre para definir quando cada entrega será feita na `main` conforme o projeto avança, e o desenvolvimento bruto isolará bugs e testes na `develop`.

Durante o desenvolvimento, cada nova feature, bug ou tarefa de documentação deve ser formalizada em uma issue, havendo a possibilidade de descrevê-las com os templates definidos no repositório. Assim, cada membro do grupo pode pegar uma issue e desenvolvê-la na sua própria branch; quando terminar, este deve realizar um `merge` na branch `develop`.

Vale citar que a utilização intensa das issues é recomendada pela possibilidade de criá-las pelo próprio bot, o que não só agiliza o processo como também permite unificar as necessidades do grupo de desenvolvimento com o que o resto do grupo (CodeLab) sugerir.

### Nomenclatura de issues e branches

Recomenda-se seguir a estratégia do desenvolvimento inicial, usando três nomes padrão para o começo de cada issue:

- **Feature:** Pede uma nova funcionalidade ou adição de código ao projeto
- **Task:** Nova documentação, ou adição da gerência do projeto (como o gerenciamento de dependências, deploy, etc...)
- **fix:** Incida bugs a serem corrigidos
- **change:** Indica grandes trechos de códigos ou reestruturações arquiteturais necessárias no projeto

Como como issue deve ser resolvida na sua própria branch, sugere-se que adote essa mesma nomenclatura para nomear as branches:
  
  `tipoDeIssue/nomeQueDescreveAIssue`
  
Por exemplo, a issue da qual essa documentação surgiu chamava-se **Task: Documento de contribuição** e, consequentemente, sua branch foi chamada de `task/documentoDeContribuição`

## Padrões de código

O código é fortemente baseado na biblioteca `telebot`, utilizando uma arquitetura de injeção de dependências, que pode ser entendida em : ADICIONAR LINK PARA O DOCUMENTO DE ARQUITETURA

### Nomenclatura do código

- O código, seus arquivos e módulos devem estar todos em inglês
- Comentários devem estar em português
- Funções e variáveis devem ser escritas em `snake_case`
- Classes devem ser escritas em `CamelCase`
- Constantes devem ser escritas com todas as letras em maiúsculo.
- Recomenda-se que cada arquivo de handler tenha o mesmo nome da classe que implementa que, por sua vez, é o mesmo nome do comando a ser chamado pelo usuário.
