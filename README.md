# HUNTER SYSTEM — A Forja da Constância

Um aplicativo desktop para Windows que transforma estudo em uma campanha de fantasia sombria: missões, XP, níveis, atributos, ouro, equipamentos, eventos de foco, questões rápidas, chefes e narrativa original.

## O que está incluído

- **Três slots separados:** Python (curso Udemy), Caixa — Técnico Bancário Novo (não TI) e uma Jornada Livre personalizável.
- **Save local automático:** os dados ficam no computador. Não há cadastro, telemetria ou sincronização em nuvem.
- **Progressão RPG:** XP, níveis, pontos de atributo, moeda, armas, armaduras, talismãs, elixires e combate por turnos.
- **Missões por etapa:** teoria, prática/questões e revisão para cada fase da trilha.
- **Eventos diários e foco de 25 minutos**, sequência de estudo, histórico e exportação/importação de save JSON.
- **Códice de questões:** perguntas rápidas para os perfis padrão e suporte a perguntas próprias no slot personalizado.
- **História linear original:** prólogo, cenas pós-chefe e desfecho após o guardião final.
- **Configuração livre:** altere o nome da campanha/personagem, sinopse, temas, missões (com XP e ouro), nomes de chefes e questões.

## Conteúdo usado para semear as trilhas

### Python
A trilha é inspirada nas áreas divulgadas para o curso [Python 3 do básico ao avançado — com projetos reais](https://www.udemy.com/course/python-3-do-zero-ao-avancado/?couponCode=MT261012G1): lógica, sintaxe, estruturas, funções, módulos, POO, bancos de dados, testes, Regex, PySide6, Django, automação, padrões de projeto e extras. O curso pode mudar; as missões são editáveis para acompanhar a sua área de aluno.

### Caixa
A trilha baseia-se no edital anexado pelo usuário: **Edital nº 01/2024/NM**, com alterações publicadas em 27/02/2024. Para Técnico Bancário Novo (não TI), o edital indica 60 questões objetivas — 25 de conhecimentos básicos e 35 de específicos — além de redação. A trilha usa as disciplinas e tópicos do Anexo IV, mas reduz os tópicos a temas de planejamento e revisão.

**Atenção:** esse é o edital de 2024 que foi anexado à conversa; o aplicativo não afirma que ele seja um edital vigente ou futuro. Confira sempre o edital mais recente quando houver nova seleção. Os quizzes são exercícios introdutórios criados para o app, não questões oficiais da Cesgranrio.

## Como gerar o `.exe` pelo GitHub usando apenas o navegador

1. Entre no GitHub e crie um repositório novo, por exemplo `hunter-system`.
2. Extraia o ZIP deste projeto no computador **ou** envie os arquivos pelo navegador usando **Add file → Upload files**. A raiz do repositório deve conter `main.py`, `game_data.py`, `README.md` e a pasta `.github/workflows/build-windows.yml`.
3. Faça o commit na branch `main`.
4. Abra a aba **Actions** do repositório. Se necessário, habilite GitHub Actions.
5. Selecione **Build Hunter System para Windows** e clique em **Run workflow**. Um push/commit dos arquivos também inicia o workflow automaticamente.
6. Ao terminar, abra a execução concluída, role até **Artifacts** e baixe **HunterSystem-Windows**. O ZIP baixado pelo GitHub contém `HunterSystem.exe`.
7. Extraia o ZIP e execute `HunterSystem.exe` no Windows. Na primeira execução, o Windows SmartScreen pode mostrar um aviso para aplicativos não assinados; só execute builds que você mesmo gerou a partir deste repositório.

## Onde fica o progresso

- Windows: `%APPDATA%\HunterSystem\save.json`
- Outros sistemas (para desenvolvimento): `~/.hunter_system/save.json`

O arquivo de save é local. Use **Configuração → Exportar save JSON** para criar um backup e **Importar save JSON** para restaurar.

## Executar para desenvolvimento

Requer Python 3 com Tkinter disponível (a instalação padrão de Python para Windows normalmente oferece essa opção).

```bash
python main.py
```

Não é necessário instalar bibliotecas para executar o app. O GitHub Actions instala PyInstaller só durante a etapa de empacotamento.

## Personalizar missões, chefes e questões

Em **Configuração**:

- **Temas:** um tema por linha. Ao mudar os temas e deixar missões personalizadas vazias, o app monta três missões por tema.
- **Missões personalizadas:** `TEMA | TÍTULO | DESCRIÇÃO | XP | OURO` — uma missão por linha.
- **Chefes:** um nome por linha. O último chefe exige a conclusão de todas as missões.
- **Questões:** `TEMA | PERGUNTA | OPÇÃO A | OPÇÃO B | OPÇÃO C | OPÇÃO D | GABARITO A/B/C/D | EXPLICAÇÃO` — uma questão por linha.

O save é independente por slot. Você pode experimentar no slot personalizado sem afetar Python ou Caixa.
