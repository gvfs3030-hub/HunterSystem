# HUNTER SYSTEM — Crônicas da Forja

Um aplicativo desktop para Windows que transforma estudo em uma campanha de fantasia sombria: missões, XP, níveis, atributos, ouro, equipamentos, eventos de foco, questões rápidas, chefes e narrativa original.

## O que está incluído

- **Três slots separados, com histórias distintas:** Python (A Cidade Sem Aurora), Caixa — Técnico Bancário Novo (O Arquivo dos Ecos) e uma Jornada Livre personalizável.
- **Save local automático:** os dados ficam no computador. Não há cadastro, telemetria ou sincronização em nuvem.
- **Progressão RPG:** XP, níveis, pontos de atributo, moeda, armas, armaduras, talismãs, elixires e combate por turnos.
- **Campanha linear, tópico por tópico:** 141 etapas temáticas de Python em 21 capítulos, 82 etapas de Técnico Bancário Novo (não TI) em 10 capítulos e uma jornada livre com cinco passos por tema.
- **Ritual obrigatório de estudo:** cada página tem introdução narrativa, roteiro de estudo, atividade prática, notas salvas e prova de domínio (4 questões; exige 3 acertos). A prova só libera depois de confirmar a atividade.
- **Recapitulação no dia seguinte:** cada tópico concluído ganha uma revisão datada no dia seguinte, com teste de recuperação ativa e recompensa única. O aplicativo avisa quando há revisão vencida.
- **Chefes em sequência:** antes de cada combate existe uma prova cumulativa; quando um guardião fica disponível, a próxima região permanece selada até ele cair.
- **Identidade visual nova:** ícone de portal arcano, grimório e relíquia dourada; incluído no executável Windows.
- **Backup completo em ZIP:** reúne os três slots, anotações, revisões, histórico, configurações e inventários. ZIP e JSON podem ser importados.
- **Reinício seguro de slot:** apaga apenas o perfil ativo depois de confirmação, criando automaticamente um backup local de segurança.
- **Eventos diários e foco de 25 minutos**, sequência, XP, ouro, equipamento e histórico.
- **Configuração livre:** nome, personagem, tema, missões, chefes e questões próprias.

## Conteúdo usado para semear as trilhas

### Python
A trilha é inspirada nos tópicos do curso [Python 3 do básico ao avançado — com projetos reais](https://www.udemy.com/course/python-3-do-zero-ao-avancado/): lógica, sintaxe, estruturas, funções, módulos, POO, bancos de dados, testes, Regex, PySide6, Django, automação, padrões de projeto e publicação. A jornada do app tem 141 unidades de estudo temáticas, não uma transcrição literal de cada um dos vídeos da Udemy; use-a como roteiro para localizar a aula correspondente na sua área do aluno. Dentro de cada lição existe um botão para abrir a página do curso.

### Caixa
A trilha baseia-se no edital anexado pelo usuário: **Edital nº 01/2024/NM**, com alterações publicadas em 27/02/2024. Para Técnico Bancário Novo (não TI), o edital indica 60 questões objetivas — 25 de conhecimentos básicos e 35 de específicos — além de redação. A trilha usa as disciplinas e tópicos do Anexo IV, mas reduz os tópicos a temas de planejamento e revisão.

**Atenção:** esse é o edital de 2024 que foi anexado à conversa; o aplicativo não afirma que ele seja um edital vigente ou futuro. Confira sempre o edital mais recente quando houver nova seleção. Os quizzes são exercícios introdutórios criados para o app, não questões oficiais da Cesgranrio.

## Como gerar o `.exe` pelo GitHub usando apenas o navegador

1. Entre no GitHub e crie um repositório novo, por exemplo `hunter-system`.
2. Extraia o ZIP e envie o **conteúdo da pasta inteira** pelo navegador usando **Add file → Upload files**. A raiz deve conter `main.py`, `game_data.py`, `campaign_data.py`, `requirements.txt`, a pasta `assets` e `tests/test_campaign.py`.
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
