# Onboarding: 001-captura-voz-ao-arquivo

> Passo a passo para testar a feature pela primeira vez
> Data: `2026-08-11`

🟡 Este documento assume que a feature já foi construída. Ele descreve como um humano verifica, com as próprias mãos, que ela funciona. Os passos estão em ordem de dependência: cada um só faz sentido se o anterior passou.

## Passo 0, medição da classificação

> 🟡 **O teste Mago de Oz foi removido do plano** por decisão do usuário, em 2026-08-11, dado o caráter também acadêmico do projeto. Ele era um portão bloqueante executado antes de qualquer código. A verificação que restou acontece **depois** de a `classificacao-ia` estar construída, no passo 3 da ordem de construção, e não impede a continuidade.

🟡 Quando a `classificacao-ia` estiver de pé, antes de fechar a esteira completa:

1. Reunir pelo menos vinte transcrições reais, geradas pelo Whisper já construído no passo anterior, a partir de áudio gravado no contexto real, inclusive dirigindo.
2. Rodar a classificação sobre elas.
3. Julgar as vinte saídas, uma a uma, e **registrar o número**, mesmo que seja ruim.

🟡 O número não bloqueia nada, e por isso mesmo precisa ser anotado: é a única referência objetiva que você terá para saber se um ajuste de prompt melhorou ou piorou a classificação. Sem ele, qualquer mudança futura vira impressão.

🟡 Aproveite para conferir quais **tipos de registro** aparecem de fato. Os cinco configurados foram fixados por escolha e não por observação, e é aqui que você descobre se algum nunca é atribuído ou se falta algum.

🟡 **Cuidado metodológico:** use transcrições reais do Whisper, não texto digitado à mão. Texto limpo mede a classificação sobre a melhor entrada possível e produz um número otimista que o sistema real não vai reproduzir, porque a entrada verdadeira vem de áudio com ruído de trânsito e fala ao volante.

## Passo 1, preparar o ambiente

1. Instalar Python e as dependências do projeto.
2. Copiar o arquivo de exemplo de configuração para `.env`.
3. Preencher os **oito parâmetros obrigatórios**:
   - `TELEGRAM_BOT_TOKEN` e `TELEGRAM_USUARIO_AUTORIZADO`
   - `LLM_API_KEY`, `LLM_PROVEDOR` e `LLM_MODELO`
   - `DIGEST_EMAIL_DESTINO`, `DIGEST_EMAIL_REMETENTE` e as credenciais `SMTP_*`
4. Deixar os demais nos padrões. Eles foram escolhidos para funcionar sem ajuste.

🟡 **Como obter o token do bot:** falar com o BotFather no Telegram e criar um bot novo. **Como obter seu identificador de usuário:** enviar mensagem para um bot que reporte o próprio identificador, ou consultar o retorno da API após enviar a primeira mensagem ao seu bot.

🟡 **Verificação:** iniciar o sistema com `TELEGRAM_USUARIO_AUTORIZADO` vazio. Ele deve **recusar iniciar**, nomeando o parâmetro ausente. Se subir mesmo assim, há um defeito grave: o sistema estaria aceitando qualquer remetente.

## Passo 2, primeira captura por texto

🟡 Comece pelo caminho mais curto, que não envolve áudio nem transcrição.

1. Iniciar o sistema.
2. Enviar ao bot uma mensagem de **texto**: algo como "testar se a captura funciona".
3. **Esperado:** resposta de confirmação no chat, com um assunto atribuído.
4. Abrir a pasta do acervo e confirmar que existe um arquivo markdown novo.
5. Abrir o arquivo em qualquer editor de texto e conferir que ele é legível, com metadados no topo e o texto original preservado.

🟡 O passo 5 é o mais importante do documento. Se o arquivo não for legível sem o sistema, o requisito central de portabilidade falhou.

## Passo 3, primeira captura por voz

1. Gravar uma mensagem de voz curta pelo Telegram, de trinta segundos ou menos.
2. **Esperado:** aviso de recebimento, seguido da confirmação com o assunto, em até sessenta segundos.
3. Conferir que o arquivo de áudio original foi preservado na pasta configurada.
4. Conferir que o registro contém o texto bruto da transcrição.

🟡 **Anote o tempo real** entre o envio e a confirmação. É esse número que decide se o modelo de Whisper configurado serve ou precisa ser trocado por um menor.

## Passo 4, os casos que costumam quebrar

🟡 Testar as falhas é o que separa um sistema que parece funcionar de um que funciona.

1. **Sem sinal:** ativar o modo avião, gravar uma mensagem, desativar. A mensagem deve ser entregue sozinha e processada normalmente.
2. **Máquina desligada:** encerrar o sistema, enviar uma mensagem, reiniciar. A mensagem retida deve ser processada, com confirmação atrasada.
3. **Interrupção no meio:** encerrar o processo durante o processamento de um áudio e reiniciar. Não pode haver registro duplicado nem arquivo parcial no acervo.
4. **Remetente não autorizado:** pedir a outra pessoa que envie mensagem ao bot. Nada deve ser criado e ela não deve receber resposta.
5. **Classificação indisponível:** alterar `LLM_API_KEY` para um valor inválido e capturar. O registro deve ser arquivado assim mesmo, com o texto bruto íntegro e marcação de não classificado, e o chat deve informar o erro.

🟡 O caso 5 é o mais importante dos cinco: ele verifica a regra de que perder o insight é inaceitável e perder a estrutura é recuperável.

## Passo 5, reunião

1. Obter autorização verbal dos participantes **antes** de gravar, mencionando que o áudio será transcrito automaticamente e processado por um serviço externo.
2. Gravar a reunião e enviar pelo canal de captura.
3. **Esperado:** aviso de processamento estendido, seguido de confirmação quando concluir.
4. Conferir que o registro está marcado como originado de reunião e distinguível das notas pessoais.
5. Conferir que o registro traz **vários** próximos passos, e não apenas um.

🟡 **Anote o tempo total.** É a maior incógnita técnica da feature e a única forma de saber se reunião é viável nessa máquina.

## Passo 6, painel

1. Abrir o painel no navegador, no endereço anunciado na inicialização.
2. Conferir que as contagens batem com a contagem manual dos arquivos no acervo.
3. Marcar um registro como executado e conferir que o arquivo markdown em disco reflete a mudança.
4. Tentar acessar o painel a partir de outro aparelho da rede. **A conexão deve ser recusada.**
5. Configurar `PAINEL_INTERFACE` para um endereço externo e tentar iniciar. **Deve recusar iniciar.**

## Passo 7, digest

1. Ajustar temporariamente `DIGEST_DIA_SEMANA` e `DIGEST_HORARIO` para dali a poucos minutos.
2. Aguardar o envio e conferir a chegada do e-mail.
3. Conferir que vieram até cinco registros, dos **mais antigos primeiro**.
4. Clicar em um link de marcação. **Esperado:** abre uma página de confirmação, e o estado ainda **não** mudou.
5. Confirmar na página e conferir que o arquivo markdown mudou de estado.
6. Esvaziar o acervo de pendentes e aguardar o próximo envio. O e-mail deve chegar mesmo assim, informando que não há pendentes.
7. Restaurar dia e horário reais.

🟡 O passo 4 é a verificação de que o pré-carregamento de links por clientes de e-mail não marca registros sozinho. Se o estado mudar sem você confirmar, há um defeito sério.

## Passo 8, verificação final

🟡 Ao terminar, você deve conseguir responder sim a todas:

- [ ] Consigo ler qualquer registro do acervo sem o sistema estar rodando?
- [ ] Uma captura feita dirigindo chegou ao arquivo, com confirmação no chat?
- [ ] Uma falha proposital gerou erro visível, e não silêncio?
- [ ] Uma interrupção no meio do processamento não deixou lixo nem duplicata?
- [ ] O painel recusa conexão de fora da máquina?
- [ ] O digest chegou e um link marcou um registro, com confirmação explícita?

---
Gerado por `/reversa-plan` em 2026-08-11
