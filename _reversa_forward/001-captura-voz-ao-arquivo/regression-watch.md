# Regression Watch: 001-captura-voz-ao-arquivo

> Identificador da feature: `001-captura-voz-ao-arquivo`
> Data: `2026-08-11`
> **Cenário greenfield.** Não há regras 🟢 a vigiar, porque nada foi extraído de código existente ainda.

## Watch principal

| ID | Origem (arquivo, seção) | Regra esperada após mudança | Tipo de verificação | Sinal de violação |
|----|--------------------------|------------------------------|---------------------|-------------------|
| — | — | — | — | — |

🟡 Vazio por construção. O watch principal só admite regras que eram 🟢, ou seja, confirmadas a partir de código real. Neste projeto o código acabou de nascer e ainda não foi extraído por `/reversa`.

🟡 Os itens da seção Observações abaixo **ganham peso de regressão** quando uma futura extração `/reversa` sobre este código os confirmar como 🟢. Até lá, são expectativas, não garantias.

## Observações, sem peso de regressão

🟡 Comportamentos implementados na Fase 1 que deveriam permanecer verdadeiros. Cada um tem um teste correspondente já previsto no `actions.md`.

| ID | Comportamento esperado | Origem | Como verificar | Teste previsto |
|----|------------------------|--------|----------------|----------------|
| O-001 | Ausência de qualquer parâmetro obrigatório impede a inicialização e nomeia o parâmetro faltante | `requirements.md#RF-16` | Remover um obrigatório do `.env` e iniciar | T011 |
| O-002 | `TELEGRAM_USUARIO_AUTORIZADO` vazio **nunca** resulta em modo permissivo | `sdd/captura-telegram.md#9.1` | Esvaziar o campo e iniciar; precisa recusar | T011 |
| O-003 | `PAINEL_INTERFACE` fora de loopback impede a inicialização | `requirements.md#RF-15` | Configurar `0.0.0.0` e iniciar | T012 |
| O-004 | Divergência entre `PAINEL_URL_BASE` e o par interface/porta gera alerta, sem impedir a inicialização | `requirements.md#RF-19` | Alterar `PAINEL_PORTA` sem alterar a URL base | T012 |
| O-005 | Com `.env` nos padrões, painel e digest concordam por construção e não há alerta | `sdd/painel-acompanhamento.md#9.1` | Iniciar sem sobrescrever porta ou URL | T012 |
| O-006 | Criação de diretórios é idempotente e nunca cria, move ou apaga arquivo | `sdd/acervo-markdown.md#EC-10` | Executar duas vezes; a segunda não cria nada | — |
| O-007 | Log jamais registra token, chave de API, senha ou texto bruto capturado | `sdd/captura-telegram.md#12` | Passar um token a uma chamada de log e conferir o mascaramento | — |
| O-008 | O prompt de classificação vive fora do código e é editável sem alteração de implementação | `sdd/classificacao-ia.md#RF-10` | Editar `config/prompt_classificacao.txt` e reiniciar | — |

🟡 **Estado da cobertura após a Fase 2** (T011 e T012 executados, 38 testes passando):

| Observação | Coberta por | Situação |
|---|---|---|
| O-001 | `tests/test_config.py` | ✅ um caso por parâmetro obrigatório, mais o caso de erro coletivo |
| O-002 | `tests/test_config.py` | ✅ campo vazio e campo não numérico, ambos recusam iniciar |
| O-003 | `tests/test_config_rede.py` | ✅ quatro endereços de loopback aceitos, seis externos recusados |
| O-004 | `tests/test_config_rede.py` | ✅ divergência de porta, de host e URL malformada, todas alertando sem impedir |
| O-005 | `tests/test_config_rede.py` | ✅ padrões concordam, zero alertas |
| O-006 | `tests/test_config.py` | ✅ **coberto por oportunidade**, não estava previsto no `actions.md` |
| O-007 | — | 🔴 **sem teste.** Verificado manualmente na Fase 1 |
| O-008 | — | 🔴 **sem teste.** Verificado manualmente na Fase 1 |

🟡 O-006 ganhou teste porque o caso de idempotência de diretórios cabia naturalmente no arquivo de configuração. O-007 (mascaramento de segredo em log) e O-008 (prompt fora do código) continuam sem rede de proteção e merecem uma ação nova no `actions.md` — o mascaramento em particular é a diferença entre um log limpo e um token do bot em texto claro no disco.

## Observações acrescentadas nas fases 3, 4 e 5

| ID | Comportamento esperado | Origem | Teste |
|----|------------------------|--------|-------|
| O-009 | Interrupção durante a gravação nunca deixa arquivo parcial, e a regravação que falha preserva o conteúdo anterior | `sdd/acervo-markdown.md#RNF-02` | T013 |
| O-010 | O identificador de um registro sobrevive a renomeação e a mudança de pasta | `requirements.md#RF-07` | T014 |
| O-011 | `ACERVO_TAMANHO_MAX_NOME` limita o nome inteiro, não só o fragmento do assunto | correção da fase 2 | T014 |
| O-012 | A fila retoma pela etapa registrada, sem repetir transcrição concluída nem duplicar registro | `requirements.md#RF-10` | T015 |
| O-013 | A fronteira de classificação não importa nenhum pacote de provedor | `requirements.md#RF-04` | T016 |
| O-014 | O pipeline funciona com o adaptador simulado sem que o pacote do fornecedor seja importado | `requirements.md#RF-04` | T016 |
| O-015 | **Requisição de leitura na página de confirmação nunca altera estado**, mesmo repetida | `requirements.md#RF-12` | T017 |
| O-016 | Marcação por POST é idempotente | `sdd/painel-acompanhamento.md#RF-14` | T017 |
| O-017 | O endereço de marcação tem formato estável: mudá-lo quebra digests já enviados | `sdd/painel-http.md` | T017 |
| O-018 | O digest seleciona apenas pendentes, mais antigos primeiro, respeitando o limite | `requirements.md#RF-11` | T018 |
| O-019 | O digest é enviado mesmo sem registros pendentes | `requirements.md#RF-18` | T018 |
| O-020 | Registro de reunião é marcado como tal no painel e no digest | `requirements.md#RN-09` | T018 |
| O-021 | Transcrição sem pontuação confiável ainda é dividida em blocos para a segunda passagem | correção da fase 3 | — |
| O-022 | Porta ocupada impede a inicialização do painel em vez de escolher outra | `sdd/painel-http.md#EC-10` | — |
| O-023 | O deslocamento de leitura do polling só avança após o processamento concluir | `sdd/captura-telegram.md#RNF-04` | — |
| O-024 | Falha no envio do digest não consome a semana: o envio ocorre na execução seguinte, uma única vez | `sdd/digest-semanal.md#RF-09` | — |

🟡 **O-021 a O-024 foram verificados por execução manual e não têm teste automatizado.** As duas primeiras nasceram de defeitos reais encontrados durante a implementação, o que as torna candidatas óbvias a virar teste antes do próximo ciclo.

## Histórico de re-extrações

| Data | Extração | Itens verificados | Violações |
|------|----------|-------------------|-----------|
| 2026-08-11 | **Verificação direcionada** (não foi re-extração completa) | 24 de 24 | **0** |

### 2026-08-11 — verificação direcionada

🟡 **O que foi feito.** O usuário optou por verificar as observações contra o código real em vez de rodar o `/reversa` completo. Cada uma das 24 foi checada por execução ou por inspeção estrutural do código, não por leitura de intenção. Resultado: **24 confirmadas, nenhuma violação.**

🟡 **Verificações que exigiram execução, não inspeção:**

| Observação | Como foi confirmada |
|---|---|
| O-001 | Os oito obrigatórios removidos um a um; todos recusam iniciar **e nomeiam o parâmetro** |
| O-003 | Quatro endereços externos recusados, três de loopback aceitos |
| O-009 | `os.replace` sabotado no meio da regravação: conteúdo anterior preservado, nenhum temporário deixado |
| O-010 | Registro renomeado e movido de pasta; identificador intacto |
| O-012 | Item retomado em `TRANSCRITO` executou apenas `classificar` e `arquivar` |
| O-013 | Árvore sintática de `fronteira.py` auditada: 3 imports, nenhum de provedor |
| O-014 | `__import__` instrumentado durante o caminho simulado: o pacote do fornecedor não foi tocado |
| O-015 | Cinco requisições de leitura seguidas na página de confirmação, via cliente HTTP real: estado inalterado |
| O-021 | Transcrição de 3000 palavras sem pontuação dividida em 2 blocos |
| O-023 | Ordem das chamadas no laço de captura auditada: `estado.salvar()` vem depois de `processar()` |
| O-024 | Ordem em `despachar_digest` auditada: o retorno em caso de falha antecede `agendador.concluir()` |

🟡 **Ressalva de precisão sobre O-006.** A idempotência foi confirmada (segunda execução cria zero diretórios), mas a metade "cria o que falta" não foi exercitada nesta rodada, porque os diretórios já existiam. Essa metade está coberta pelo teste `test_criacao_de_diretorios_e_idempotente`, que verifica as duas.

🟡 **O que esta verificação NÃO faz, e é importante.** Ela não é uma re-extração. Nenhum artefato 🟢 foi gerado em `<output_folder>/` a partir do código, e por isso:

- **O watch principal continua vazio.** O selo 🟢 do framework designa fato extraído de código pelo Time de Descoberta, e essa extração não ocorreu. As 24 seguem como observações — agora *verificadas*, o que é mais forte que antes e menos que 🟢.
- **O adendo `001-captura-voz-ao-arquivo.md` continua vigente**, sem linha de superação. Só uma re-extração completa o supera.

🟡 **Por que o usuário adiou a re-extração completa.** A distância entre o que está documentado e o que é real tinha, nesta data, duas horas de idade e estava integralmente registrada no adendo. Re-extração se paga quando essa distância é real e desconhecida — depois de uso, de edições manuais e de mais features entregues.

## Arquivadas

🟡 Vazio.
