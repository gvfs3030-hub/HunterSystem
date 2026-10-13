"""Dados iniciais do Hunter System. Tudo pode ser adaptado no slot personalizado."""
from copy import deepcopy

PYTHON_PHASES = [
    ("Portal de Entrada", "Boas-vindas, método do curso e mapa da jornada"),
    ("Forja do Ambiente", "Python, VS Code, terminal e ambiente de desenvolvimento"),
    ("Lógica de Programação", "Algoritmos, pensamento lógico e primeiros exercícios"),
    ("Tipos e Variáveis", "str, int, float, bool, conversão e operadores"),
    ("Fluxo de Controle", "Condições, comparações, operadores lógicos e loops"),
    ("Coleções", "Listas, tuplas, sets, dicionários e compreensão de listas"),
    ("Funções e Escopo", "Parâmetros, retorno, escopo, closures e funções de ordem superior"),
    ("Módulos e Pacotes", "Imports, módulos próprios, organização e bibliotecas"),
    ("Arquivos e Dados", "Leitura e escrita de arquivos, JSON e persistência"),
    ("Erros e Exceções", "Tratamento de erros, depuração e código robusto"),
    ("Orientação a Objetos", "Classes, objetos, atributos, métodos, herança e composição"),
    ("Python Avançado", "Iteradores, geradores, decoradores e recursos idiomáticos"),
    ("Expressões Regulares", "Regex, padrões, validação e extração de texto"),
    ("Banco de Dados", "SQLite, SQL, conexão, CRUD e modelagem básica"),
    ("Testes e TDD", "unittest, pytest, testes unitários e ciclo de desenvolvimento"),
    ("Interface Gráfica", "PySide6, Qt e construção de aplicações desktop"),
    ("Web e APIs", "Django, rotas, views, templates e APIs"),
    ("Automação e Web Scraping", "Selenium, requisições e automação de tarefas"),
    ("Projeto Integrador", "Planejamento e construção de uma aplicação real"),
    ("Design Patterns", "Padrões GoF e arquitetura orientada a objetos"),
    ("SQL e Web Extra", "MySQL, HTML5, CSS3 e comandos Unix/WSL opcionais"),
    ("Integração e Qualidade", "Juntar componentes, corrigir bugs, validar requisitos e melhorar a estrutura"),
    ("Publicação e Portfólio", "Revisão, deploy, documentação e apresentação de projetos"),
]

CAIXA_SUBJECTS = [
    ("Língua Portuguesa", "Interpretação, argumentação, coesão, tipologia textual, ortografia, acentuação, crase, sintaxe, pontuação, concordância, regência, semântica, colocação pronominal e redação oficial.", 5),
    ("Língua Inglesa", "Vocabulário fundamental e aspectos gramaticais básicos para compreensão de textos.", 5),
    ("Matemática Financeira", "Valor do dinheiro no tempo, juros simples e compostos, séries uniformes, equivalência de capitais, SAC, Price, descontos, sequências, PA e PG.", 5),
    ("Probabilidade e Estatística", "Variáveis, população e amostra, frequências, gráficos, média, moda, mediana, quartis, percentis, dispersão, probabilidade condicional e distribuição binomial.", 5),
    ("Ética e Compliance", "Prevenção à lavagem de dinheiro, assédio, ética profissional, segurança da informação, princípios do art. 37, sigilo bancário, LGPD, anticorrupção e governança.", 5),
    ("Conhecimentos Bancários", "Estatuto da CAIXA, SFN, mercados, bancos digitais, fintechs, PIX, Open Finance, Drex, política monetária, produtos bancários, câmbio, FGTS, PIS e benefícios.", 15),
    ("Tecnologia da Informação e Comunicação", "Office 365, segurança da informação, arquivos e pastas, redes, internet/intranet, navegadores, e-mail, redes sociais, multimídia, trabalho remoto, IA, cloud, inovação e Open Finance.", 5),
    ("Conhecimentos e Comportamentos Digitais", "Mindset de crescimento, intraempreendedorismo, Design Thinking, métodos ágeis, resolução de problemas, ciência de dados, pensamento computacional, liderança, CX, ODS, OKR e produtividade.", 5),
    ("Atendimento Bancário", "Experiência do cliente, vendas, marketing digital, ética em vendas, escuta empática, canais remotos, negociação, ouvidoria, CDC, inclusão e atendimento prioritário.", 10),
    ("Redação", "Produção de texto dissertativo, organização de ideias, tese, argumentos, coesão, coerência, clareza e revisão textual.", 0),
]

PYTHON_MISSION_SUFFIXES = [
    ("Estudar a teoria", "Assista às aulas do tema e registre os conceitos que realmente entendeu.", 35, 12),
    ("Praticar sem copiar", "Resolva exercícios ou escreva código sem acompanhar a solução; depois revise os erros.", 45, 18),
    ("Revisar e explicar", "Explique o assunto com suas próprias palavras e anote dúvidas para a próxima sessão.", 30, 10),
]

CAIXA_MISSION_SUFFIXES = [
    ("Mapear o conteúdo", "Leia o trecho do edital e transforme os tópicos em um resumo curto.", 30, 10),
    ("Resolver questões", "Pratique questões do tema e registre por que cada alternativa está certa ou errada.", 45, 18),
    ("Revisão ativa", "Faça uma revisão sem consulta e marque os pontos que ainda precisam de reforço.", 35, 12),
]

PYTHON_QUIZ = [
    {"id":"py1","subject":"Python","q":"Qual estrutura armazena pares de chave e valor?","options":["list","tuple","dict","set"],"a":2,"why":"dict mapeia chaves para valores."},
    {"id":"py2","subject":"Python","q":"Qual palavra inicia uma definição de função em Python?","options":["func","def","function","lambda"],"a":1,"why":"Funções nomeadas são definidas com def."},
    {"id":"py3","subject":"Python","q":"Qual é o resultado de len([3, 5, 8])?","options":["2","3","8","16"],"a":1,"why":"A lista contém três elementos."},
    {"id":"py4","subject":"Python","q":"Qual bloco trata uma exceção capturada?","options":["catch","except","rescue","handle"],"a":1,"why":"Python usa try/except para tratar exceções."},
    {"id":"py5","subject":"Python","q":"Em POO, uma instância é…","options":["um pacote","um objeto criado a partir de uma classe","um tipo de loop","um arquivo JSON"],"a":1,"why":"A instância é um objeto concreto de uma classe."},
    {"id":"py6","subject":"Python","q":"Qual método costuma inicializar um objeto?","options":["__start__","__main__","__init__","__newfile__"],"a":2,"why":"__init__ inicializa o estado da instância."},
    {"id":"py7","subject":"Python","q":"Qual biblioteca padrão oferece acesso a banco SQLite?","options":["sqlite3","pandasql","sqlplus","dbpy"],"a":0,"why":"sqlite3 faz parte da biblioteca padrão do Python."},
    {"id":"py8","subject":"Python","q":"Qual expressão cria uma condição alternativa?","options":["otherwise","elseif","elif","when"],"a":2,"why":"elif é usado para condições alternativas."},
    {"id":"py9","subject":"Python","q":"O que um teste unitário verifica principalmente?","options":["uma pequena unidade de comportamento","o computador inteiro","a velocidade da internet","somente a interface"],"a":0,"why":"Testes unitários verificam unidades pequenas e isoladas de comportamento."},
    {"id":"py10","subject":"Python","q":"O que normalmente significa CRUD?","options":["Create, Read, Update, Delete","Copy, Run, Upload, Download","Class, Return, Until, Debug","Create, Route, Use, Deploy"],"a":0,"why":"CRUD resume as operações básicas de persistência."},
]

CAIXA_QUIZ = [
    {"id":"cx1","subject":"Matemática Financeira","q":"Em juros simples, o juro é calculado sobre…","options":["o montante a cada período","o capital inicial","a taxa acumulada exponencialmente","apenas os juros do mês anterior"],"a":1,"why":"Nos juros simples, a base de cálculo permanece o capital inicial."},
    {"id":"cx2","subject":"Matemática Financeira","q":"R$ 1.000 a 2% ao mês por 3 meses, em juros simples, gera juros de…","options":["R$ 20","R$ 40","R$ 60","R$ 120"],"a":2,"why":"J = C × i × t = 1.000 × 0,02 × 3 = R$ 60."},
    {"id":"cx3","subject":"Probabilidade e Estatística","q":"A mediana é…","options":["sempre o maior valor","o valor central dos dados ordenados","a soma dos dados","a diferença entre máximo e mínimo"],"a":1,"why":"A mediana divide os dados ordenados em duas metades."},
    {"id":"cx4","subject":"Probabilidade e Estatística","q":"Uma amostra é…","options":["todo elemento possível","um subconjunto observado da população","sempre maior que a população","um gráfico de setores"],"a":1,"why":"A amostra é uma parte da população usada para análise."},
    {"id":"cx5","subject":"Ética e Compliance","q":"Qual conjunto corresponde aos princípios expressos no art. 37 da Constituição?","options":["Legalidade, impessoalidade, moralidade, publicidade e eficiência","Liberdade, lucro, mercado, sigilo e hierarquia","Publicidade, exclusividade, oportunidade, rapidez e lucro","Legalidade, pessoalidade, sigilo, informalidade e eficiência"],"a":0,"why":"O art. 37 traz o conjunto conhecido como LIMPE."},
    {"id":"cx6","subject":"Ética e Compliance","q":"A LGPD trata principalmente…","options":["de regras para câmbio","da proteção de dados pessoais","de amortização de empréstimos","de redação oficial"],"a":1,"why":"A Lei 13.709/2018 dispõe sobre tratamento de dados pessoais."},
    {"id":"cx7","subject":"Conhecimentos Bancários","q":"O PIX é…","options":["um título público","um sistema de pagamentos instantâneos","uma modalidade de previdência","uma moeda estrangeira"],"a":1,"why":"O PIX permite transferências e pagamentos em tempo real, conforme regras do arranjo."},
    {"id":"cx8","subject":"Conhecimentos Bancários","q":"O Sistema Financeiro Nacional é composto por…","options":["somente bancos comerciais","órgãos normativos, supervisores e instituições operadoras, entre outros participantes","apenas fintechs","somente o Banco Central e a Caixa"],"a":1,"why":"O SFN tem diferentes órgãos e instituições com funções normativas, supervisoras e operacionais."},
    {"id":"cx9","subject":"Conhecimentos Bancários","q":"Open Finance está ligado a…","options":["compartilhamento padronizado de dados e serviços, mediante consentimento e regras aplicáveis","abertura automática de contas sem autorização","fim de todo sigilo bancário","uso exclusivo de dinheiro físico"],"a":0,"why":"O compartilhamento ocorre conforme consentimento e regras regulatórias."},
    {"id":"cx10","subject":"Tecnologia da Informação e Comunicação","q":"Qual é uma prática segura contra phishing?","options":["abrir qualquer anexo urgente","confirmar remetente e endereço antes de clicar","reutilizar senhas","enviar códigos por e-mail a desconhecidos"],"a":1,"why":"Verificar remetente, domínio e destino do link reduz o risco de fraude."},
    {"id":"cx11","subject":"Tecnologia da Informação e Comunicação","q":"Uma intranet é, em geral…","options":["uma rede privada de uma organização","um tipo de planilha","um protocolo de câmbio","um editor de texto"],"a":0,"why":"A intranet é uma rede privada que usa tecnologias semelhantes às da internet."},
    {"id":"cx12","subject":"Conhecimentos e Comportamentos Digitais","q":"Em métodos ágeis, o foco central tende a ser…","options":["evitar qualquer feedback","entregar valor em ciclos e aprender com retorno frequente","planejar tudo e nunca alterar","trabalhar sem colaboração"],"a":1,"why":"Métodos ágeis valorizam entregas frequentes, colaboração e adaptação."},
    {"id":"cx13","subject":"Conhecimentos e Comportamentos Digitais","q":"OKR é uma abordagem para…","options":["definir objetivos e resultados-chave","criptografar arquivos","calcular juros compostos","substituir o atendimento"],"a":0,"why":"OKR significa Objectives and Key Results."},
    {"id":"cx14","subject":"Atendimento Bancário","q":"Escuta ativa no atendimento significa…","options":["interromper para oferecer logo o produto","ouvir, confirmar entendimento e responder ao que o cliente precisa","usar apenas respostas padronizadas","evitar perguntas"],"a":1,"why":"A escuta ativa busca compreender a necessidade antes de responder ou oferecer soluções."},
    {"id":"cx15","subject":"Atendimento Bancário","q":"Uma venda ética começa por…","options":["omitir custos","prometer resultado garantido","identificar necessidades e apresentar informações claras","pressionar por decisão imediata"],"a":2,"why":"O atendimento deve ser transparente e adequado à necessidade do cliente."},
    {"id":"cx16","subject":"Língua Portuguesa","q":"Coesão textual diz respeito principalmente…","options":["à ligação linguística entre partes do texto","ao tamanho da fonte","à quantidade de parágrafos, somente","ao número de palavras"],"a":0,"why":"Coesão conecta elementos do texto por recursos linguísticos."},
    {"id":"cx17","subject":"Língua Inglesa","q":"Em um texto, a palavra 'increase' geralmente significa…","options":["diminuir","aumentar","esconder","emprestar"],"a":1,"why":"Increase significa aumentar ou incremento, conforme o contexto."},
    {"id":"cx18","subject":"Redação","q":"Uma redação dissertativa bem estruturada costuma conter…","options":["apenas uma lista","introdução, desenvolvimento e conclusão","somente citações","períodos sem conexão"],"a":1,"why":"Essa estrutura ajuda a apresentar tese, argumentos e fechamento coerente."},
]

SHOP_ITEMS = [
    {"id":"weapon_ember","name":"Lâmina de Brasa","slot":"weapon","cost":65,"attack":5,"defense":0,"hp":0,"focus":0,"desc":"Uma lâmina que aquece a cada missão concluída."},
    {"id":"weapon_umbra","name":"Fio da Umbra","slot":"weapon","cost":150,"attack":11,"defense":0,"hp":0,"focus":1,"desc":"Forjada com metal recolhido no limite da noite."},
    {"id":"armor_vigil","name":"Manto do Vigia","slot":"armor","cost":75,"attack":0,"defense":4,"hp":20,"focus":0,"desc":"Costuras reforçadas para sobreviver a longas jornadas."},
    {"id":"armor_abyss","name":"Couraça do Abismo","slot":"armor","cost":165,"attack":0,"defense":9,"hp":38,"focus":0,"desc":"Pesada, mas firme diante de um golpe decisivo."},
    {"id":"charm_quill","name":"Selo do Escriba","slot":"charm","cost":60,"attack":1,"defense":0,"hp":0,"focus":4,"desc":"Transforma pequenas descobertas em concentração."},
    {"id":"charm_oracle","name":"Olho da Oráculo","slot":"charm","cost":140,"attack":3,"defense":1,"hp":10,"focus":7,"desc":"Um talismã que recompensa a curiosidade disciplinada."},
    {"id":"potion","name":"Elixir de Ânimo","slot":"consumable","cost":22,"attack":0,"defense":0,"hp":0,"focus":0,"desc":"Recupera saúde durante uma batalha."},
]

STORY = {
    "intro": [
        ("ÍRIA, a guardiã", "A Cidade Sem Aurora não perdeu o sol de uma vez. Primeiro, as pessoas deixaram de terminar o que começavam. Depois, esqueceram o que tinham aprendido. Por fim, a noite tomou as ruas."),
        ("ÍRIA, a guardiã", "Você não precisa vencer tudo hoje. Precisa voltar amanhã um pouco mais preparado. Cada missão que conclui reacende um fragmento da Forja."),
        ("VOCÊ", "E se eu falhar?"),
        ("ÍRIA, a guardiã", "Falhar é informação. Abandonar a jornada é que entrega a cidade ao Vazio. Escolha seu caminho. A Forja cuidará do resto — desde que você faça sua parte."),
    ],
    "boss_1": [
        ("ÍRIA", "O primeiro guardião caiu. Não foi a força que abriu caminho: foi a sua constância. Leve essa prova com você."),
        ("ECO", "Você voltou… achei que a primeira dificuldade seria suficiente para te afastar."),
        ("VOCÊ", "Ainda estou aqui."),
    ],
    "boss_2": [
        ("ÍRIA", "A segunda porta exige algo diferente: lembrar sem apenas reler. Mostre que consegue recuperar o que aprendeu quando a resposta não está diante dos olhos."),
        ("ECO", "A memória falha. O esforço pesa. Quantas vezes você vai recomeçar?"),
        ("VOCÊ", "Quantas forem necessárias."),
    ],
    "boss_3": [
        ("ÍRIA", "Você já mudou mais do que percebe. Agora precisa combinar as ferramentas que reuniu em vez de depender de uma só."),
        ("ECO", "Mais um nível não faz de você invencível."),
        ("VOCÊ", "Não. Mas me torna mais capaz do que ontem."),
    ],
    "boss_4": [
        ("ÍRIA", "A penúltima porta não pergunta o quanto você estudou. Pergunta o que consegue fazer com o que estudou."),
        ("ECO", "Chegar até aqui foi sorte."),
        ("VOCÊ", "Então vou provar isso mais uma vez."),
    ],
    "ending": [
        ("O REI DA ÚLTIMA PÁGINA", "Você poderia ter esperado pelo momento perfeito. Em vez disso, acumulou pequenos começos."),
        ("ÍRIA", "A noite não desaparece para sempre. Mas agora você sabe acender a própria luz."),
        ("NARRADOR", "A Forja se apaga, não por ter sido vencida, mas porque já não precisa manter a chama por você. A próxima jornada será sua escolha."),
    ],
}

BOSS_NAMES = [
    ("O Cobrador de Ecos", "A criatura que transforma dúvidas em adiamento."),
    ("A Matriarca da Névoa", "Ela embaralha conceitos até que pareçam impossíveis."),
    ("O Cartógrafo Cego", "Ele esconde o caminho dentro de problemas que parecem desconexos."),
    ("A Sentinela da Última Ponte", "Seu escudo cede apenas diante da prática consistente."),
    ("O Rei da Última Página", "O guardião final da campanha — só enfrenta quem concluiu a trilha."),
]


def make_missions(profile_key):
    missions = []
    if profile_key == "python":
        for i, (topic, detail) in enumerate(PYTHON_PHASES):
            for j, (verb, how, xp, coins) in enumerate(PYTHON_MISSION_SUFFIXES):
                missions.append({"id":f"py_{i+1}_{j+1}","topic":topic,"title":f"{topic}: {verb}","description":f"{detail}. {how}","xp":xp + (5 if i > 9 else 0),"coins":coins,"kind":"study","completed":False})
    elif profile_key == "caixa":
        for i, (topic, detail, weight) in enumerate(CAIXA_SUBJECTS):
            tasks = CAIXA_MISSION_SUFFIXES if topic != "Redação" else [
                ("Estudar estrutura", "Revise introdução, tese, desenvolvimento e conclusão.", 30, 10),
                ("Escrever um texto", "Produza um texto dissertativo e revise clareza, coesão e argumentação.", 55, 20),
                ("Reescrever após revisão", "Identifique pontos fracos e reescreva o texto com foco em precisão.", 40, 14),
            ]
            for j, (verb, how, xp, coins) in enumerate(tasks):
                block = "Redação" if topic == "Redação" else ("Conhecimentos Básicos" if topic in {"Língua Portuguesa", "Língua Inglesa", "Matemática Financeira", "Probabilidade e Estatística", "Ética e Compliance"} else "Conhecimentos Específicos")
                missions.append({"id":f"cx_{i+1}_{j+1}","topic":topic,"title":f"{topic}: {verb}","description":f"{detail} {how}","xp":xp + (10 if weight >= 10 else 0),"coins":coins + (5 if weight >= 10 else 0),"weight":weight,"block":block,"kind":"study","completed":False})
    else:
        topics = ["Trilha pessoal 1 — renomeie", "Trilha pessoal 2 — renomeie", "Trilha pessoal 3 — renomeie", "Projeto livre — renomeie", "Revisão final — renomeie"]
        for i, topic in enumerate(topics):
            for j, (verb, how, xp, coins) in enumerate(CAIXA_MISSION_SUFFIXES):
                missions.append({"id":f"custom_{i+1}_{j+1}","topic":topic,"title":f"{topic}: {verb}","description":how,"xp":xp,"coins":coins,"kind":"study","completed":False})
    return missions


def default_profile(key):
    if key == "python":
        title, hero, archetype, intro = "A Forja do Código", "O Aprendiz da Forja", "Artífice", "A trilha transforma o curso de Python em pequenas missões: teoria, prática e revisão. O objetivo não é marcar aulas como vistas, mas construir habilidade com as próprias mãos."
        topics = [x[0] for x in PYTHON_PHASES]
    elif key == "caixa":
        title, hero, archetype, intro = "A Rota da Caixa", "O Guardião do Atendimento", "Estrategista", "Uma campanha para preparar o Técnico Bancário Novo (não TI), organizada pelos componentes do edital da CAIXA 2024 que você enviou. O conteúdo é uma base de planejamento, não substitui materiais atualizados nem um novo edital."
        topics = [x[0] for x in CAIXA_SUBJECTS]
    else:
        title, hero, archetype, intro = "A Jornada Livre", "Aventureiro Personalizado", "Explorador", "Este slot é seu. Defina o que quer aprender, crie suas próprias etapas e escolha os guardiões que marcarão seu progresso."
        topics = ["Trilha pessoal 1 — renomeie", "Trilha pessoal 2 — renomeie", "Trilha pessoal 3 — renomeie", "Projeto livre — renomeie", "Revisão final — renomeie"]
    bosses = [{"id":f"{key}_boss_{i+1}","name":name,"subtitle":sub,"threshold":0,"hp":120+i*65,"attack":8+i*3,"reward_xp":70+i*25,"reward_gold":45+i*20} for i,(name,sub) in enumerate(BOSS_NAMES)]
    if key == "python":
        missions = make_missions("python")
    elif key == "caixa":
        missions = make_missions("caixa")
    else:
        missions = make_missions("custom")
    milestones = [max(3, int(len(missions)*0.08)), max(4, int(len(missions)*0.28)), max(5, int(len(missions)*0.50)), max(6, int(len(missions)*0.75)), len(missions)]
    for i,boss in enumerate(bosses):
        boss["threshold"] = min(len(missions), milestones[i]) if i < len(milestones)-1 else len(missions)
        if i and boss["threshold"] <= bosses[i-1]["threshold"]:
            boss["threshold"] = min(len(missions), bosses[i-1]["threshold"] + 1)
    return {
        "key":key,"settings":{"title":title,"hero":hero,"archetype":archetype,"intro":intro,"topics":topics,"boss_names":[b["name"] for b in bosses],"missions_text":""},
        "level":1,"xp":0,"gold":120 if key != "custom" else 80,"completed_missions":[],"bosses_defeated":[],"mission_data":missions,"boss_data":bosses,
        "attributes":{"strength":1,"focus":1,"endurance":1},"attribute_points":0,"inventory":["weapon_training"],"equipped":{"weapon":"weapon_training","armor":None,"charm":None},"potions":2,
        "last_study_date":"","streak":0,"history":[],"quiz_answered":[],"event_claims":{},"story_seen":[],"notes":"","custom_quiz_text":""
    }


def create_save():
    return {"version":1,"active_profile":"python","profiles":{"python":default_profile("python"),"caixa":default_profile("caixa"),"custom":default_profile("custom")}}
