# Investigation: 001-captura-voz-ao-arquivo

> Pesquisa de fundo e alternativas avaliadas
> Data: `2026-08-11`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA

🟡 Este documento registra o raciocínio por trás das decisões do `roadmap.md`, incluindo o que foi descartado e por quê. Serve para que, daqui a seis meses, a pergunta "por que não fizemos do jeito óbvio?" tenha resposta escrita.

## 1. Recepção de mensagens: long polling contra webhook

🟡 **Escolhido: long polling.**

O modo natural de integrar com uma API de mensageria é registrar um webhook: o serviço chama o seu endereço quando há mensagem nova. É mais eficiente e é o que a maior parte da documentação sugere.

🟡 Aqui ele é inviável por uma razão de topologia, não de eficiência. Webhook exige que a máquina do usuário seja **alcançável a partir da internet**: endereço público, porta encaminhada no roteador doméstico e certificado. O requirements proíbe expor a máquina, e essa proibição não é preferência, é a contrapartida de o acervo ser local.

🟡 Long polling inverte a direção da conexão. A máquina local abre a conexão para fora, como um navegador faz, e mantém a requisição aberta esperando novidade. Nenhuma porta aberta, nenhum endereço fixo, nenhum certificado. O custo é uma conexão permanentemente aberta e latência ligeiramente maior, ambos irrelevantes para o volume de dez capturas por semana.

🟡 Alternativas descartadas: túnel reverso por serviço de terceiro, que reintroduz dependência externa e uma superfície de exposição; endereço dinâmico com porta encaminhada, frágil a troca de roteador e à política do provedor de internet.

## 2. Transcrição: local contra API

🟡 **Escolhido: local, decidido pelo usuário.**

APIs de transcrição são mais rápidas, não consomem a máquina e dispensam gerenciar modelo. Foram descartadas por dois motivos declarados: custo por minuto, que cresceria de forma desproporcional com reuniões, e envio da fala bruta a um terceiro.

🟡 O segundo motivo perdeu parte da força quando o usuário decidiu classificar por API externa, já que a transcrição transita de qualquer forma. O que permanece válido é o primeiro: uma reunião de quarenta e cinco minutos por semana somaria cerca de três horas de áudio por mês, faixa em que transcrição paga deixa de ser desprezível, enquanto a execução local continua custando zero.

🟡 **Ponto não resolvido e importante:** o tempo de transcrição local de reuniões longas é a maior incógnita técnica desta feature. O plano trata isso medindo antes de comprometer, no passo 3 da ordem de construção, em vez de estimar.

## 3. Áudio longo: mesma esteira ou esteira separada

🟡 **Escolhido: mesma esteira, com política por duração.**

Duas esteiras separadas parecem mais limpas no papel, porque reunião e nota de voz têm perfis muito diferentes. Na prática, as quatro etapas são idênticas: baixar, transcrever, classificar, arquivar. O que muda são limites numéricos e a forma de classificar.

🟡 Duplicar a esteira duplicaria também o tratamento de erro, o controle de fila e a lógica de exatamente-uma-vez, que são as partes mais delicadas e as menos divertidas de manter em duplicata.

🟡 A premissa está registrada no `roadmap.md` com um **sintoma observável** que indicaria erro: condicionais por duração aparecendo em mais de três pontos do código. Passando disso, a diferença é estrutural e vale separar.

## 4. Classificação de reunião: o problema que não estava nas specs

🟡 Este foi o achado mais consequente do planejamento, e ele não vem de tecnologia, vem de modelagem.

🟡 As specs foram escritas assumindo que **um áudio contém um insight**. Isso é verdade para trinta segundos falados ao volante e é falso para quarenta e cinco minutos de reunião. A spec `classificacao-ia` tem um caso de borda para múltiplos assuntos, o EC-07, que manda escolher o predominante. Aplicado a uma reunião, esse comportamento produziria um registro com assunto "reunião sobre diversos temas" e um único próximo passo, ou seja, um registro sem valor.

🟡 Três saídas foram consideradas:

1. **Um registro com lista de próximos passos.** Escolhida. Preserva a integridade do registro como unidade de captura e admite que uma reunião gera vários encaminhamentos.
2. **N registros, um por tema.** Descartada nesta entrega. Contraria a decisão explícita da spec de não dividir automaticamente, e divisão automática errada gera fragmentos sem contexto, que são piores que um bloco íntegro.
3. **Resumo estruturado em texto livre.** Descartada. Não é acionável nem marcável, e a métrica de sucesso depende de marcar registros como executados.

🟡 A opção 2 permanece como evolução natural, e a preservação do texto bruto imutável é o que a mantém possível sem reprocessar áudio.

🟡 Sobre limite de contexto: a preocupação inicial era que uma transcrição de reunião não coubesse na janela do modelo. Uma fala de quarenta e cinco minutos rende algo em torno de seis a sete mil palavras, o que cabe com folga nos modelos atuais. **O problema real não é o tamanho da entrada, é a qualidade da saída** quando se pede um único assunto para um conteúdo multiassunto. Daí a decisão de duas passagens, D-12, e não de truncamento.

## 5. Confirmação de marcação: por que não um link direto

🟡 **Escolhido: duas etapas, com página de confirmação.**

O caminho óbvio é um link que já marca o registro ao ser aberto. É um clique a menos e todo mundo faz assim.

🟡 O problema é que clientes de e-mail, antivírus e filtros de segurança **pré-carregam endereços** contidos em mensagens, para checar reputação e gerar pré-visualização. Um link que altera estado ao ser carregado seria acionado por essas ferramentas, e o usuário encontraria registros marcados como executados sem nunca os ter tocado.

🟡 O dano aqui não é o registro errado, é a perda de confiança: um acervo que se altera sozinho deixa de ser confiável inteiro, inclusive na parte correta. Como o produto existe para o usuário confiar que o insight está guardado, esse é o pior defeito possível.

🟡 Alternativa descartada: token de uso único no endereço. Resolve o pré-carregamento repetido, mas não o primeiro acesso automático, que é justamente o que dispara o problema.

## 6. Agendamento do digest: interno contra sistema operacional

🟡 **Escolhido: agendador interno, por verificação periódica de relógio.**

Delegar ao agendador do sistema operacional é a solução clássica e evita manter um processo vivo. Foi descartada por duas razões: difere entre plataformas, o que multiplica a documentação de instalação, e é a peça que o usuário provavelmente esqueceria de configurar, fazendo o digest simplesmente nunca chegar sem nenhum erro visível.

🟡 Como o processo já precisa estar vivo para o long polling, hospedar o agendador nele não custa nada. Verificação de relógio a cada minuto é precisão mais que suficiente para um evento semanal.

🟡 Consequência aceita: com a máquina desligada no horário, o envio ocorre na primeira execução seguinte, uma única vez, sem acumular envios atrasados. Isso já estava previsto na spec.

## 7. Persistência: arquivos contra banco

🟡 **Escolhido: arquivos markdown, com índice auxiliar descartável.**

Um banco embarcado seria mais rápido para consultar e mais simples para manter consistência. Foi descartado porque tornaria o acervo ilegível sem o software do projeto, o que contraria o requisito de portabilidade.

🟡 Esse requisito não é estético. O sistema é mantido por uma pessoa só, construído por agentes, e sem consequência externa se parar. A probabilidade de ele ser abandonado em algum momento não é baixa, e o acervo precisa sobreviver a esse cenário. Markdown em pasta sobrevive; banco embarcado sobrevive apenas enquanto alguém souber abri-lo.

🟡 O índice auxiliar recupera o desempenho de consulta sem abrir mão da propriedade, porque pode ser apagado a qualquer momento e reconstruído a partir dos arquivos.

## 8. Padrões aplicáveis

🟡 **Fronteira de adaptador** para o provedor de modelo de linguagem, isolando uma dependência volátil atrás de uma interface estável. É o que torna a escolha de provedor uma decisão adiável sem custo.

🟡 **Deslocamento de leitura persistido**, padrão comum em consumo de fluxo de mensagens, aplicado aqui para garantir exatamente-uma-vez através de reinícios.

🟡 **Escrita atômica por arquivo temporário e renomeação**, garantindo que uma interrupção nunca deixe arquivo parcial. Aplicado a todos os arquivos do acervo e ao índice.

🟡 **Máquina de estados explícita por item de fila**, com o campo `etapa`, permitindo retomar do ponto correto em vez de reprocessar do início.

## 9. O que continua sem resposta

🔴 Tempo real de transcrição de uma reunião de quarenta e cinco minutos na máquina do usuário. Resolvido por medição no passo 3 da ordem de construção, não por estimativa.

🔴 Qual limite de duração separa nota curta de áudio longo. Fica configurável, com valor inicial a calibrar por observação.

🔴 Se o usuário conseguirá agir sobre uma reunião representada como registro único. Só o uso real responde, e o sintoma de erro é ele não conseguir marcar como executado algo parcialmente resolvido.

---
Gerado por `/reversa-plan` em 2026-08-11
