# Interface: Servidor de e-mail de saída

> Tipo: SMTP, cliente. Direção: saída
> Feature: `001-captura-voz-ao-arquivo`
> Componente: `digest-semanal`

## 1. Papel no sistema

🟡 Entrega o digest semanal. É o único componente que fala com o usuário por iniciativa própria, sem que ele tenha pedido nada.

🟡 Foi escolhido em vez do Telegram por um motivo de comportamento, não técnico: **e-mail é lido sentado**, que é o modo correto para a retomada. Telegram é lido em movimento, e marcar "feito" em movimento tende a ser mentira.

## 2. Operação

| Operação | Uso | Frequência |
|---|---|---|
| 🟡 Autenticar e enviar mensagem | Entrega o digest | Uma vez por semana |

🟡 Não há recepção. O sistema **não lê caixa de entrada** — foi decisão explícita, para evitar a máquina de ler inbox por IMAP. A ação do usuário volta pelos links, não por resposta ao e-mail.

## 3. Requisição

```
🟡 Enviar
  servidor:     SMTP_SERVIDOR : SMTP_PORTA        // padrão 587
  autenticação: SMTP_USUARIO / SMTP_SENHA
  remetente:    DIGEST_EMAIL_REMETENTE
  destinatário: DIGEST_EMAIL_DESTINO              // exatamente um, sem lista
  assunto:      identificação do digest e da semana
  corpo:        até DIGEST_QUANTIDADE registros, mais antigos primeiro
```

🟡 Recomenda-se **senha de aplicativo específica**, nunca a senha principal da conta. Provedores comuns exigem isso de qualquer forma, e uma senha principal em `.env` é risco desproporcional.

## 4. Conteúdo da mensagem

Por registro incluído:

| Elemento | Origem |
|---|---|
| 🟡 Assunto | `Registro.assunto` |
| 🟡 Próximos passos | `Registro.proximos_passos`, lista completa |
| 🟡 Data de captura | `Registro.capturado_em` |
| 🟡 Marcação de origem | Destaque quando `origem = reuniao` |
| 🟡 Dois links | `PAINEL_URL_BASE` + identificador + ação |

Mais, no rodapé:

- 🟡 Total de pendentes no acervo, para o usuário perceber acúmulo sem abrir o painel

🟡 **A mensagem precisa permanecer legível com imagens bloqueadas.** Nenhum conteúdo essencial pode depender de recurso remoto, porque clientes de e-mail bloqueiam imagens por padrão e um digest que chega vazio é indistinguível de falha.

## 5. Erros e tratamento

| Condição | Comportamento |
|---|---|
| 🟡 Servidor indisponível | Registrar falha e tentar na execução seguinte. **Sem acumular envios atrasados** |
| 🟡 Credenciais inválidas ou expiradas | Erro **distinto** de indisponibilidade, nomeando a autenticação, para que a causa fique evidente |
| 🟡 Destinatário rejeitado | Erro explícito nomeando o endereço configurado |
| 🟡 Máquina desligada no horário | Enviar na primeira execução seguinte, **uma única vez** |
| 🟡 Nenhum registro pendente | Enviar assim mesmo, informando a ausência |

🟡 As duas últimas linhas parecem contraditórias e não são. Não acumular envios atrasados protege contra receber três digests ao voltar de viagem, que é a forma mais rápida de aprender a ignorá-los. Enviar mesmo sem pendentes protege contra o silêncio, que é indistinguível de falha. As duas defendem a mesma coisa: a confiança no ritual semanal.

## 6. Idempotência

🟡 **No máximo um envio por semana**, garantido por registro de envio persistido com a semana correspondente.

🟡 Envio duplicado não corrompe dado algum, mas acelera a perda de eficácia do digest, que é o risco de meia-vida já registrado. Por isso a garantia existe.

## 7. Tempos limite

| Operação | Limite |
|---|---|
| 🟡 Conexão e autenticação | 30 segundos |
| 🟡 Envio da mensagem | 60 segundos |

🟡 Falha por tempo excedido é tratada como indisponibilidade transitória e entra na política de nova tentativa na execução seguinte.

## 8. Dependência e substituição

🟡 Indisponibilidade do servidor de e-mail **não afeta captura, transcrição, classificação nem arquivamento**. Apenas a devolução semanal deixa de ocorrer, e os registros permanecem pendentes, reaparecendo no envio seguinte. Nada se perde.

🟡 Trocar o canal de entrega afeta este componente e os links de marcação. Os endereços gravados em e-mails já enviados continuariam válidos enquanto o painel mantivesse o contrato descrito em `painel-http.md`.
