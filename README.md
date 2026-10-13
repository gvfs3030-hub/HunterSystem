# HUNTER SYSTEM — Crônicas da Forja

Um aplicativo desktop para Windows que transforma estudo em uma campanha de fantasia sombria: missões, XP, níveis, atributos, ouro, equipamentos, eventos de foco, questões rápidas, chefes e narrativa original.

## O que está incluído

- **Três slots separados, com histórias distintas:** Python (A Cidade Sem Aurora), Caixa — Técnico Bancário Novo (O Arquivo dos Ecos) e uma Jornada Livre personalizável.
- **Save local automático:** os dados ficam no computador. Não há cadastro, telemetria ou sincronização em nuvem.
- **Progressão RPG:** XP, níveis, pontos de atributo, moeda, armas, armaduras, talismãs, elixires e combate por turnos.
- **Campanha linear, tópico por tópico:** 141 etapas temáticas de Python em 21 capítulos, 82 etapas de Técnico Bancário Novo (não TI) em 10 capítulos e uma jornada livre com cinco passos por tema.
- **Ritual obrigatório de estudo:** cada página tem introdução narrativa, roteiro de estudo, atividade prática, notas salvas e prova de domínio (4 questões; exige 3 acertos). A prova só libera depois de confirmar a atividade.
- **Recapitulação no dia seguinte:** cada tópico concluído ganha revisão D+1; ao concluir, a sequência avança para mais 7 dias e depois mais 30 dias após cada revisão concluída. Revisões vencidas sobem para o plano de hoje; falhar não apaga progresso e vira evidência para reforço.
- **Chefes em sequência:** antes de cada combate existe uma prova cumulativa; quando um guardião fica disponível, a próxima região permanece selada até ele cair.
- **Identidade visual nova:** ícone de portal arcano, grimório e relíquia dourada; incluído no executável Windows.
- **Backup completo em ZIP:** reúne os três slots, anotações, revisões, histórico, configurações e inventários. ZIP e JSON podem ser importados.
- **Reinício seguro de slot:** apaga apenas o perfil ativo depois de confirmação, criando automaticamente um backup local de segurança.
- **Eventos diários e foco de 25 minutos**, sequência, XP, ouro, equipamento e histórico.
- **Configuração livre:** nome, personagem, tema, missões, chefes e questões próprias.

- **Treinador adaptativo (Estratégia):** diagnósticos por disciplina, registro de tentativas boas e ruins, prioridade por peso do edital + desempenho observado + recência + assuntos ainda não calibrados, e reforços que não quebram a sequência linear da campanha.
- **Barreira contra eliminação na Caixa:** acompanha Conhecimentos Básicos e Específicos separadamente, ponderando cada disciplina pelo número de questões do edital anexado. A tela diferencia projeção parcial de uma estimativa com todas as disciplinas medidas e sinaliza margem baixa em relação ao corte de 50%.
- **Simulados diferentes para finalidades diferentes:** treino adaptativo de 20 questões para reforçar pontos fracos e simulado de 60 questões com a distribuição objetiva do edital TBN comum 2024 (25 básicas + 35 específicas). As questões são autorais do app, não oficiais da Cesgranrio. O resultado é registrado por matéria e bloco e alimenta as prioridades.
- **Redação com honestidade de medição:** oficina semanal, temas alternados e rubrica de 5 critérios autoavaliados. O app não finge corrigir o texto automaticamente nem converte essa autoavaliação em nota oficial.
- **Ritmo até a data-alvo:** data opcional, minutos disponíveis, mínimo de tópicos e meta pessoal de acerto. O app compara a carga restante com os dias e sinaliza quando precisa de ajuste; não prevê nem garante nota de aprovação.

## Conteúdo usado para semear as trilhas

### Python
A trilha é inspirada nos tópicos do curso [Python 3 do básico ao avançado — com projetos reais](https://www.udemy.com/course/python-3-do-zero-ao-avancado/): lógica, sintaxe, estruturas, funções, módulos, POO, bancos de dados, testes, Regex, PySide6, Django, automação, padrões de projeto e publicação. A jornada do app tem 141 unidades de estudo temáticas, não uma transcrição literal de cada um dos vídeos da Udemy; use-a como roteiro para localizar a aula correspondente na sua área do aluno. Dentro de cada lição existe um botão para abrir a página do curso.

### Caixa
A trilha baseia-se no edital anexado pelo usuário: **Edital nº 01/2024/NM**, com alterações publicadas em 27/02/2024. Para Técnico Bancário Novo (não TI), o edital indica 60 questões objetivas — 25 de conhecimentos básicos e 35 de específicos — além de redação. A trilha usa as disciplinas e tópicos do Anexo IV, mas reduz os tópicos a temas de planejamento e revisão.

**Atenção:** esse é o edital de 2024 que foi anexado à conversa; o aplicativo não afirma que ele seja um edital vigente ou futuro. Confira sempre o edital mais recente quando houver nova seleção. Os quizzes são exercícios introdutórios criados para o app, não questões oficiais da Cesgranrio.

## Calendário adaptativo e ambientação

- Abra **Calendário** no menu lateral para navegar por mês, escolher uma data e ver tópicos planejados, conclusões registradas e recapitulações.
- Meta mínima inicial: **Python: 1 tópico/dia**, **Caixa: 2 tópicos/dia** e **Jornada Livre: 1 tópico/dia**. Em **Ritmo da campanha**, ajuste o mínimo (1 a 5) e a data de início.
- O cronograma é uma previsão móvel que preserva a ordem linear: ao terminar a meta, as próximas páginas aparecem como bônus adaptativo e a previsão se antecipa. Se um dia ficar pendente, no dia seguinte o planejamento começa pelo primeiro tópico ainda não concluído; nenhum tópico é marcado como feito automaticamente.
- Para a Caixa, o plano recomenda mais tempo para **Conhecimentos Bancários (15 questões)** e **Atendimento Bancário (10)**, tempo-base para os demais eixos objetivos (5 questões cada) e uma sessão maior de **Redação**, por ser eliminatória no edital de 2024 enviado. A ordem da história continua linear; a prioridade aparece no tempo sugerido de cada tópico.
- O Santuário agora traz uma cena panorâmica; diálogos e lições exibem retratos da Íria e do protagonista. O ícone do aplicativo e o ícone incorporado ao `.exe` também foram trocados.
- O histórico diário passa a ser registrado nesta versão. O progresso anterior continua salvo, mas não é atribuído retroativamente a datas específicas quando não existe registro confiável.
- **Como começar a estratégia da Caixa:** primeiro faça o diagnóstico das 9 matérias objetivas; depois use o simulado adaptativo de 20 questões para treinar áreas fracas e o simulado de 60 questões para verificar a distribuição completa. Repita o simulado completo periodicamente e observe separadamente o percentual de Básicos e Específicos. Faça redação pelo menos uma vez por semana e use a rubrica como autoavaliação, não como correção oficial.
- **Como o plano decide:** matérias de maior peso começam com mais prioridade, mas um resultado baixo, uma revisão atrasada ou evidência antiga elevam a necessidade de reforço. Quando não existe evidência, o app pede diagnóstico em vez de inventar percentual. A projeção de bloco permanece marcada como parcial até haver dados de todas as matérias daquele bloco.
- **Princípio de carga sustentável:** o reforço extra cabe apenas no tempo que sobra depois do mínimo linear e das revisões; se o orçamento diário já foi consumido, o app alerta para não empilhar tarefas nem sacrificar sono.

## Como gerar o `.exe` pelo GitHub usando apenas o navegador

1. Entre no GitHub e crie um repositório novo, por exemplo `hunter-system`.
2. Extraia o ZIP e envie o **conteúdo da pasta inteira** pelo navegador usando **Add file → Upload files**. A raiz deve conter `main.py`, `game_data.py`, `campaign_data.py`, `schedule_system.py`, `adaptive_planner.py`, `requirements.txt`, a pasta `assets` e a pasta `tests` completa.
3. Garanta também que `.github/workflows/build-windows.yml` foi enviado. Se o GitHub não aceitar pastas ocultas, use **Add file → Create new file**, digite `.github/workflows/build-windows.yml` no campo do nome e cole o conteúdo do workflow que acompanha este projeto.
4. Faça o commit na branch `main`.
5. Abra a aba **Actions** do repositório. Se necessário, habilite GitHub Actions.
6. Selecione **Build Hunter System para Windows** e clique em **Run workflow**. Um push/commit dos arquivos também inicia o workflow automaticamente.
7. Ao terminar, abra a execução concluída, role até **Artifacts** e baixe **HunterSystem-Windows**. O ZIP baixado pelo GitHub contém `HunterSystem.exe`.
8. Extraia o ZIP e execute `HunterSystem.exe` no Windows. Na primeira execução, o Windows SmartScreen pode mostrar um aviso para aplicativos não assinados; só execute builds que você mesmo gerou a partir deste repositório.

## Onde fica o progresso

- Windows: `%APPDATA%\HunterSystem\save.json`
- Outros sistemas (para desenvolvimento): `~/.hunter_system/save.json`

O arquivo de save é local. Use **Configuração → Backup completo ZIP** para arquivar os três slots; em **Importar ZIP / JSON** você pode restaurar. Ao reiniciar o slot atual, o app cria uma cópia JSON de segurança na pasta `backups` antes de apagar o progresso daquele slot.

## Executar para desenvolvimento

Requer Python 3 com Tkinter disponível (a instalação padrão de Python para Windows normalmente oferece essa opção).

```bash
python main.py
```

Não é necessário instalar bibliotecas para executar o app. O GitHub Actions instala PyInstaller só durante a etapa de empacotamento.

## Personalizar missões, chefes e questões

Em **Configuração**:

- **Temas:** um tema por linha. Ao mudar os temas e deixar missões personalizadas vazias, o app monta cinco páginas guiadas por tema.
- **Missões personalizadas:** `TEMA | TÍTULO | DESCRIÇÃO | XP | OURO` — uma página por linha, com prova e revisão.
- **Chefes:** um nome por linha. O último chefe exige a conclusão de todas as missões.
- **Questões:** `TEMA | PERGUNTA | OPÇÃO A | OPÇÃO B | OPÇÃO C | OPÇÃO D | GABARITO A/B/C/D | EXPLICAÇÃO` — uma questão por linha.

O save é independente por slot. Você pode experimentar no slot personalizado sem afetar Python ou Caixa.
