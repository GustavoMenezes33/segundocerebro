# Interface: API do provedor de modelo de linguagem

> Tipo: HTTP, cliente. Direção: saída
> Feature: `001-captura-voz-ao-arquivo`
> Componente: `classificacao-ia`

## 1. Papel no sistema

🟡 Extrai estrutura do texto transcrito: assunto, tipo de registro e próximos passos. É a única etapa probabilística do pipeline e a que carrega a premissa central do projeto.

🟡 **Provedor e modelo não estão fixados.** A escolha é parametrizada em `.env` e foi deliberadamente adiada. Esta interface existe para tornar essa postergação viável sem custo, e é ela que faz "qual provedor?" deixar de ser pergunta bloqueante.

## 2. Fronteira interna

🟡 Toda comunicação com o provedor passa por **uma única fronteira** no código. O restante do sistema chama uma operação de classificação e recebe um resultado estruturado, sem saber qual provedor respondeu.

🟡 Trocar de provedor deve exigir alterar **no máximo um arquivo**. Este é o critério de aceite do RF-04 da spec `classificacao-ia` e o teste é objetivo: substituir a implementação por uma versão simulada e verificar que nada mais precisa mudar.

🟡 Nesta entrega, **um** adaptador concreto é implementado. Parametrizar sem implementar não classifica nada.

## 3. Requisição

```
🟡 Classificar
  prompt:      lido de LLM_PROMPT_ARQUIVO, editável sem tocar em código
  entrada:     texto bruto da transcrição, íntegro
  saída:       formato estruturado com assunto, tipo e lista de próximos passos
  tipos:       conjunto fechado, de LLM_TIPOS_REGISTRO
```

🟡 **Duas modalidades, conforme a duração do áudio de origem** (decisão D-12 do roadmap):

| Modalidade | Quando | Passagens |
|---|---|---|
| 🟡 Simples | Áudio curto, abaixo do limite configurado | Uma passagem sobre a transcrição inteira, retornando um assunto e uma lista de um próximo passo |
| 🟡 Dupla | Áudio longo, reunião | Primeira passagem extrai os temas e encaminhamentos por blocos; segunda consolida em um assunto abrangente e uma lista de próximos passos |

🟡 A modalidade dupla **não** existe por limite de contexto. Uma transcrição de quarenta e cinco minutos cabe com folga nos modelos atuais. Ela existe porque pedir *um* assunto para um conteúdo multiassunto produz saída pobre.

## 4. Resposta esperada

| Campo | Obrigatório | Validação |
|---|---|---|
| 🟡 `assunto` | Sim | Não vazio, curto o bastante para servir de título |
| 🟡 `tipo` | Sim | **Precisa pertencer ao conjunto fechado.** Valor fora da lista invalida a resposta |
| 🟡 `proximos_passos` | Sim | Lista com pelo menos um item; cada item é ação concreta, não intenção vaga |
| 🟡 `multiplos_temas` | Não | Sinaliza que a transcrição continha temas distintos |

🟡 Rejeitar tipo fora do conjunto fechado é o que impede a proliferação de categorias inventadas, que reintroduziria pela porta dos fundos o problema de taxonomia que o projeto evita.

## 5. Erros e tratamento

| Condição | Comportamento |
|---|---|
| 🟡 Serviço indisponível | Até `LLM_TENTATIVAS` tentativas com espera crescente. Esgotando, **arquivar assim mesmo**, marcado como não classificado |
| 🟡 Resposta em formato inválido | Uma nova tentativa. Persistindo, arquivar como não classificado e guardar a resposta recebida para diagnóstico |
| 🟡 Tipo fora do conjunto fechado | Tratado como resposta inválida, mesmo caminho acima |
| 🟡 Cota ou saldo esgotado | Erro **distinto** de indisponibilidade, nomeando cota, para que a causa financeira fique evidente |
| 🟡 Chave inválida | Falha explícita na inicialização, não durante o processamento |
| 🟡 Conteúdo recusado pelo filtro do provedor | Arquivar como não classificado, nomeando a recusa. O registro do usuário nunca é descartado por decisão de terceiro |
| 🟡 Transcrição vazia | **Nenhuma chamada é feita.** Registro marcado como sem conteúdo, custo zero |

🟡 Toda linha desta tabela obedece à mesma regra: **falha de classificação nunca impede o arquivamento**. Perder o insight é inaceitável; perder a estrutura é recuperável, porque o texto bruto permanece íntegro e permite reclassificar depois.

## 6. Idempotência

🟡 A operação **não é idempotente por natureza**: a mesma entrada pode produzir saídas diferentes entre chamadas, por ser probabilística.

🟡 Isso não causa problema porque a classificação ocorre **uma única vez por registro**, no momento do arquivamento, e o resultado é persistido. Reclassificação futura é operação deliberada, jamais automática, e o texto bruto imutável é o que a torna possível.

## 7. Tempos limite

| Modalidade | Limite | Origem |
|---|---|---|
| 🟡 Simples | `LLM_TIMEOUT_S`, padrão 15 s | Precisa caber no limite de 60 s até a confirmação no chat |
| 🟡 Dupla | Limite próprio, maior | O limite de 60 s não se aplica a áudio longo; vale o aviso de processamento estendido |

🟡 Tempo excedido é tratado como falha transitória e entra na política de novas tentativas.

## 8. Custo

🟡 Único componente com custo recorrente do sistema. Cada chamada registra provedor, modelo, tokens de entrada e saída, e custo estimado. O painel exibe o acumulado do período.

🟡 **Reunião custa desproporcionalmente mais**: transcrição longa como entrada, e duas passagens em vez de uma. O usuário não definiu teto de custo, e é por isso que o registro por chamada existe, para que a conta não surpreenda.

## 9. Privacidade

🟡 A transcrição transita para o provedor. Com reunião no escopo, isso inclui **fala de terceiros**.

🟡 Ao escolher o provedor, verificar a política de uso de conteúdo para treinamento. É verificação de escolha, não de implementação, e precisa acontecer antes de a decisão ser tomada.
