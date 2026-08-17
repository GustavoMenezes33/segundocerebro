# Data Delta: 001-captura-voz-ao-arquivo

> Diff conceitual sobre o modelo extraído em `_reversa_sdd/`
> Data: `2026-08-11`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA

🟡 **Baseline:** projeto greenfield, sem modelo anterior. O diff é contra as entidades definidas nas specs de `_reversa_sdd/sdd/`, que fazem o papel do modelo extraído. Tudo aqui é adição; não há campo removido nem migração de dados existentes.

## 1. Entidades

| Entidade | Situação | Persistência | Sobrevive à perda do software? |
|---|---|---|---|
| 🟡 `Registro` | nova | Um arquivo markdown por registro | **Sim.** É o único ativo com valor duradouro |
| 🟡 `EstadoPolling` | nova | Arquivo JSON único | Não, e não precisa. Estado operacional |
| 🟡 `ItemFila` | nova | Arquivo JSON, um por item pendente | Não. Estado operacional |
| 🟡 `EnvioDigest` | nova | Registro em log estruturado | Não. Histórico operacional |
| 🟡 `IndiceAcervo` | nova | Arquivo JSON único, derivado | Não, e é reconstruível integralmente a partir dos arquivos |

## 2. `Registro`, a entidade central

```
🟡 Registro {
  id: texto                          // único, estável, independente de nome e caminho
  capturado_em: datahora
  origem: enum(voz, texto, reuniao)  // ⚠️ "reuniao" é valor NOVO nesta feature
  assunto: texto | vazio
  tipo: enum(ideia, insight, tarefa, referencia, duvida) | vazio
  proximos_passos: lista de texto    // ⚠️ era texto único nas specs, virou LISTA
  estado: enum(pendente, executado, descartado)
  estado_alterado_em: datahora | nulo
  classificado: booleano
  motivo_nao_classificado: texto | nulo
  audio_path: texto | nulo
  duracao_segundos: decimal | nulo
  texto_bruto: texto                 // imutável, jamais sobrescrito
  contem_terceiros: booleano         // ⚠️ campo NOVO, verdadeiro para origem = reuniao
}
```

### 2.1 Campos alterados em relação às specs

| Campo | Nas specs | Nesta feature | Motivo |
|---|---|---|---|
| 🟡 `origem` | `enum(voz, texto)` | `enum(voz, texto, reuniao)` | Reunião entrou no escopo na sessão de esclarecimentos. Sustenta a RN-09, que exige distinguir registros com fala de terceiros |
| 🟡 `proximo_passo` → `proximos_passos` | Texto único | Lista de texto | Decisão D-03. Uma reunião contém muitos assuntos; um único próximo passo produziria registro inútil. Nota de voz continua gerando lista de um elemento, o que mantém o modelo uniforme |
| 🟡 `contem_terceiros` | Não existia | Campo novo, booleano | Sustenta a RN-09. Permite ao usuário filtrar ou tratar de forma distinta o material que contém fala de outras pessoas |
| 🟡 `duracao_segundos` | Só em `Transcricao` | Promovido ao `Registro` | É o campo que determina a política de processamento aplicada, e precisa ficar visível no registro final para auditoria da decisão tomada |

🟡 **Consequência de compatibilidade:** a mudança de `proximo_passo` para `proximos_passos` afeta o digest e o painel, que exibem esse campo. Como não há dados anteriores, não há migração, mas as specs `digest-semanal` e `painel-acompanhamento` referenciam o campo no singular e ficam **defasadas** a partir desta feature. Convergir via `/reversa-sync` após a entrega.

## 3. Entidades de estado operacional

```
🟡 EstadoPolling {
  ultimo_update_id: inteiro     // deslocamento de leitura, garante exatamente-uma-vez
  atualizado_em: datahora
}

🟡 ItemFila {                    // ⚠️ entidade sem spec correspondente, ver risco R-06
  id: texto
  telegram_message_id: inteiro
  telegram_chat_id: inteiro
  tipo_origem: enum(voz, texto, reuniao)
  audio_path: texto | nulo
  duracao_segundos: decimal | nulo
  etapa: enum(baixado, transcrito, classificado, arquivado)
  tentativas: inteiro
  ultimo_erro: texto | nulo
  enfileirado_em: datahora
}

🟡 EnvioDigest {
  id: texto
  enviado_em: datahora
  registros_incluidos: lista de texto
  quantidade: inteiro
  status: enum(enviado, falhou, vazio)
  erro: texto | nulo
}
```

🟡 O campo `etapa` do `ItemFila` é o que permite retomar do ponto correto após reinício, sem repetir a transcrição de um áudio já transcrito. É ele que torna o requisito de exatamente-uma-vez implementável sem depender de transação.

## 4. Estrutura em disco

```
🟡
<ACERVO_PASTA>/                    # padrão ./dados/acervo
  2026-08/                         # derivada de capturado_em, granularidade configurável
    20260811-143052-newsletter-por-nicho.md
    20260811-181233-reuniao-fornecedor.md
  2026-09/
    ...

<CAPTURA_PASTA_AUDIO>/             # padrão ./dados/audios
  20260811-143052.ogg

./dados/estado_polling.json
./dados/fila/<id>.json
./dados/indice.json
```

🟡 A pasta por período é **derivada da data de captura**, sem nenhuma decisão do usuário. É a resposta ao achado do enquadramento: pasta é atrito quando exige decisão humana no momento errado, e deixa de custar qualquer coisa quando derivada de um dado que o sistema já tem.

## 5. Migrações necessárias

🟡 **Nenhuma.** Não há dados preexistentes. A migração do acervo antigo em bloco de notas e cadernos de papel é não-objetivo declarado no PRD.

🟡 Duas mudanças futuras já são previsíveis e merecem registro, porque afetam decisões de hoje:

1. 🟡 **Divisão de reunião em vários registros.** Se a evolução natural registrada no risco R-03 for adotada, será preciso migrar registros de reunião já existentes de um para N. A preservação do `texto_bruto` imutável, decisão D-10, torna essa migração possível sem reprocessar áudio.
2. 🟡 **Reclassificação em massa após melhoria do prompt.** Também sustentada pelo `texto_bruto` imutável. Sem ele, exigiria reouvir ou retranscrever todo o acervo.

## 6. Índices e desempenho

🟡 `IndiceAcervo` é derivado e descartável, mantido em arquivo JSON único. Contém, por registro, o identificador, o caminho, a data de captura, o assunto, o tipo, o estado e a origem. Não contém o texto bruto, que permanece exclusivamente nos arquivos markdown.

🟡 Para o volume declarado, cerca de dez capturas por semana, o acervo leva mais de um ano e meio para atingir mil registros. Nesse horizonte, ler todos os arquivos a cada carga do painel seria viável. O índice existe para que o painel continue respondendo em menos de três segundos quando o acervo crescer, e não porque seja necessário no primeiro mês.

---
Gerado por `/reversa-plan` em 2026-08-11
