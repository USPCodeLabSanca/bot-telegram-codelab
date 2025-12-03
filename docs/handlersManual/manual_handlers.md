# Manual de Handlers

## Introdução
Este documento serve como a referência central para todos os message_handlers do Bot. O objetivo é mapear, de forma padronizada, como o Bot reage a interações do usuário, detalhando a lógica de entrada (comandos), processamento (fluxos e estados) e saída (respostas).

A documentação está organizada por Módulos (arquivo.py), refletindo a estrutura do código-fonte (`./src`). Cada seção detalha uma classe de handler, expondo suas dependências técnicas e caminho de comunicação ideal de um usuário

## Legenda: Atributos
Para garantir uma leitura rápida das capacidades de cada comando, os seguintes ícones e definições foram utilizados no cabeçalho de cada classe:

- ⚙️ **Comando:** O gatilho textual que inicia o handler (ex: /start, /help).

- 📋 **Menu de Comandos:** Indica (Sim/Não) se o comando está visível no botão "Menu" da interface do Telegram.

- 📝 **/help:** Indica (Sim/Não) se o comando está presente no comando de ajuda interno.

- 🔎 **Escopo:** Define onde o comando pode ser executado:
    - *All:* Funciona em qualquer chat (Privado e Grupos).
    - *Privado:* Funciona restritamente em conversas diretas com o bot (DM).
    - *Grupo:* Funciona restritamente em grupos/supergrupos/canais.
- 🗝️ **Permissão:** Define o nível de acesso necessário:
    - *Qualquer Usuário:* Aberto ao público geral.
    - *Admin:* Restrito a administradores do grupo.

## Princípios gerais de um handler
- ### abstract.py e msg_handler
    Todos os message_handler's descritos neste documento são filhas da classe abstrata `msg_handler`, que está disposta no módulo `abstract.py`. Atualmente, as únicas 2 funcionalidades desta classe são:

     - Inicializar o atributo `BOT` (Instância do AsyncTeleBot) para cada uma das classes filhas no método `__init__`.
     - Impor que o método `__call__` deve ser utilizado nas classes filhas.
    
    Caso este projeto do telegram-bot-codelab seja revisitado no futuro, com novas funcionalidades mais complexas, será possível adicionar mais características ou funções a esta classe-pai, de maneira que todos os handlers herdem essas novidades, o que torna as classes-filhas menos redundantes.


- ### def \_\_call\_\_(self, msg: Message)
    O método `__call__` é utilizado em todos os handlers, pois ele é a primeira função a ser executada quando o comando do handler acionado. Funcionalidades mais complexas do Bot precisam estabelecer formas de acionar outras funções a partir do `__call__` .

- ### @catch_message_errors() e @catch_callbackquery_errors()
    Os decoradores `@catch_message_errors()` e `@catch_callbackquery_errors()` devem ser usados em métodos que enviam mensagens e que lidam com callbackqueries, respectivamente. Quando ocorre uma `Exception` dentro destes métodos, uma mensagem é enviada para o usuário, alertando que algo de errado ocorreu e o fluxo de comunicação é interrompido. Esses decoradores padronizam a forma como os erros são lidados e removem a necessidade de usar `try-catch` em todas as funções.

## Sumário
* [Introdução e Legenda](#Introdução)
* [Princípios Gerais de um Handler](#principios-gerais)
* [Módulo: codelab.py](#módulo-codelabpy)
    * [CodelabHandler](#codelabhandler)
* [Módulo: feedbacks.py](#módulo-feedbackspy)
    * [FeedbackMain](#feedbacknmain)
    * [FeedbackAdd](#feedbackadd)
    * [FeedbackHelper](#feedbackguide)
* [Módulo: fronts.py](#módulo-frontspy)
    * [ShowFronts](#showfronts)
* [Módulo: git_invite.py](#módulo-gitinvitepy)
    * [GitInvite](#gitinvite)
* [Módulo: help.py](#módulo-helppy)
    * [Help](#help)
* [Módulo: links.py](#módulo-linkspy)
    * [ShowLinks](#showlinks)
* [Módulo: start.py](#módulo-startpy)
    * [Start](#start)
* [Módulo: suggestions.py](#módulo-suggestionspy)
    * [SuggestionMain](#suggestionmain)
    * [SuggestionAdd](#suggestionadd)
    * [SuggestionList](#suggestionlist)
    * [SuggestionGuide](#suggestionguide)
    * [BuggedCommand](#buggedcommand)

## Módulo: codelab.py 🧪

- ### CodelabHandler
    - #### Atributos
        - ⚙️ **Comando:** `/codelab`.
        - 📋 **Menu de Comandos:** Sim.
        - 📝 **/help:** Sim.
        - 🔎 **Escopo:** All.
        - 🗝️ **Permissão:** Qualquer Usuário.

    - #### Função
        - O handler CodelabHandler envia variações do nome Codelab, visto que poucas pessoas sabem como realmente é o nome do grupo.

    - #### Fluxo de comunicação
        1. **Solicitação:** O usuário envia `/codelab`. O Bot envia a mensagem "O meu grupo se chama _*nome_errado*!"

    - #### Inicialização e dependências
        ``` 
            codelab_comm = codelab.CodelabHandler(bot, CODELAB_NAME_LIST)
        ```

        | Parâmetro                | Descrição               |
        | :------------------------|:-----------------------|
        | `bot`                    | Instância do AsyncTeleBot |
        | `CODELAB_NAME_LIST`      | Caminho (str) para o arquivo JSON com variações erradas do nome "codelab"|

    [⬆️ Voltar ao Topo](#Manual-de-Handlers)

## Módulo: feedbacks.py 🗣️

- ### FeedbackMain
    - #### Atributos
        - ⚙️ **Comando:** `/feedback`.
        - 📋 **Menu de Comandos:** Sim.
        - 📝 **/help:** Sim.
        - 🔎 **Escopo:** All (preferencialmente, Privado).
        - 🗝️ **Permissão:** Qualquer Usuário.

    - #### Função
        - O handler FeedbackMain é o início do sistema de feedbacks. Ele direciona o usuário para as ações de enviar um feedback ou então ver os regulamentos do envio.

    - #### Fluxo de comunicação
        1. **Solicitação:** O usuário envia `/feedback`. O Bot envia um menu contendo:
            - Opção de dar um feedback.
            - Opção de cancelar.
            - Regras de uso.


    - #### Inicialização e dependências
        ``` 
            feedback_main = feedbacks.FeedbackMain(bot, feedback_add, feedbacks_guide)
        ```

        | Parâmetro                | Descrição               |
        | :------------------------|:-----------------------|
        | `bot`                    | Instância do AsyncTeleBot |
        | `feedback_add`           | Instancia do handler [FeedbackAdd](#2-feedbackadd)|
        | `feedback_guide`         | Instancia do handler [FeedbackHelper](#3-feedbackhelper)|

    [⬆️ Voltar ao Topo](#Manual-de-Handlers)

- ### FeedbackAdd
    - #### Atributos
        - ⚙️ **Comando:** `/feedback_add`.
        - 📋 **Menu de Comandos:** Não.
        - 📝 **/help:** Não.
        - 🔎 **Escopo:** All (preferencialmente, Privado).
        - 🗝️ **Permissão:** Qualquer Usuário.

    - #### Função
        - O handler FeedbackAdd coleta a categoria do feedback a ser enviado, recebe o texto do usuário, formata e então o envia para um grupo do telegram contendo os coordenadores do Codelab.

    - #### Fluxo de comunicação
        1.  **Solicitação:** O usuário aciona o handler por meio do [FeedbackMain](#1-feedbackmain) ou então envia o comando `/feedback_add`. O Bot apresenta os botões de categoria `SUGESTÃO`, `RECLAMAÇÃO`, `ELOGIO`.

        2. **Seleção**: Usuário clica na categoria desejada.

        3. **Submissão de feedback**: Usuário envia o texto do feedback.

        4. **Confirmação:** O Bot exibe uma prévia formatada. Se o usuário confirmar, o Bot envia para o grupo dos coordenadores e notifica o usuário do sucesso.

    - #### Inicialização e dependências
        ```
            feedbacks_add = feedbacks.FeedbackAdd(bot, TARGET_CHAT_ID)
        ``` 
        
        | Parâmetro                | Descrição               |
        | :------------------------|:-----------------------|
        | `bot`                    | Instância do AsyncTeleBot |
        | `TARGET_CHAT_ID`         | ID (int) do chat dos coordenadores |

    [⬆️ Voltar ao Topo](#Manual-de-Handlers)

- ### FeedbackHelper
    - #### Atributos
        - ⚙️ **Comando:** `/feedback_guide`.
        - 📋 **Menu de Comandos:** Não.
        - 📝 **/help:** Não.
        - 🔎 **Escopo:** All (preferencialmente, Privado).
        - 🗝️ **Permissão:** Qualquer Usuário.

    - #### Função
        - O handler FeedbackHelper fornece instruções e regras para o usuário, explicando as melhores práticas para construir um feedback claro, respeitoso e produtivo.

    - #### Fluxo de comunicação
        1.  **Solicitação:** O usuário aciona o handler por meio do [FeedbackMain](#1-feedbackmain) ou então envia o comando `/feedback_guide`. O Bot envia um texto com os regulamentos e as dicas.

    - #### Inicialização e dependências
        ```
            feedbacks_guide = feedbacks.FeedbackHelper(bot)
        ```

        | Parâmetro                | Descrição               |
        | :------------------------|:-----------------------|
        | `bot`                    | Instância do AsyncTeleBot |

    [⬆️ Voltar ao Topo](#Manual-de-Handlers)

## Módulo: fronts.py 💻

- ### ShowFronts
    - #### Atributos
        - ⚙️ **Comando:** `/fronts`.
        - 📋 **Menu de Comandos:** Sim.
        - 📝 **/help:** Sim.
        - 🔎 **Escopo:** All.
        - 🗝️ **Permissão:** Qualquer Usuário.

    - #### Função
        - O handler ShowFronts envia um menu contendo resumos da atuação de cada frente do Codelab.

    - #### Fluxo de comunicação
        1. **Solicitação:** O usuário envia `/fronts`. O Bot apresenta um menu contendo os botões das frentes `DEV.LEARN`, `DEV.BOOST`, `DEV.HIRE`, `DEV.CLARA`, `DEV.HIRE`.

        2. **Seleção**: Quando o usuário escolhe uma das frentes, o Bot envia um resumo curto daquela opção

    - #### Inicialização e dependências
        ``` 
            front = fronts.ShowFronts(bot)
        ```

        | Parâmetro                | Descrição               |
        | :------------------------|:-----------------------|
        | `bot`                    | Instância do AsyncTeleBot |

    [⬆️ Voltar ao Topo](#Manual-de-Handlers)

## Módulo: git_invite.py 💌

- ### GitInvite
    - #### Atributos
        - ⚙️ **Comando:** `/git_Invite/*`.
        - 📋 **Menu de Comandos:** Sim.
        - 📝 **/help:** Sim.
        - 🔎 **Escopo:** All.
        - 🗝️ **Permissão:** Qualquer Usuário.

    - #### Função
        - O handler GitInvite recebe o email do usuário e, usando a API do GitHub, envia um convite para que ele entre para a organização do Codelab dentro do GitHub.

    - #### Fluxo de comunicação
        1. **Solicitação:** O usuário envia `/git_Invite/*` com o seu email, que deve estar atrelado a uma conta do Git, na frente da segunda barra. O Bot faz um request à API do GitHub, e então um convite para adentrar a organização chega no email fornecido.

    - #### Inicialização e dependências
        ``` 
            git_Invite = git_invite.gitInvite(bot, GIT_TOKEN, GIT_API_INVITE_ENDPOINT, session)
        ```

        | Parâmetro                | Descrição               |
        | :------------------------|:-----------------------|
        | `bot`                    | Instância do AsyncTeleBot |

    [⬆️ Voltar ao Topo](#Manual-de-Handlers)


## Módulo: help.py 🫂

- ### Help
    - #### Atributos
        - ⚙️ **Comando:** `/help`.
        - 📋 **Menu de Comandos:** Sim.
        - 📝 **/help:** Sim.
        - 🔎 **Escopo:** All.
        - 🗝️ **Permissão:** Qualquer Usuário.

    - #### Função
        - O handler Help é a principal documentação interna para expor as funcionalidades do Bot aos usuários.

    - #### Fluxo de comunicação
        1.  **Solicitação:** O usuário envia `/help`. O bot envia um resumo dos principais comandos e as suas ações.

    - #### Inicialização e dependências
        ```
            help_command = help.Help(bot)
        ```

        | Parâmetro                | Descrição               |
        | :------------------------|:-----------------------|
        | `bot`                    | Instância do AsyncTeleBot |
        
    [⬆️ Voltar ao Topo](#Manual-de-Handlers)

## Módulo: links.py 🔗

- ### ShowLinks
    - #### Atributos
        - ⚙️ **Comando:** `/links`.
        - 📋 **Menu de Comandos:** Sim.
        - 📝 **/help:** Sim.
        - 🔎 **Escopo:** All.
        - 🗝️ **Permissão:** Qualquer Usuário.

    - #### Função
        - O handler ShowLinks envia uma mensagem contendo os links importantes do Codelab, como o do Insta, do Notion, entre outros.

    - #### Fluxo de comunicação
        1. **Solicitação:** O usuário envia `/links`. O Bot envia uma mensagem contendo os hyperlinks importantes do grupo.

    - #### Inicialização e dependências
        ``` 
            link = links.show_links(bot)
        ```

        | Parâmetro                | Descrição               |
        | :------------------------|:-----------------------|
        | `bot`                    | Instância do AsyncTeleBot |

    [⬆️ Voltar ao Topo](#Manual-de-Handlers)
    
## Módulo: start.py 🏁

- ### Start
    - #### Atributos
        - ⚙️ **Comando:** `/start`.
        - 📋 **Menu de Comandos:** Sim.
        - 📝 **/help:** Sim.
        - 🔎 **Escopo:** All.
        - 🗝️ **Permissão:** Qualquer Usuário.

    - #### Função
        - O handler Start é a primeira interação que um usuário faz com o Bot. Ele cumprimenta o usuário e o direciona para o comando `/help`, para que se informe melhor sobre as utilidades do Bot.


    - #### Fluxo de comunicação
        1.  **Solicitação:** O usuário envia `/start`. O bot se apresenta, e envia um atalho para conhecer melhor a atuação do bot (`/help`).            

    - #### Inicialização e dependências
        ```
            start_command = start.Start(bot)
        ```

        | Parâmetro                | Descrição               |
        | :------------------------|:-----------------------|
        | `bot`                    | Instância do AsyncTeleBot |

    [⬆️ Voltar ao Topo](#Manual-de-Handlers)

## Módulo: suggestions.py 💡

- ### SuggestionMain
    - #### Atributos
        - ⚙️ **Comando:** `/suggestion`.
        - 📋 **Menu de Comandos:** Sim.
        - 📝 **/help:** Não.
        - 🔎 **Escopo:** All.
        - 🗝️ **Permissão:** Qualquer Usuário.

    - #### Função
        - O handler SuggestionMain atua como um guia do sistema de sugestões. Ele envia um menu que direciona o usuário para as ações de adicionar ou de visualizar sugestões, ou então de receber dicas de contribuição.

    - #### Fluxo de comunicação
        1. **Solicitação:** O usuário envia `/suggestion`. O Bot envia um menu informativo contendo:
            - Atalho para adicionar sugestão (`/suggestion_add`).
            - Atalho para listar sugestões (`/suggestion_list`).
            - Recomendação de leitura do guia (`/suggestion_guide`).

    - #### Inicialização e dependências
        ``` 
            suggestion_main = suggestions.SuggestionMain(bot)
        ```

        | Parâmetro                | Descrição               |
        | :------------------------|:-----------------------|
        | `bot`                    | Instância do AsyncTeleBot |

    [⬆️ Voltar ao Topo](#Manual-de-Handlers)

- ### SuggestionAdd
    - #### Atributos
        - ⚙️ **Comando:** `/suggestion_add`.
        - 📋 **Menu de Comandos:** Não.
        - 📝 **/help:** Sim.
        - 🔎 **Escopo:** All.
        - 🗝️ **Permissão:** Qualquer Usuário.

    - #### Função
        - O handler SuggestionAdd coleta a categoria da issue a ser adicionada, recebe o texto do usuário, valida, formata e então publica a nova sugestão no repositório do bot.


    - #### Fluxo de comunicação
        1.  **Solicitação:** O usuário envia `/suggestion_add`. O Bot apresenta os botões de categoria `FEATURE`, `FIX`, `OUTRO`.

        2. **Seleção**: Usuário clica na categoria desejada.

        3. **Submissão de sugestão**: Usuário envia o texto da sugestão.
            - *Validação:* O texto deve conter `:` separando título e corpo e ter no máximo 600 caracteres, caso contrário, o usuário é alertado do erro cometido e o fluxo é encerrado.

        4. **Confirmação:** O Bot exibe uma prévia formatada. Se o usuário confirmar, o Bot envia para o GitHub e notifica o usuário do sucesso.

    - #### Inicialização e dependências
        ```
            suggestions_add = suggestions.SuggestionAdd(bot, GIT_LINK_ISSUES, GIT_API_ISSUE_ENDPOINT, GIT_TOKEN, session)
        ``` 
        
        | Parâmetro                | Descrição               |
        | :------------------------|:-----------------------|
        | `bot`                    | Instância do AsyncTeleBot |
        | `GIT_LINK_ISSUES`        | Url das issues abertas no repositório |
        | `GIT_API_ISSUE_ENDPOINT` | Endpoint da API do Github de manipular issues |
        | `GIT_TOKEN`              | Token de autenticação da API do GitHub |
        | `session`                | Sessão `aiohttp.ClientSession` para requisições assíncronas |

    [⬆️ Voltar ao Topo](#Manual-de-Handlers)

- ### SuggestionList
    - #### Atributos
        - ⚙️ **Comando:** `/suggestion_list`.
        - 📋 **Menu de Comandos:** Não.
        - 📝 **/help:** Sim.
        - 🔎 **Escopo:** All.
        - 🗝️ **Permissão:** Qualquer Usuário.

    - #### Função
        - O handler SuggestionList conecta-se à API do GitHub para recuperar e listar as issues abertas, permitindo que o usuário visualize o backlog atual do projeto diretamente pelo Telegram.

    - #### Fluxo de comunicação
        1.  **Solicitação:** O usuário envia `/suggestion_list`. O Bot apresenta os botões de categoria `TODOS`, `FEATURE`, `FIX`, `OUTRO`.

        2. **Seleção**: Usuário clica na categoria desejada. O Bot envia uma mensagem listando todas as issues na opção escolhida (paginando de 5 em 5 por mensagem), ou informa que não há issues em aberto na categoria informada.

    - #### Inicialização e dependências
        ```
            suggestions_list = suggestions.SuggestionList(bot, GIT_LINK_ISSUES, GIT_API_ISSUE_ENDPOINT, GIT_TOKEN, session)
        ```

        | Parâmetro                | Descrição               |
        | :------------------------|:-----------------------|
        | `bot`                    | Instância do AsyncTeleBot |
        | `GIT_LINK_ISSUES`        | Url das issues abertas no repositório |
        | `GIT_API_ISSUE_ENDPOINT` | Endpoint da API do Github de manipular issues |
        | `GIT_TOKEN`              | Token de autenticação da API do GitHub |
        | `session`                | Sessão `aiohttp.ClientSession` para requisições assíncronas. |

    (mesmas do SuggestionAdd)

    [⬆️ Voltar ao Topo](#Manual-de-Handlers)


- ### SuggestionGuide
    - #### Atributos
        - ⚙️ **Comando:** `/suggestion_guide`.
        - 📋 **Menu de Comandos:** Não.
        - 📝 **/help:** Sim.
        - 🔎 **Escopo:** All.
        - 🗝️ **Permissão:** Qualquer Usuário.

    - #### Função
        - O handler SuggestionGuide fornece instruções para o usuário, explicando as melhores práticas para escrever uma issue clara e útil.

    - #### Fluxo de comunicação
        1.  **Solicitação:** O usuário envia `/suggestion_guide`. O Bot envia 3 mensagens sequenciais contendo regras, instruções e dicas.

        2. **Exemplos interativos (opcional):** A última mensagem contém botões `Exemplo Feature`, `Exemplo Fix`, `Èxemplo Outro`. Ao clicar, o Bot sorteia e exibe um exemplo real extraído do arquivo JSON de exemplos.

    - #### Inicialização e dependências
        ```
            suggestion_guide = suggestions.SuggestionGuide(bot, SUGGESTION_EXAMPLES)
        ```

        | Parâmetro                | Descrição               |
        | :------------------------|:-----------------------|
        | `bot`                    | Instância do AsyncTeleBot |
        | `SUGGESTION_EXAMPLES`    | Caminho (str) para o arquivo JSON com exemplos de issues divididas por categoria|

    [⬆️ Voltar ao Topo](#Manual-de-Handlers)

- ### BuggedCommand
    - #### Atributos
        - ⚙️ **Comando:** `/bugged_command`.
        - 📋 **Menu de Comandos:** Não.
        - 📝 **/help:** Não.
        - 🔎 **Escopo:** All.
        - 🗝️ **Permissão:** Qualquer Usuário.

    - #### Função
        - O handler BuggedCommand é intencionalmente defeituoso. Serve para ilustrar os exemplos de issue de bug do SuggestionGuide.

    - #### Fluxo de comunicação
        1.  **Solicitação:** O usuário envia `/bugged_command`
        2. **Comportamentos (bugs simulados):**
            *   *Quintas-feiras:* O comando é ignorado quando usado nas quintas-feiras.
            *   *Duplicação:* Envia a mensagem "😃 Eu sou um bug!" duas vezes.
            *   *Botões defeituosos:* O botão "bug 1" não faz nada e o botão "bug 2" dispara uma exceção `PoorUseOfCommand` proposital.

    - #### Inicialização e dependências
        ```
            bugged_command = suggestions.BuggedCommand(bot)
        ```

        | Parâmetro                | Descrição               |
        | :------------------------|:-----------------------|
        | `bot`                    | Instância do AsyncTeleBot |


    [⬆️ Voltar ao Topo](#Manual-de-Handlers)

