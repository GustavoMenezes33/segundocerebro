# Interface: API do Telegram

> Tipo: HTTP, cliente. Direção: **saída sempre**, inclusive na recepção
> Feature: `001-captura-voz-ao-arquivo`
> Componente: `captura-telegram`

## 1. Papel no sistema

🟡 Único ponto de entrada de insights. Também é o canal de resposta, usado para aviso de recebimento, confirmação e erro.

🟡 **Propriedade que sustenta a arquitetura:** todas as chamadas partem da máquina local. Não existe endereço de entrada, porta aberta nem certificado. É o que permite o acervo ser local sem expor a máquina.

## 2. Operações consumidas

| Operação | Uso | Frequência |
|---|---|---|
| 🟡 Obter atualizações, em modo long polling | Recebe mensagens novas | Contínua, conexão mantida aberta |
| 🟡 Obter metadados de arquivo | Resolve o caminho de download do áudio | Uma vez por mensagem de voz |
| 🟡 Baixar arquivo | Traz o áudio para o disco local | Uma vez por mensagem de voz |
| 🟡 Enviar mensagem | Aviso de recebimento, confirmação e erro | Duas a três vezes por captura |

## 3. Requisição de recepção

```
🟡 Obter atualizações
  offset:  ultimo_update_id + 1     // deslocamento persistido, garante exatamente-uma-vez
  timeout: 30 segundos              // long polling; conexão fica aberta aguardando novidade
  allowed_updates: ["message"]      // ignora edições, reações e demais eventos
```

🟡 O `offset` é a peça central da entrega exatamente-uma-vez. Ele só avança **depois** que a mensagem foi arquivada com sucesso ou marcada como falha definitiva. Avançar antes trocaria duplicata por perda, e perda é inaceitável.

## 4. Resposta esperada e campos consumidos

| Campo | Uso |
|---|---|
| 🟡 `update_id` | Atualiza o deslocamento persistido |
| 🟡 `message.message_id` | Identificador de deduplicação |
| 🟡 `message.from.id` | **Validado contra `TELEGRAM_USUARIO_AUTORIZADO` antes de qualquer processamento** |
| 🟡 `message.chat.id` | Destino das respostas |
| 🟡 `message.voice.file_id` | Referência para download do áudio |
| 🟡 `message.voice.duration` | **Determina a política aplicada**: nota curta ou áudio longo |
| 🟡 `message.text` | Fluxo alternativo de captura por texto |
| 🟡 `message.date` | Momento da captura, mesmo quando a entrega foi atrasada por falta de sinal |

🟡 `message.date` é preferido ao momento do recebimento local. Uma mensagem gravada em túnel e entregue duas horas depois deve constar no acervo com a hora em que o insight ocorreu, não com a hora em que a rede voltou.

## 5. Erros e tratamento

| Condição | Comportamento |
|---|---|
| 🟡 Token inválido ou revogado | Falha explícita na inicialização, nomeando o token. Nunca laço silencioso de tentativas |
| 🟡 Limite de requisições atingido | Respeitar a espera indicada pela API e retomar. Nenhuma mensagem é descartada por limite |
| 🟡 Falha de rede no laço de recepção | Nova tentativa com espera crescente. Mensagens permanecem retidas no serviço e nada se perde |
| 🟡 Falha no download do áudio | Até três tentativas com espera crescente. Persistindo, erro no chat nomeando a etapa de download |
| 🟡 Falha ao enviar resposta | Registrar em log. O registro já está arquivado, então a falha afeta a notificação e não o dado |
| 🟡 Remetente não autorizado | Descartar em silêncio, sem responder. Registrar a tentativa no log |

🟡 Responder a remetente não autorizado confirmaria a existência do bot a quem não deveria saber. O silêncio é deliberado.

## 6. Idempotência

🟡 Garantida pelo par deslocamento persistido mais identificador de mensagem. Uma mensagem já arquivada nunca gera segundo registro, mesmo que o processo seja interrompido e reiniciado no meio do processamento.

🟡 O envio de respostas **não** é idempotente: uma interrupção após arquivar e antes de responder pode gerar confirmação duplicada no chat em caso de reprocessamento. Consequência aceita, por ser cosmética e infinitamente preferível a registro duplicado no acervo.

## 7. Tempos limite

| Operação | Limite | Origem |
|---|---|---|
| 🟡 Long polling | 30 segundos por ciclo | Valor da própria requisição; ciclo reaberto em seguida |
| 🟡 Download de áudio | `CAPTURA_TIMEOUT_DOWNLOAD_S`, padrão 30 s | Configurável; áudio de reunião pode exigir valor maior |
| 🟡 Envio de mensagem | 10 segundos | Falha aqui não bloqueia o pipeline |

## 8. Dependência e substituição

🟡 Canal único de captura. Indisponibilidade do serviço interrompe a entrada, mas **nada se perde**: as mensagens ficam retidas no aplicativo do usuário ou nos servidores do serviço e são processadas quando a conexão volta.

🟡 Substituir o canal afeta somente este componente. O restante do pipeline recebe áudio e metadados por uma fronteira interna, e não conhece a origem.
