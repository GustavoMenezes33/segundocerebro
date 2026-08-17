# Interface: Painel local, HTTP

> Tipo: HTTP, servidor. Direção: entrada, **exclusivamente de loopback**
> Feature: `001-captura-voz-ao-arquivo`
> Componente: `painel-acompanhamento`

## 1. Papel no sistema

🟡 Serve a interface de acompanhamento e as páginas de confirmação usadas pelos links do digest.

🟡 **É um contrato local tratado como público.** Os endereços de marcação ficam gravados dentro de e-mails já enviados, que permanecem na caixa do usuário indefinidamente. Alterá-los quebra digests antigos, o que confere a esses endereços estabilidade de contrato externo mesmo nunca saindo da máquina.

## 2. Vinculação de rede

```
🟡 escuta em: PAINEL_INTERFACE : PAINEL_PORTA     // padrão 127.0.0.1:8000
```

| Regra | Comportamento |
|---|---|
| 🟡 Interface não-loopback configurada | **Recusar iniciar**, informando que apenas loopback é permitido |
| 🟡 Porta já em uso | **Recusar iniciar**, nomeando a porta. Jamais escolher outra silenciosamente |
| 🟡 Endereço efetivo diverge de `PAINEL_URL_BASE` | Alertar na inicialização, informando ambos |

🟡 Escolher outra porta automaticamente é o comportamento "gentil" que quebraria **todos** os links de digests já enviados, sem aviso. Falhar é a opção correta.

🟡 Não há autenticação. A proteção vem da vinculação a loopback, em máquina pessoal. Senha em serviço exposto protegeria menos.

## 3. Endpoints

| Método | Caminho | Uso |
|---|---|---|
| 🟡 GET | `/` | Painel: contagens do período e lista de registros |
| 🟡 GET | `/registro/<id>` | Registro individual, com texto bruto e próximos passos |
| 🟡 GET | `/registro/<id>/marcar/<acao>` | **Página de confirmação.** Não altera nada |
| 🟡 POST | `/registro/<id>/marcar/<acao>` | **Aplica** a mudança de estado |

🟡 `<acao>` assume `executado` ou `descartado`.

🟡 **A separação entre GET e POST é o requisito de integridade mais importante desta interface.** Clientes de e-mail, antivírus e filtros de segurança pré-carregam endereços contidos em mensagens. Se o GET alterasse estado, registros seriam marcados sozinhos, e um acervo que se altera sem o usuário destrói a confiança em todo o sistema, inclusive na parte correta.

## 4. Página de confirmação, comportamento

| Situação | Resposta |
|---|---|
| 🟡 Registro existe e está pendente | Exibe assunto, próximos passos e um botão de confirmação |
| 🟡 Registro já está no estado pretendido | Informa o estado atual. **Não é erro** |
| 🟡 Registro está em outro estado final | Informa o estado atual e permite alterar |
| 🟡 Registro não existe mais | Explica que o registro não foi encontrado. **Não é erro genérico** |
| 🟡 Ação desconhecida | Recusa, listando as ações válidas |

🟡 Nenhuma dessas situações retorna erro genérico. O usuário chegou ali por um link de um e-mail que pode ter semanas, e a página precisa explicar o que aconteceu, não falhar.

## 5. Idempotência

🟡 O POST **é idempotente**: confirmar duas vezes a mesma ação produz o mesmo estado final, sem erro. Toque duplicado é comum e não pode gerar comportamento estranho.

🟡 O GET é seguro por construção: **nunca** altera estado. É a garantia contra pré-carregamento.

## 6. Escrita permitida

🟡 Este componente escreve **exclusivamente** o campo de estado dos registros, mais a data e hora da mudança.

🟡 Proibido alterar assunto, tipo, próximos passos, origem e, sobretudo, o texto bruto. O usuário edita conteúdo no editor que já usa; restringir a escrita reduz a superfície de dano.

## 7. Conflito com edição manual

| Situação | Comportamento |
|---|---|
| 🟡 Arquivo alterado no editor entre a leitura e a escrita | Detectar o conflito, **preservar o conteúdo em disco** e informar que a marcação não foi aplicada |
| 🟡 Arquivo apagado manualmente | Informar que o registro não existe mais, sem tentar recriá-lo |

🟡 O arquivo em disco é sempre a fonte da verdade. O índice é derivado e se ajusta na reconstrução.

## 8. Tempos limite e desempenho

| Operação | Alvo |
|---|---|
| 🟡 Carga do painel | Abaixo de 3 segundos para até 1000 registros |
| 🟡 Página de confirmação | Abaixo de 1 segundo |
| 🟡 Aplicação da marcação | Abaixo de 5 segundos |

🟡 Marcação lenta faz o usuário duvidar se a ação foi registrada, e a dúvida leva ao clique repetido, que é por que o POST precisa ser idempotente.

## 9. Acoplamento com o digest

🟡 `PAINEL_URL_BASE`, definido em `digest-semanal`, precisa corresponder a `PAINEL_INTERFACE` e `PAINEL_PORTA` definidos aqui.

🟡 Divergência produz um digest que chega **íntegro**, com todos os links apontando para lugar nenhum. É falha silenciosa, a categoria de defeito que este produto existe para evitar, e o alerta de inicialização é a única defesa contra ela.

🟡 Com o `.env` vazio, os dois lados assumem `127.0.0.1:8000` e concordam por construção. A divergência só pode nascer de alteração deliberada.
