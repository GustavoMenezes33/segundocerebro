# Roadmap: Captura de voz ao arquivo, fatia fina de ponta a ponta

> Identificador: `001-captura-voz-ao-arquivo`
> Data: `2026-08-11`
> Requirements: `_reversa_forward/001-captura-voz-ao-arquivo/requirements.md`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA

> **Nota de contexto:** projeto greenfield. Não há legado sobre o qual escrever delta, então este roadmap descreve delta sobre o **conjunto de specs** em `_reversa_sdd/sdd/`, que fazem o papel do sistema mapeado. Nenhum item recebe selo 🟢, reservado a fatos extraídos de código existente.

## 1. Resumo da abordagem

🟡 Um único processo Python, executado na máquina do usuário, contendo seis módulos que espelham as seis specs. O processo mantém um laço de long polling contra a API do Telegram, e cada mensagem recebida percorre uma esteira de quatro etapas: baixar o áudio, transcrever localmente, classificar via API externa e arquivar em markdown. A confirmação volta ao chat ao final.

🟡 O mesmo processo hospeda um servidor HTTP local, que serve o painel e as páginas de confirmação usadas pelos links do digest, e um agendador interno que dispara o envio semanal por e-mail. Escolher um processo único, em vez de serviços separados, é a decisão que mais reduz complexidade operacional para um sistema de usuário único: um comando sobe tudo, e não há orquestração, fila externa nem banco.

🟡 A esteira é **única**, e a diferença entre nota de voz e reunião é tratada por **política dependente da duração do áudio**, não por caminhos separados. Áudio curto segue com os limites atuais; áudio longo recebe tempo limite próprio, aviso de processamento estendido e uma forma diferente de classificação, porque uma reunião contém muitos assuntos e uma nota de voz contém um.

🟡 O processamento é serializado por uma fila interna: apenas uma transcrição por vez, para não inutilizar a máquina pessoal do usuário durante rajadas de captura ou durante uma reunião longa.

## 2. Princípios aplicados

🟡 `.reversa/principles.md` não existe neste projeto. Nenhum princípio formal foi definido, portanto não há princípio a respeitar nem a conflitar.

| Princípio | Como a feature se relaciona | Status |
|-----------|------------------------------|--------|
| n/a | Nenhum princípio registrado em `.reversa/principles.md` | n/a |

🟡 Recomendação, fora do escopo deste skill: rodar `/reversa-principles` antes do segundo ciclo forward. Três candidatos emergiram naturalmente das decisões já tomadas e mereceriam status de princípio: *nenhuma falha pode ser silenciosa*, *perder o insight é inaceitável e perder a estrutura é recuperável*, e *o acervo precisa ser legível sem o software do projeto*.

## 3. Decisões técnicas

| ID | Decisão | Justificativa | Alternativas descartadas | Confidência |
|----|---------|----------------|--------------------------|-------------|
| D-01 | Processo único em Python hospedando o consumidor do Telegram, o servidor HTTP do painel e o agendador do digest | Usuário único, máquina única, sem requisito de escala. Um comando sobe tudo e não há orquestração a manter. O custo de separar seria pago todo dia sem contrapartida | Serviços separados por componente; contêineres; execução por tarefa agendada do sistema operacional | 🟡 |
| D-02 | Esteira única com política dependente da duração do áudio, em vez de caminhos separados para nota e reunião | As quatro etapas são idênticas nos dois casos; o que muda são limites e forma de classificação. Duplicar a esteira duplicaria também o tratamento de erro, que é a parte mais delicada | Pipelines separados por tipo de origem; componente dedicado a reuniões | 🟡 |
| D-03 | Reunião gera **um único registro**, cuja classificação carrega uma **lista** de próximos passos em vez de um só | Uma reunião de quarenta e cinco minutos contém muitos assuntos, e o modelo de um assunto com um próximo passo, correto para a nota no carro, produziria um registro inútil do tipo "reunião sobre vários temas" | Dividir automaticamente em N registros, um por tema; forçar um único próximo passo também para reunião | 🟡 |
| D-04 | Fila interna persistida em disco, com processamento estritamente serial | Protege a máquina pessoal durante rajadas e sobrevive a reinício, sustentando o requisito de exatamente-uma-vez. Persistir em disco evita depender de serviço de fila | Fila em memória; serviço de fila externo; processamento paralelo | 🟡 |
| D-05 | Adaptador de provedor de linguagem atrás de uma interface única, com **um** adaptador concreto implementado nesta entrega | Parametrizar sem implementar não classifica nada. A interface preserva a troca futura sem custo, conforme registrado no requirements | Cliente do provedor chamado diretamente de vários pontos; múltiplos adaptadores já nesta entrega | 🟡 |
| D-06 | Confirmação de marcação em duas etapas: o endereço do link apenas exibe a página, e a alteração de estado ocorre por envio explícito do formulário | Clientes de e-mail e antivírus pré-carregam endereços. Ação no carregamento marcaria registros sozinha, e um acervo que se altera sem o usuário destrói a confiança em todo o sistema | Link que altera o estado diretamente; token de uso único no endereço | 🟡 |
| D-07 | Agendador interno por verificação periódica de relógio, dentro do processo | Elimina dependência de agendador do sistema operacional, que difere entre plataformas e é a peça que o usuário esqueceria de configurar. Verificação a cada minuto basta para precisão semanal | Agendador do sistema operacional; serviço de agendamento dedicado | 🟡 |
| D-08 | Servidor HTTP local vinculado exclusivamente a endereço de loopback, com recusa de inicialização em qualquer outro | Requisito de segurança do requirements. Falhar ao iniciar é preferível a subir exposto, porque o erro de configuração fica visível em vez de silencioso | Vinculação a todas as interfaces com filtro por endereço de origem; autenticação por senha | 🟡 |
| D-09 | Acervo em arquivos markdown com cabeçalho de metadados estruturado, mais índice auxiliar em arquivo separado e descartável | Legibilidade sem o software do projeto é a única garantia real de que o acervo sobrevive. O índice acelera o painel e pode ser apagado a qualquer momento | Banco de dados como fonte da verdade; metadados em arquivo paralelo ao markdown | 🟡 |
| D-10 | Preservar áudio original e texto bruto da transcrição de forma permanente e imutável | Permite reclassificar o acervo inteiro sem reprocessar áudio quando o critério de classificação melhorar, mitigando o ponto sem volta registrado no PRD | Descartar o áudio após transcrever; sobrescrever o texto bruto com a versão refinada | 🟡 |
| D-11 | Aviso de recebimento imediato no chat, antes do processamento, e confirmação final ao término | Sem o aviso, o silêncio durante uma transcrição longa é indistinguível de falha, contrariando a regra de que nenhuma falha pode ser silenciosa | Responder apenas ao final; não responder nada em caso de sucesso | 🟡 |
| D-12 | Classificação de áudio longo em duas passagens: extração por blocos e consolidação final | Uma transcrição de quarenta e cinco minutos cabe no contexto dos modelos atuais, mas pedir um único assunto para ela produz resultado pobre. Duas passagens preservam os temas sem dividir o registro | Passagem única sobre a transcrição inteira; truncamento da entrada; divisão em vários registros | 🟡 |

## 4. Premissas

| Premissa | Origem (`requirements.md` seção) | Risco se errada |
|----------|----------------------------------|-----------------|
| 🟡 Nota de voz e reunião podem compartilhar a mesma esteira, diferindo apenas por política de duração | Seção 10, `[DÚVIDA]` sobre dimensionamento de áudio longo | Se as diferenças se mostrarem estruturais e não apenas de limite, a esteira única acumula condicionais e fica mais cara de manter do que dois caminhos explícitos. Sintoma a observar: condicionais por duração aparecendo em mais de três pontos do código |
| 🟡 O limite de duração que separa nota curta de áudio longo pode ser fixado em configuração e ajustado por medição | Seção 10, mesma dúvida | Um limite mal calibrado faz notas médias receberem tratamento de reunião, gerando classificação em duas passagens desnecessária e custo dobrado de API |
| 🟡 Uma reunião representada como registro único, com lista de próximos passos, é suficiente para o usuário agir | Seção 5, RF-21 e RF-22 | Se o usuário precisar tratar cada tema da reunião separadamente, o registro único vira um bloco que ele não consegue marcar como executado parcialmente, e a métrica de ações por mês fica distorcida |
| 🟡 O volume declarado de cerca de dez capturas curtas por semana, mais reuniões eventuais, cabe na máquina do usuário | Seção 9, esclarecimentos | Transcrição mais lenta que o tempo entre capturas forma fila crescente. Sintoma a observar: confirmação chegando minutos depois da fala em dia de uso normal |
| 🟡 **A premissa central do projeto entra em construção sem validação prévia.** Assume-se que a classificação automática será confiável o bastante para dispensar conferência item a item, sem que isso tenha sido medido | Decisão do usuário de 2026-08-11, ao remover o teste Mago de Oz do plano | Se falsa, três componentes já terão sido construídos quando o problema aparecer, e o produto entregará uma fila de revisão em vez de trabalho poupado. O aprendizado técnico permanece entregue de qualquer forma, o que é justamente a razão declarada para aceitar este risco. Sintoma a observar no passo 3: vontade de conferir cada classificação em vez de confiar nela |
| 🟡 Os cinco tipos de registro configurados são adequados ao material real do usuário | Seção 9, esclarecimentos | Fixados por escolha e não por observação, já que a calibração viria do teste removido. Sintoma a observar: um tipo que nunca é atribuído, ou registros recorrentes que não cabem em nenhum dos cinco |

## 5. Delta arquitetural

🟡 Todos os componentes são novos. Em greenfield não há `architecture.md`, então a coluna de origem aponta para a spec que define cada componente.

| Componente | Arquivo de origem no legado | Tipo de mudança | Resumo |
|------------|------------------------------|-----------------|--------|
| `captura-telegram` | `_reversa_sdd/sdd/captura-telegram.md` | componente-novo | Laço de long polling, autorização por identificador único, download de áudio, avisos e confirmações no chat |
| `transcricao-whisper` | `_reversa_sdd/sdd/transcricao-whisper.md` | componente-novo | Transcrição local, com tempo limite dependente da duração do áudio |
| `classificacao-ia` | `_reversa_sdd/sdd/classificacao-ia.md` | componente-novo | Adaptador de provedor atrás de interface única, com passagem simples para áudio curto e dupla para áudio longo |
| `acervo-markdown` | `_reversa_sdd/sdd/acervo-markdown.md` | componente-novo | Escrita atômica de registros, pastas derivadas da data, índice auxiliar reconstruível |
| `digest-semanal` | `_reversa_sdd/sdd/digest-semanal.md` | componente-novo | Agendador interno, montagem do e-mail, links de confirmação, envio por servidor de saída |
| `painel-acompanhamento` | `_reversa_sdd/sdd/painel-acompanhamento.md` | componente-novo | Servidor HTTP em loopback, listagem, contagens do período e páginas de confirmação de marcação |
| `fila-processamento` | 🔴 sem spec correspondente | componente-novo | **Componente não previsto nas specs.** Serialização e persistência do trabalho pendente, necessário para sustentar exatamente-uma-vez e para proteger a máquina. Ver risco R-06 |
| `configuracao` | `_reversa_sdd/sdd/*.md#9.1` | componente-novo | Carga e validação dos trinta e nove parâmetros de `.env`, com falha explícita nomeando o parâmetro ausente |

## 6. Delta no modelo de dados

- 🟡 Resumo das mudanças: quatro entidades novas, todas persistidas em arquivo e nenhuma em banco. `Registro` é a única com valor duradouro, gravada como markdown legível. `EstadoPolling`, `ItemFila` e `EnvioDigest` são estado operacional, descartáveis sem perda do acervo. O campo `origem` do `Registro` ganha o valor `reuniao`, e o campo de próximo passo passa a aceitar lista, ambos decorrentes da inclusão de reunião no escopo.
- Detalhe completo em: `_reversa_forward/001-captura-voz-ao-arquivo/data-delta.md`

## 7. Delta de contratos externos

| Contrato | Tipo | Arquivo de detalhe |
|----------|------|--------------------|
| API do Telegram, recepção de mensagens e envio de respostas | HTTP | `_reversa_forward/001-captura-voz-ao-arquivo/interfaces/telegram-bot-api.md` |
| API do provedor de modelo de linguagem, classificação | HTTP | `_reversa_forward/001-captura-voz-ao-arquivo/interfaces/llm-classificacao.md` |
| Servidor de e-mail de saída, envio do digest | SMTP | `_reversa_forward/001-captura-voz-ao-arquivo/interfaces/smtp-digest.md` |
| Painel local, listagem e páginas de confirmação | HTTP | `_reversa_forward/001-captura-voz-ao-arquivo/interfaces/painel-http.md` |

🟡 O contrato do painel é local, porém tratado como externo por um motivo específico: **seus endereços ficam gravados dentro de e-mails já enviados**. Alterá-los quebra digests antigos que ainda estão na caixa do usuário, o que confere a ele estabilidade de contrato público.

## 8. Plano de migração

🟡 Não há migração de dados, porque não há dados anteriores. O acervo antigo em bloco de notas e cadernos de papel é não-objetivo declarado. O que existe é uma **ordem de construção**, ditada por dependência técnica.

> **Decisão do usuário, 2026-08-11:** o teste Mago de Oz foi **removido do plano**. Ele era o passo 1 desta ordem e funcionava como portão bloqueante da construção. A justificativa é que o projeto tem também finalidade acadêmica e de aprendizado, de modo que o retorno do esforço não depende de a classificação automática se mostrar confiável. A construção começa com a premissa central **não validada**, e essa é uma escolha consciente, registrada em Premissas e no risco R-01.

1. 🟡 Construir `configuracao` e `acervo-markdown`, que não dependem de nada e sustentam todo o resto.
2. 🟡 Construir `transcricao-whisper` e medir o tempo real na máquina do usuário, fixando o modelo por medição e não por escolha antecipada.
3. 🟡 Construir `classificacao-ia` com um adaptador concreto. **Assim que este passo estiver de pé, medir a qualidade da classificação** sobre pelo menos vinte transcrições reais, antes de seguir. É aqui que a premissa central passa a ser verificável, agora com custo de construção já incorrido.
4. 🟡 Construir `fila-processamento` e `captura-telegram`, fechando a esteira de ponta a ponta. Neste ponto o sistema já entrega valor.
5. 🟡 Construir `painel-acompanhamento`, incluindo as páginas de confirmação, que precisam existir antes do primeiro digest.
6. 🟡 Construir `digest-semanal` por último, porque digest sobre acervo vazio não valida nada.

🟡 O passo 3 concentra o ponto de decisão que antes ficava no passo 1. A diferença prática é o custo: reprovar ali significa ter construído três componentes, e não nenhum.

## 9. Riscos e mitigações

| Risco | Impacto | Probabilidade | Mitigação |
|-------|---------|---------------|-----------|
| 🟡 R-01: a classificação automática não é confiável o bastante para dispensar conferência | alto | médio | **Mitigação enfraquecida por decisão do usuário.** A validação prévia sem código foi removida do plano. A verificação passa a ocorrer no passo 3 da ordem de construção, medindo a qualidade sobre pelo menos vinte transcrições reais assim que a `classificacao-ia` estiver de pé. Reprovando, a fronteira única de provedor permite ajustar prompt ou trocar de provedor sem reescrita, e só depois disso a alternativa é reduzir o escopo ao resurfacing simples. O custo de descobrir agora é de três componentes já construídos, e não de zero |
| 🟡 R-02: transcrição de reunião demora mais do que o tolerável na máquina do usuário | alto | alto | Aviso de processamento estendido, tempo limite próprio para áudio longo e medição do modelo no passo 3, antes de qualquer compromisso de latência |
| 🟡 R-03: registro único de reunião não permite marcar temas individualmente como executados | médio | alto | Lista de próximos passos no registro em vez de um só. Divisão em registros por tema fica registrada como evolução natural, fora desta entrega |
| 🟡 R-04: processo único derruba tudo quando qualquer parte falha | médio | médio | Isolamento de falha por etapa, com o áudio e o texto bruto preservados em disco a cada transição, permitindo reprocessar sem recapturar |
| 🟡 R-05: divergência entre o endereço do painel e os links gravados em e-mails antigos | médio | médio | Alerta na inicialização quando o endereço efetivo diverge do configurado, e recusa de escolher outra porta silenciosamente quando a configurada estiver ocupada |
| 🟡 R-06: `fila-processamento` não tem spec correspondente em `_reversa_sdd/sdd/` | médio | alto | Registrado aqui como componente novo do plano. Recomenda-se rodar `/reversa-sync` após a entrega para convergir esse componente na extração, sob pena de a documentação nascer desatualizada |
| 🟡 R-07: custo de API cresce com reuniões, que consomem muito mais entrada que notas curtas | médio | médio | Custo estimado registrado por chamada, exibido no painel, e classificação em duas passagens apenas acima do limite de duração configurado |
| 🟡 R-08: consentimento obtido em reunião cobre a gravação, mas não o envio a serviço externo | médio | médio | Observação registrada na RN-08 do requirements. Mitigação é de processo, não de software: o usuário precisa mencionar o processamento automático ao pedir autorização |

## 10. Critério de pronto

- [ ] Todas as ações do `actions.md` marcadas `[X]`
- [ ] `cross-check.md` (se executado) sem CRITICAL nem HIGH
- [ ] `regression-watch.md` gerado
- [ ] Re-extração reversa executada e sem regressão vermelha (recomendado, não obrigatório)
- [ ] 🟡 Qualidade da classificação medida sobre pelo menos vinte transcrições reais, no passo 3 da ordem de construção, com o resultado registrado mesmo que seja ruim
- [ ] 🟡 Uma captura real feita dirigindo, do celular ao arquivo em disco, com confirmação recebida no chat
- [ ] 🟡 Uma reunião real gravada, transcrita e classificada dentro do tempo limite de áudio longo
- [ ] 🟡 Um digest recebido por e-mail, com um registro marcado como executado por meio do link
- [ ] 🟡 Painel exibindo contagens coerentes com a contagem manual dos arquivos do acervo
- [ ] 🟡 Interrupção deliberada do processo durante uma gravação, sem gerar arquivo parcial nem registro duplicado

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-08-11 | Versão inicial gerada por `/reversa-plan` | reversa |
| 2026-08-11 | Teste Mago de Oz removido do plano por decisão do usuário, dado o caráter acadêmico do projeto. Ordem de construção renumerada, mitigação do R-01 reescrita para verificação pós-construção, duas premissas novas registradas e critério de pronto ajustado | reversa |
