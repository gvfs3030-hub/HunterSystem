"""Campanhas lineares do Hunter System.

Os textos didáticos são resumos e exercícios originais para guiar o estudo; não substituem
as aulas do curso nem o edital. A trilha Python é organizada por tópicos de estudo a partir
dos temas e da ementa pública do curso. A trilha Caixa segue os eixos do edital 01/2024/NM
fornecido pelo usuário.
"""
from __future__ import annotations
from copy import deepcopy

# Questions are intentionally short and self-contained. Each topic receives a rotating
# subset from its relevant bank; failed attempts can be repeated without losing progress.
def Q(subject, question, options, answer, explanation):
    return {"subject": subject, "q": question, "options": options, "a": answer, "why": explanation}

PYTHON_BANKS = {
"environment": [
 Q("Ambiente", "Qual comando costuma mostrar a versão do Python instalado?", ["python --version", "python --erase", "version python", "pip --remove"], 0, "python --version consulta a versão do interpretador."),
 Q("Ambiente", "Qual é a extensão usual de um arquivo de código Python?", [".py", ".pt", ".pytxt", ".exe"], 0, "Arquivos-fonte Python normalmente usam a extensão .py."),
 Q("Ambiente", "Para que serve o terminal integrado do VS Code?", ["Executar comandos e programas", "Trocar automaticamente toda a lógica", "Substituir todos os arquivos", "Garantir que não existam bugs"], 0, "O terminal permite executar comandos, scripts e ferramentas do projeto."),
 Q("Ambiente", "Por que vale testar um pequeno script no início?", ["Confirmar que instalação e execução funcionam", "Pular o aprendizado de sintaxe", "Dispensar o interpretador", "Evitar escrever código"], 0, "Um teste mínimo reduz problemas de ambiente antes de avançar."),
 Q("Ambiente", "Um ambiente virtual serve principalmente para…", ["Isolar dependências de um projeto", "Aumentar a velocidade física do PC", "Substituir o Python", "Fazer backup automático de tudo"], 0, "venv isola bibliotecas usadas por projeto."),
],
"logic": [
 Q("Fundamentos", "Qual função exibe texto no terminal?", ["show()", "print()", "write_screen()", "echo_python()"], 1, "print() envia uma representação para a saída padrão."),
 Q("Fundamentos", "Qual chamada coleta texto digitado pelo usuário?", ["input()", "readline_user()", "ask()", "scan()"], 0, "input() lê uma linha e retorna uma string."),
 Q("Fundamentos", "Qual tipo representa verdadeiro ou falso?", ["str", "float", "bool", "dict"], 2, "bool representa valores True e False."),
 Q("Fundamentos", "O que a expressão 10 // 3 retorna?", ["3", "3.33", "1", "30"], 0, "// é divisão inteira por piso: o resultado é 3."),
 Q("Fundamentos", "Qual estrutura permite escolher entre caminhos com base numa condição?", ["if/elif/else", "import", "class", "with"], 0, "Condicionais controlam qual bloco será executado."),
 Q("Fundamentos", "Qual laço é adequado para percorrer uma sequência de itens?", ["for", "class", "return", "raise"], 0, "for percorre elementos de um iterável."),
 Q("Fundamentos", "O que break faz dentro de um laço?", ["Encerra o laço", "Pula apenas a iteração atual", "Reinicia o Python", "Cria uma função"], 0, "break interrompe imediatamente o laço atual."),
 Q("Fundamentos", "Por que usar f-strings?", ["Interpolar valores em strings de forma legível", "Criar banco de dados", "Importar pacotes automaticamente", "Repetir loops"], 0, "f-strings permitem inserir expressões entre chaves em texto."),
],
"functions": [
 Q("Funções", "Qual palavra-chave define uma função nomeada?", ["func", "def", "function", "method"], 1, "Em Python, a definição começa com def."),
 Q("Funções", "Qual é a diferença central entre print e return?", ["print exibe; return devolve um valor ao chamador", "São sempre idênticos", "return só funciona em loops", "print encerra o programa"], 0, "return disponibiliza um resultado para o código que chamou a função."),
 Q("Funções", "O que acontece quando uma função não executa return explícito?", ["Retorna None", "Retorna sempre 0", "O programa não inicia", "Retorna o último print"], 0, "O retorno padrão de uma função Python é None."),
 Q("Coleções", "Qual estrutura armazena pares chave-valor?", ["list", "tuple", "dict", "range"], 2, "dict mapeia chaves para valores."),
 Q("Coleções", "Qual coleção elimina valores repetidos?", ["set", "list", "str", "tuple"], 0, "Um set guarda elementos únicos."),
 Q("Iteração", "O que é um iterável?", ["Um objeto cujos elementos podem ser percorridos", "Apenas um número inteiro", "Sempre um arquivo", "Uma classe abstrata obrigatória"], 0, "Listas, strings, tuplas e muitos outros objetos são iteráveis."),
 Q("Funções", "Para que serve *args numa assinatura?", ["Receber quantidade variável de argumentos posicionais", "Tornar todos os parâmetros globais", "Capturar erros", "Criar uma classe"], 0, "*args reúne argumentos posicionais extras numa tupla."),
 Q("Compreensão", "Uma list comprehension é útil para…", ["Construir uma lista a partir de um iterável", "Abrir uma janela gráfica automaticamente", "Definir uma tabela SQL", "Substituir toda função"], 0, "Ela combina iteração e expressão numa construção concisa."),
],
"oop": [
 Q("POO", "Uma classe é melhor descrita como…", ["Um molde para criar objetos", "Um arquivo de texto obrigatório", "Um tipo de loop", "Uma exceção"], 0, "A classe define atributos e comportamentos de suas instâncias."),
 Q("POO", "Qual é o papel usual de __init__?", ["Inicializar o estado de uma instância", "Apagar a classe", "Importar um módulo", "Rodar os testes"], 0, "__init__ configura o objeto depois que ele é criado."),
 Q("POO", "O parâmetro self representa…", ["A instância que está recebendo a chamada", "A classe pai em todos os casos", "Um valor booleano", "O terminal"], 0, "self referencia o objeto atual nos métodos de instância."),
 Q("POO", "Herança permite…", ["Derivar uma classe a partir de outra", "Executar um SELECT", "Instalar dependências", "Transformar str em int sem conversão"], 0, "Uma classe derivada pode especializar/reutilizar comportamento de outra."),
 Q("POO", "Composição descreve…", ["Um objeto que contém/usa outros objetos", "Apenas herança múltipla", "Uma variável local", "Um operador aritmético"], 0, "Composição modela relações do tipo 'tem um'."),
 Q("POO", "Polimorfismo permite…", ["Usar uma interface comum com implementações diferentes", "Eliminar todos os tipos", "Evitar todo teste", "Converter todo objeto em string"], 0, "Objetos diferentes podem responder ao mesmo contrato de maneiras próprias."),
 Q("POO", "O que dataclasses ajudam a reduzir?", ["Código repetitivo de classes focadas em dados", "Número de tabelas no banco", "Necessidade de compreender atributos", "Erros de rede"], 0, "dataclass gera métodos comuns como __init__ e representação."),
],
"advanced": [
 Q("Python avançado", "Um generator tende a produzir valores…", ["Sob demanda, conforme é iterado", "Todos de uma vez obrigatoriamente", "Somente em banco SQL", "Apenas como string"], 0, "Generators podem pausar e retomar com yield."),
 Q("Python avançado", "Um decorador é usado para…", ["Envolver/alterar comportamento de uma função ou classe", "Criar uma pasta", "Escrever uma query SQL", "Instalar Python"], 0, "Decoradores recebem e devolvem objetos chamáveis ou classes."),
 Q("Python avançado", "Para que serve um context manager com with?", ["Gerenciar entrada/saída de um contexto e sua limpeza", "Criar um loop infinito", "Ignorar exceções automaticamente em todos os casos", "Renomear variáveis"], 0, "with organiza recursos, como fechamento de arquivo, mesmo diante de erro."),
 Q("Python avançado", "O que uma type hint oferece?", ["Uma anotação sobre tipos esperados", "Garantia absoluta de tipo em execução", "Uma interface gráfica", "Uma conexão automática com SQL"], 0, "Type hints documentam intenções e apoiam ferramentas de análise."),
 Q("Python avançado", "O que __str__ costuma fornecer?", ["Uma representação textual amigável do objeto", "Um iterador", "Uma conexão de rede", "Uma exceção"], 0, "__str__ define o texto usado por str(objeto)."),
],
"modules": [
 Q("Módulos", "O papel de import é…", ["Disponibilizar nomes de um módulo", "Apagar o interpretador", "Criar automaticamente uma classe", "Executar todo arquivo do PC"], 0, "import permite utilizar funcionalidades de módulos."),
 Q("Arquivos", "Por que usar with open(...) para arquivos?", ["Gerenciar o fechamento do arquivo mesmo em situações de erro", "Impedir a leitura", "Converter arquivo em classe", "Pular permissões"], 0, "O gerenciador de contexto ajuda a garantir o fechamento do recurso."),
 Q("Arquivos", "Qual módulo da biblioteca padrão facilita ler e gravar JSON?", ["json", "webpage", "sqlpy", "picture"], 0, "json disponibiliza dump/load e dumps/loads."),
 Q("Arquivos", "Para caminhos que funcionem bem entre sistemas, qual alternativa é indicada?", ["pathlib", "print", "random", "enum"], 0, "pathlib representa caminhos com uma API orientada a objetos."),
 Q("Dependências", "Qual arquivo costuma listar dependências de um projeto?", ["requirements.txt", "lesson.png", "main.exe", "desktop.ini"], 0, "requirements.txt é uma convenção para dependências pip."),
],
"regex": [
 Q("Regex", "Uma expressão regular serve para…", ["Encontrar ou validar padrões em texto", "Criar objetos de banco automaticamente", "Desenhar botões", "Compilar o .exe"], 0, "Regex descreve padrões para busca e validação de strings."),
 Q("Regex", "Em regex, \u005cd normalmente representa…", ["Um dígito", "Qualquer arquivo", "Uma classe Python", "Uma quebra de projeto"], 0, "\\d corresponde a um dígito decimal em padrões comuns."),
 Q("Regex", "Por que testar regex com casos válidos e inválidos?", ["Para verificar limites e evitar correspondências indevidas", "Para aumentar a velocidade da internet", "Para criar tabelas", "Porque todo texto é igual"], 0, "Casos variados revelam falsos positivos e falsos negativos."),
 Q("Regex", "Qual módulo padrão oferece operações de regex em Python?", ["re", "regexsql", "matchpy", "pattern"], 0, "O módulo re oferece search, match, findall, sub e outras funções."),
],
"tests": [
 Q("Testes", "Um teste unitário verifica principalmente…", ["Uma pequena unidade de comportamento", "Todo o computador", "A conexão Wi-Fi", "Somente cores da interface"], 0, "Testes unitários procuram verificar unidades isoladas."),
 Q("Testes", "No TDD, o ciclo clássico é…", ["Teste falha, implementar, refatorar", "Publicar, apagar, esquecer", "Instalar, reiniciar, publicar", "Copiar, colar, encerrar"], 0, "Red-Green-Refactor: escrever teste que falha, fazê-lo passar e refatorar."),
 Q("Testes", "Uma boa asserção expressa…", ["O resultado esperado", "O nome do autor", "A senha do sistema", "A posição da janela"], 0, "assert compara o comportamento obtido com o esperado."),
 Q("Testes", "Qual é uma boa reação a um teste que falha?", ["Investigar a causa e reproduzir o erro", "Apagar o teste imediatamente", "Ignorar o resultado", "Alterar o teste para sempre passar sem investigar"], 0, "Falhas devem ser entendidas antes de modificar código ou teste."),
],
"gui": [
 Q("Interface gráfica", "O que é um widget em uma GUI?", ["Um componente visual/interativo", "Um banco de dados", "Um pacote ZIP", "Um erro de sintaxe"], 0, "Botões, campos e rótulos são exemplos de widgets."),
 Q("Interface gráfica", "Signals e slots conectam…", ["Eventos a funções que reagem a eles", "Tabelas a planilhas apenas", "Usuários à internet automaticamente", "Comentários a variáveis"], 0, "Signals anunciam eventos e slots tratam esses eventos."),
 Q("Interface gráfica", "Por que separar a interface da lógica de negócio?", ["Facilita teste, manutenção e evolução", "Torna testes impossíveis", "Exige abandonar funções", "Remove a necessidade de dados"], 0, "Separação de responsabilidades reduz acoplamento."),
 Q("Interface gráfica", "Qual componente costuma organizar widgets em linhas e colunas?", ["Grid layout", "Exception handler", "JSON parser", "Cursor SQL"], 0, "Um grid layout posiciona componentes numa grade."),
],
"database": [
 Q("Banco de dados", "CRUD significa…", ["Create, Read, Update, Delete", "Copy, Run, Upload, Download", "Class, Return, Use, Debug", "Create, Route, Use, Deploy"], 0, "CRUD resume operações básicas sobre dados persistidos."),
 Q("Banco de dados", "Por que utilizar placeholders em consultas SQL?", ["Separar valores dos comandos e reduzir risco de SQL injection", "Deixar a query mais ambígua", "Substituir a chave primária", "Apagar todas as linhas"], 0, "Parâmetros são enviados ao driver sem concatenar valores no SQL."),
 Q("Banco de dados", "Qual comando SQL consulta registros?", ["SELECT", "INSERT", "DROP", "UPDATE"], 0, "SELECT recupera dados de uma ou mais tabelas."),
 Q("Banco de dados", "O que uma chave primária faz?", ["Identifica unicamente cada registro", "Armazena a senha do banco sem proteção", "Substitui todas as colunas", "Executa Python"], 0, "Uma chave primária identifica uma linha de forma única."),
 Q("Banco de dados", "Uma migração no Django é usada para…", ["Versionar/aplicar mudanças no esquema do banco", "Executar CSS", "Abrir o navegador", "Substituir autenticação"], 0, "Migrations registram e aplicam mudanças nos modelos do banco."),
],
"web": [
 Q("Web", "Em HTTP, uma request representa…", ["Uma solicitação feita a um servidor", "Um arquivo .py obrigatório", "Uma tabela de Excel", "Uma exceção do Python"], 0, "Request é a mensagem enviada pelo cliente ao servidor."),
 Q("Web", "O que uma API permite?", ["Comunicação estruturada entre sistemas", "Somente desenho de telas", "Acesso irrestrito a qualquer dado", "Substituição de testes"], 0, "APIs definem formas de sistemas trocarem dados e operações."),
 Q("Web", "Em Django, uma view normalmente…", ["Recebe uma requisição e produz uma resposta", "Instala o editor de código", "Cria um computador virtual", "Substitui qualquer modelo de dados"], 0, "Views processam requests e retornam responses."),
 Q("Web", "Para que serve um template?", ["Gerar a apresentação de uma página com dados", "Criar uma senha aleatória", "Executar consultas sem controle", "Compilar Python em Windows"], 0, "Templates combinam estrutura de apresentação e dados de contexto."),
 Q("Web", "Para que serve CSRF protection em formulários?", ["Mitigar requisições forjadas em contexto autenticado", "Corrigir pontuação de texto", "Gerar relatórios SQL", "Criar animações"], 0, "Tokens e validações CSRF ajudam a evitar submissões forjadas."),
],
"htmlcss": [
 Q("HTML/CSS", "HTML descreve principalmente…", ["A estrutura e o significado do conteúdo", "A conexão com MySQL", "Os testes Python", "O sistema operacional"], 0, "HTML organiza títulos, parágrafos, links, formulários e outros elementos."),
 Q("HTML/CSS", "CSS é usado para…", ["Estilizar a apresentação de páginas", "Executar consultas de banco", "Gerar números aleatórios", "Instalar bibliotecas Python"], 0, "CSS controla cores, espaçamentos, tipografia e layout."),
 Q("HTML/CSS", "Por que usar nomes de classes CSS consistentes?", ["Facilita manter e compreender os estilos", "Elimina a estrutura HTML", "Garante segurança absoluta", "Substitui o navegador"], 0, "Nomes claros melhoram organização e manutenção."),
 Q("HTML/CSS", "O que significa separar conteúdo e apresentação?", ["HTML estrutura o conteúdo; CSS controla a apresentação visual", "CSS armazena a base de dados", "HTML substitui todo o JavaScript", "Ambos devem ficar em um único atributo"], 0, "Separar estrutura e visualização melhora clareza e manutenção."),
],
"automation": [
 Q("Automação", "Web scraping costuma significar…", ["Extrair dados de páginas conforme regras e permissões", "Criar só interfaces desktop", "Criptografar todos os arquivos", "Executar SELECT local"], 0, "Scraping coleta conteúdo de páginas respeitando termos, políticas e limites."),
 Q("Automação", "No Selenium, WebDriver permite…", ["Controlar um navegador automatizado", "Escrever uma tabela SQL sem conexão", "Testar somente tipos estáticos", "Substituir o sistema operacional"], 0, "WebDriver interage com elementos do navegador."),
 Q("Automação", "Por que aguardar um elemento ficar disponível?", ["Páginas dinâmicas nem sempre carregam imediatamente", "Todos os navegadores têm tempo fixo", "Para ignorar erros", "Para tornar dados confidenciais públicos"], 0, "Esperas explícitas reduzem falhas por sincronização."),
 Q("Automação", "Threads são úteis quando…", ["É necessário coordenar tarefas concorrentes, considerando o tipo de trabalho", "Todo programa deve executar tudo em paralelo", "Não existem dependências", "Queremos dispensar testes"], 0, "Concorrência pode melhorar certos cenários, mas exige atenção à sincronização."),
],
"sql": [
 Q("SQL", "Qual cláusula filtra linhas consultadas?", ["WHERE", "SELECTOR", "FILTERBY", "ORDER"], 0, "WHERE restringe as linhas com base numa condição."),
 Q("SQL", "Qual cláusula ordena os resultados?", ["ORDER BY", "GROUP ONLY", "SORT SQL", "RANK WITH"], 0, "ORDER BY define a ordenação dos registros retornados."),
 Q("SQL", "Qual é uma boa prática ao atualizar dados?", ["Conferir a condição WHERE antes de executar", "Sempre executar sem WHERE", "Apagar a chave primária", "Concatenar diretamente entrada externa"], 0, "Uma condição incorreta pode alterar muitos registros."),
 Q("SQL", "O que uma chave primária representa?", ["Um identificador único de cada registro", "Uma consulta que ordena resultados", "Uma senha do banco", "Um comentário SQL"], 0, "A chave primária identifica cada linha e não pode repetir valor nem ser nula."),
],
"patterns": [
 Q("Arquitetura", "Um padrão de projeto descreve…", ["Uma solução recorrente para um tipo de problema de projeto", "Um comando obrigatório do Python", "Uma questão de prova", "Um formato de imagem"], 0, "Padrões registram soluções conhecidas, não receitas para qualquer problema."),
 Q("Arquitetura", "Por que evitar aplicar padrões sem necessidade?", ["Podem adicionar complexidade sem benefício real", "Padrões nunca funcionam", "Código simples é proibido", "Testes deixam de existir"], 0, "Use o padrão quando ele resolve um problema concreto do desenho."),
 Q("Arquitetura", "O objetivo de refatorar é…", ["Melhorar a estrutura interna preservando o comportamento esperado", "Adicionar bugs de propósito", "Mudar requisitos sem avisar", "Apagar os testes"], 0, "Refatoração melhora design sem alterar o comportamento observável."),
 Q("Arquitetura", "Quando um padrão de projeto é uma escolha ruim?", ["Quando é aplicado sem que o problema realmente precise dele", "Quando simplifica uma variação recorrente", "Quando tem teste adequado", "Quando melhora a comunicação da equipe"], 0, "Padrões são ferramentas; uso desnecessário aumenta complexidade."),
],
"project": [
 Q("Projeto", "Qual sequência ajuda a iniciar um projeto confiável?", ["Definir problema, requisitos, modelo e pequenos incrementos", "Programar tudo sem objetivo", "Publicar sem executar", "Escrever apenas o README"], 0, "Planejamento incremental permite validar cada etapa."),
 Q("Projeto", "Por que registrar instruções de execução?", ["Para que outra pessoa consiga preparar e executar o projeto", "Para substituir código", "Para garantir que não haja erros", "Para esconder dependências"], 0, "Um README reproduzível registra instalação, execução e limites conhecidos."),
 Q("Projeto", "Antes de publicar, o que deve acontecer?", ["Testar o fluxo principal, documentar e revisar a configuração", "Excluir testes", "Adicionar credenciais ao repositório", "Ignorar falhas de instalação"], 0, "Validar instalação, execução e segurança reduz falhas de entrega."),
 Q("Projeto", "Qual item deve permanecer fora de um repositório público?", ["Segredos, tokens e credenciais", "README de instalação", "Testes automatizados", "Código sem credenciais"], 0, "Credenciais devem ser protegidas e fornecidas por mecanismos adequados de configuração."),
],
}

# (título da etapa, ideia-chave, desafio prático, grupo de questões)
PYTHON_CHAPTERS = [
("Prólogo: aceitar a missão", "Boas-vindas, organização do curso e método de estudo", "A Cidade Sem Aurora precisa de alguém que volte todos os dias. Você não precisa saber tudo agora: precisa criar um método sustentável.", [
 ("Ler o mapa do curso", "A trilha é longa; dividi-la em pequenas sessões reduz a fricção e ajuda a visualizar o avanço.", "Abra a área do curso e anote em que seção está e qual será a próxima aula.", "project"),
 ("Definir uma sessão realista", "Uma sessão precisa caber na rotina. Melhor uma meta modesta concluída do que um plano enorme abandonado.", "Escolha um bloco de 25–45 minutos e um objetivo observável para ele.", "project"),
 ("Aprender ativamente", "Pausar o vídeo, prever a saída, digitar o código e explicar o motivo de cada linha é mais útil do que assistir passivamente.", "Antes da próxima demonstração, pause e tente prever o resultado.", "project"),
 ("Criar o diário de bordo", "Anotações devem guardar dúvidas, erros recorrentes e exemplos próprios, não transcrever a aula inteira.", "Registre três conceitos e uma dúvida para revisar amanhã.", "project"),
]),
("Preparar a Forja: Python e VS Code", "Instalação no Windows, editor, terminal, interpretação e ambiente de trabalho", "O arsenal está espalhado. Íria mostra que nenhuma aventura progride sem preparar as ferramentas certas.", [
 ("Verificar o Python no Windows", "O interpretador executa o arquivo .py. Conferir a versão no terminal confirma qual instalação está sendo chamada.", "No terminal, tente python --version e depois py --version; registre o resultado.", "environment"),
 ("Instalar e reconhecer o VS Code", "O editor ajuda a escrever e navegar no código, mas é o interpretador que executa Python.", "Abra o VS Code e identifique editor, explorador de arquivos e terminal.", "environment"),
 ("Criar o primeiro arquivo .py", "Um script é um arquivo de texto com instruções Python, salvo normalmente com extensão .py.", "Crie primeiro.py com print('A Forja está acesa') e execute-o.", "environment"),
 ("Ler mensagens do terminal", "A mensagem de erro costuma indicar arquivo, linha e tipo de problema; ler tudo evita correções às cegas.", "Cometa um erro de sintaxe intencional, leia o traceback e depois corrija-o.", "environment"),
 ("Configurar o editor para estudar", "Indentação consistente, terminal acessível e destaque de sintaxe diminuem erros visuais.", "Configure a indentação e pratique executar o arquivo salvo.", "environment"),
 ("Conhecer pacotes e ambiente virtual", "Um ambiente virtual isola bibliotecas do projeto e evita conflitos entre dependências.", "Crie uma venv de teste e registre como ativá-la no Windows.", "environment"),
]),
("A primeira centelha: lógica e sintaxe", "Interpretador, comentários, impressão, tipos, variáveis, operadores e condições", "A primeira muralha não se abre com força: ela responde a instruções precisas. Você aprenderá a transformar uma ideia em passos executáveis.", [
 ("Interpretador, scripts e comentários", "O Python lê instruções; comentários explicam decisões para pessoas e não são executados. Docstrings documentam módulos, classes e funções.", "Escreva um script curto com comentário útil e uma docstring quando fizer sentido.", "logic"),
 ("print e entrada de dados", "print apresenta resultados; input recolhe texto. A entrada precisa ser validada e convertida quando o programa espera número.", "Peça nome e idade, converta a idade para inteiro e apresente uma frase.", "logic"),
 ("Strings e métodos básicos", "Strings representam texto. Fatiamento, len, strip, split e join ajudam a limpar e transformar valores.", "Receba uma frase com espaços extras e exiba a versão limpa e a quantidade de caracteres.", "logic"),
 ("Inteiros, decimais e booleanos", "int, float e bool modelam valores diferentes. Escolher o tipo correto evita comparações e cálculos incoerentes.", "Converta texto numérico e teste valores verdadeiros e falsos em exemplos pequenos.", "logic"),
 ("Conversão de tipos e imprecisão decimal", "Conversão pode falhar quando o texto não tem formato válido. float usa representação binária aproximada em vários decimais.", "Compare 0.1 + 0.2 com 0.3 e experimente round ou Decimal num valor financeiro.", "logic"),
 ("Variáveis, constantes e nomes", "Variáveis associam nomes a objetos. Nomes claros e convenções consistentes tornam a intenção visível.", "Refatore um cálculo para usar nomes descritivos em vez de valores soltos.", "logic"),
 ("Operadores e precedência", "Operadores aritméticos seguem regras de precedência; parênteses tornam a intenção explícita.", "Faça uma calculadora de duas entradas com soma, subtração, multiplicação e divisão protegida.", "logic"),
 ("f-strings e formatação", "f-strings permitem interpolar expressões; formatos numéricos ajudam a exibir valores monetários e percentuais.", "Exiba um preço com duas casas decimais e uma porcentagem com formato legível.", "logic"),
 ("Comparações e condicionais", "if/elif/else escolhe um caminho. Comparações produzem booleanos que controlam a decisão.", "Crie regras para classificar uma nota em aprovado, recuperação e reprovado.", "logic"),
 ("and, or, not, in e identidade", "Operadores lógicos combinam condições; in verifica pertinência e is testa identidade do objeto, não igualdade geral.", "Escreva uma validação com duas condições e explique quando usar == em vez de is.", "logic"),
 ("Erros e try/except", "Exceções representam falhas durante a execução. Trate apenas erros esperados e não esconda toda falha com except genérico.", "Proteja a conversão de um número digitado e mostre uma mensagem útil em caso inválido.", "logic"),
 ("while, break e continue", "while repete enquanto a condição é verdadeira; break encerra o laço e continue pula para a próxima iteração.", "Monte um menu de terminal que continue até o usuário escolher sair.", "logic"),
 ("for, range e iteráveis", "for percorre cada elemento de um iterável; range produz uma sequência de inteiros para contagens.", "Some os números de 1 a 100 e compare uma solução com for e outra com while.", "logic"),
 ("Listas, índices e operações", "Listas são coleções ordenadas e mutáveis. Índices, append, insert, pop e del permitem manipular elementos.", "Construa uma lista de tarefas que permita adicionar e remover itens.", "functions"),
 ("Tuplas, desempacotamento e enumerate", "Tuplas são sequências imutáveis; desempacotamento atribui elementos a variáveis, e enumerate fornece índice e valor.", "Exiba cada item de uma lista numerado a partir de 1.", "functions"),
 ("Projetos de lógica: IMC e validador", "Projetos pequenos consolidam entrada, cálculo, condição e validação. A solução precisa ser testada com vários casos.", "Implemente um cálculo simples e teste entradas válidas, zero e valores inesperados.", "project"),
]),
("A trilha se bifurca: funções e coleções", "Funções, parâmetros, retornos, escopo, dicionários, conjuntos e programação funcional", "Um mecanismo que só funciona numa única situação é frágil. A próxima porta exige que você transforme instruções em ferramentas reutilizáveis.", [
 ("Definir funções com def", "Uma função encapsula comportamento com nome. Parâmetros tornam a operação reutilizável em entradas diferentes.", "Crie uma função que receba dois números e devolva o maior.", "functions"),
 ("Argumentos posicionais e nomeados", "Argumentos posicionais dependem da ordem; nomeados deixam explícito a qual parâmetro pertence cada valor.", "Chame a mesma função de duas formas e compare a legibilidade.", "functions"),
 ("Valores padrão, None e retorno", "Parâmetros podem ter padrões; return devolve um resultado e encerra aquela chamada da função.", "Crie uma função de desconto com taxa padrão e teste quando não houver retorno explícito.", "functions"),
 ("Escopo local, global e nonlocal", "O escopo define onde um nome pode ser acessado. Prefira entradas e retornos claros a alterar estado global sem necessidade.", "Separe uma variável global numa função com parâmetro e retorno.", "functions"),
 ("*args e **kwargs", "*args reúne argumentos posicionais extras e **kwargs reúne argumentos nomeados extras.", "Escreva uma função que receba vários itens e outra que receba configurações nomeadas.", "functions"),
 ("Dicionários e operações", "dict associa chaves a valores; get, items, keys e values ajudam a consultar e percorrer dados.", "Modele um cadastro simples usando nome, email e estado numa estrutura de dicionário.", "functions"),
 ("Sets e remoção de duplicados", "set mantém elementos únicos e oferece operações de união, interseção e diferença.", "Encontre valores que aparecem em ambas as listas de participantes.", "functions"),
 ("Compreensões e expressões lambda", "Compreensões constroem coleções a partir de iteráveis; lambda define uma pequena função anônima.", "Filtre pares de uma lista e ordene uma lista de tuplas por um campo.", "functions"),
 ("Iteradores, generators e yield", "Um iterador fornece o próximo valor; generators produzem valores sob demanda e podem economizar memória.", "Escreva um generator que produza os quadrados de números de um intervalo.", "functions"),
 ("Recursão e limites", "Recursão resolve um problema chamando a própria função, mas precisa de caso-base e pode atingir limite de chamadas.", "Escreva uma função recursiva simples e identifique seu caso-base.", "functions"),
 ("Modularizar funções", "Funções pequenas e módulos separados reduzem repetição e facilitam testes e manutenção.", "Divida uma calculadora em funções e mova as operações para um módulo próprio.", "modules"),
]),
("A oficina ganha estrutura: POO", "Classes, estado, métodos, herança, composição, polimorfismo e dataclasses", "A oficina está cheia de peças soltas. Íria lhe ensina a dar forma a objetos que guardam estado e comportamento sem transformar tudo num bloco único.", [
 ("Classe, instância e __init__", "A classe descreve estrutura e comportamento; instâncias são objetos concretos. __init__ inicializa seus atributos.", "Modele um personagem com nome, vida e método receber_dano.", "oop"),
 ("self, atributos e métodos", "self referencia a instância atual. Métodos operam sobre seus atributos ou colaboram com outras operações.", "Crie um método que altere a vida do personagem sem modificar atributos externamente.", "oop"),
 ("Estado, atributos de classe e __dict__", "Atributos de instância pertencem a cada objeto; atributos de classe são compartilhados pela definição da classe.", "Crie dois objetos e prove que o estado individual é independente.", "oop"),
 ("Métodos de classe e estáticos", "classmethod recebe a classe; staticmethod não recebe automaticamente instância nem classe. Use cada um por intenção clara.", "Implemente um construtor alternativo com classmethod.", "oop"),
 ("Properties e encapsulamento", "Properties permitem validar acesso a atributos sem mudar a interface pública; convenções sinalizam detalhes internos.", "Impeça que a vida do personagem seja alterada para um valor negativo.", "oop"),
 ("Associação, agregação e composição", "Essas relações descrevem como objetos colaboram e quem mantém o ciclo de vida de cada parte.", "Modele um personagem que equipa um item e explique a relação entre os objetos.", "oop"),
 ("Herança e super", "Herança permite especializar comportamento; super acessa funcionalidades da classe base em uma hierarquia.", "Crie uma classe Mago derivada de Personagem e especialize um método.", "oop"),
 ("Abstração, ABC e polimorfismo", "Classes abstratas definem contratos; polimorfismo permite usar implementações diferentes através de uma interface comum.", "Crie duas classes de arma com o mesmo método atacar.", "oop"),
 ("Exceções e métodos especiais", "Exceções próprias comunicam falhas de domínio; métodos especiais como __str__ e __repr__ adaptam objetos à linguagem.", "Crie uma exceção para equipamento incompatível e uma representação textual para personagem.", "oop"),
 ("Dataclasses e modelagem de domínio", "dataclasses reduzem código repetitivo em classes de dados, mantendo explícitos campos e valores padrão.", "Converta uma estrutura de inventário simples numa dataclass.", "oop"),
]),
("Os mecanismos ocultos: Python avançado", "Decoradores, context managers, tipagem, métodos mágicos e recursos avançados", "A criatura deste capítulo não ataca de frente: ela esconde efeitos colaterais e contratos implícitos. Você vai aprender a reconhecê-los, não a usá-los por ostentação.", [
 ("Dunder methods e representação", "Métodos especiais conectam objetos a operações da linguagem, como str, len, comparação e chamada.", "Adicione __str__ ou __repr__ a uma classe e teste a saída.", "advanced"),
 ("Decoradores de funções", "Um decorador recebe uma função e devolve outra função ou objeto chamável; pode adicionar comportamento sem alterar a chamada externa.", "Crie um decorador que registre início e fim de uma função.", "advanced"),
 ("Decoradores com parâmetros", "Um decorador parametrizado costuma ter uma camada externa que recebe opções e devolve o decorador real.", "Desenhe o fluxo de uma função decorada e explique cada nível de chamada.", "advanced"),
 ("Context managers", "O protocolo de contexto permite definir entrada e saída de um bloco with, inclusive a liberação de recursos.", "Crie ou use um context manager e verifique o fechamento em caso de exceção.", "advanced"),
 ("Metaclasses e criação de classes", "Metaclasses controlam como classes são construídas; são ferramentas avançadas e raramente necessárias para código comum.", "Explique em palavras a diferença entre classe, instância e tipo antes de experimentar metaclass.", "advanced"),
 ("Type hints e ferramentas de qualidade", "Anotações documentam tipos esperados e ajudam linters e analisadores estáticos; não garantem validação em runtime sozinhas.", "Adicione anotações às funções de um módulo e execute um linter ou checker se disponível.", "advanced"),
 ("Enums e tipos de domínio", "Enum representa um conjunto finito de valores nomeados, evitando strings mágicas e tornando as opções explícitas.", "Modele estados de uma missão usando Enum.", "advanced"),
 ("Iteráveis customizados", "Protocolos de iteração permitem que uma classe se comporte como sequência ou iterador quando isso tem utilidade.", "Implemente e teste um objeto simples iterável.", "advanced"),
]),
("A biblioteca da Cidade: módulos e arquivos", "Biblioteca padrão, datas, pastas, JSON, CSV, variáveis de ambiente e dependências", "A biblioteca da cidade foi saqueada e os registros se perderam. Cada arquivo recuperado ensina como programas conversam com o mundo exterior.", [
 ("if __name__ == '__main__'", "Esse guard separa código de execução direta de código importado por outro módulo.", "Crie um módulo que possa ser importado sem executar sua demonstração.", "modules"),
 ("datetime, timedelta e formatos", "datetime representa datas e horários; timedelta representa intervalos. Fuso e formato importam ao comparar registros.", "Calcule uma data de vencimento e formate-a para uma pessoa.", "modules"),
 ("os, shutil e pathlib", "Esses módulos ajudam a navegar, criar, copiar, mover e inspecionar arquivos e diretórios com cuidado.", "Escreva um script que liste os arquivos de uma pasta de teste.", "modules"),
 ("JSON: dump, load e serialização", "JSON representa estruturas em texto. dump/load trabalham com arquivos; dumps/loads trabalham com strings.", "Salve e recupere uma lista de tarefas em JSON.", "modules"),
 ("CSV e dados tabulares", "CSV armazena registros em linhas e campos separados; DictReader/DictWriter ajudam a trabalhar por nome de coluna.", "Leia um CSV de exemplo e produza um resumo de uma coluna.", "modules"),
 ("random, secrets e templates", "random serve para aleatoriedade não criptográfica; secrets é mais indicado para tokens e valores secretos.", "Gere uma amostra aleatória de teste e explique por que um token não deve usar random comum.", "modules"),
 ("Argumentos de linha de comando", "sys.argv e argparse permitem receber opções do terminal, validando entradas e documentando comandos.", "Crie um script com argumento de arquivo e opção --help.", "modules"),
 ("Pacotes, pip e requirements", "Pacotes organizam código; pip instala bibliotecas e o arquivo de dependências ajuda a reproduzir o ambiente.", "Prepare um requirements.txt mínimo para um projeto de teste.", "modules"),
 ("Arquivos temporários e ZIP", "Lidar com arquivos exige conhecer caminhos, permissões e limpeza. zipfile permite compactar e ler arquivos ZIP.", "Compacte uma pasta de teste e confira o conteúdo do arquivo criado.", "modules"),
]),
("O espelho de padrões: Regex", "Expressões regulares para localizar, validar, capturar e substituir texto", "Um mapa está escrito numa língua de símbolos. Não basta olhar a frase; você precisa reconhecer os padrões que a formam.", [
 ("Ler os metacaracteres", "Regex combina literais, classes, quantificadores e âncoras para descrever padrões de texto.", "Escreva padrões para reconhecer uma sequência de dígitos e um texto que começa com prefixo.", "regex"),
 ("Buscar e encontrar todas as ocorrências", "search encontra uma ocorrência, findall retorna correspondências e match verifica o início do texto.", "Compare as funções com uma frase que contém vários números.", "regex"),
 ("Grupos e capturas", "Grupos permitem extrair partes de uma correspondência, como códigos ou componentes de uma data.", "Extraia mês e ano de uma string de teste.", "regex"),
 ("Substituir e normalizar", "sub substitui padrões e pode normalizar dados antes de validações posteriores.", "Normalize espaços repetidos numa frase sem remover conteúdo relevante.", "regex"),
 ("Validar sem criar padrões impossíveis", "Uma regex muito permissiva aceita entradas erradas; uma excessivamente rígida rejeita dados válidos.", "Monte casos válidos, inválidos e de fronteira para um padrão.", "regex"),
]),
("O oráculo da confiança: testes e TDD", "Testes unitários, asserções, depuração e desenvolvimento orientado a testes", "A Névoa copia seus resultados e tenta convencer você de que tudo funciona. Só provas repetíveis conseguem separar sorte de confiabilidade.", [
 ("Por que testar", "Testes descrevem comportamento esperado e ajudam a detectar regressões quando o código muda.", "Escreva três casos de teste para uma função de desconto.", "tests"),
 ("assert e casos de fronteira", "Asserções comparam o esperado ao obtido. Casos de fronteira costumam revelar bugs invisíveis em exemplos simples.", "Teste zero, vazio, limite e entrada inválida quando fizer sentido.", "tests"),
 ("unittest e organização", "Um conjunto de testes agrupa verificações relacionadas e pode ser executado repetidamente.", "Crie uma classe de testes e rode as verificações pelo terminal.", "tests"),
 ("pytest e legibilidade", "Ferramentas como pytest simplificam a execução e a descoberta de testes; mantenha cada teste focado.", "Escreva testes com nomes que expressem a situação e o resultado esperado.", "tests"),
 ("Ciclo Red-Green-Refactor", "No TDD, escreva um teste que falha, faça-o passar com uma implementação mínima e refatore mantendo a suíte verde.", "Implemente uma função pequena seguindo as três etapas e registre o que mudou.", "tests"),
]),
("A oficina luminosa: PySide6", "Widgets, layouts, sinais e slots, janelas, formulários, eventos e threads", "A cidade volta a acender as janelas, mas cada uma precisa responder ao usuário. Um botão sem comportamento é só decoração.", [
 ("QApplication e janela", "Uma aplicação Qt inicia o loop de eventos e mantém a janela principal enquanto a interface está ativa.", "Crie uma janela mínima que abra e feche corretamente.", "gui"),
 ("Widgets e layouts", "Widgets são componentes de interface; layouts organizam tamanho e posicionamento conforme a janela muda.", "Monte uma janela com rótulo, campo e botão usando layout.", "gui"),
 ("Signals e slots", "Sinais anunciam eventos, como clique; slots são funções chamadas em resposta a eles.", "Conecte um botão a uma função que atualize um rótulo.", "gui"),
 ("Formulários e validação", "A interface deve validar entradas e mostrar mensagens claras sem travar o fluxo de uso.", "Faça um formulário aceitar apenas uma entrada esperada e explicar erros.", "gui"),
 ("Separar interface e lógica", "Manter cálculos fora dos widgets facilita testar regras sem abrir a janela.", "Mova uma operação para uma função independente e teste-a isoladamente.", "gui"),
 ("Eventos longos e threads", "Tarefas demoradas na thread principal congelam a interface; workers podem executar trabalho separado com comunicação segura.", "Desenhe o fluxo de uma tarefa longa e identifique o que deve rodar fora da GUI.", "gui"),
 ("Projeto de interface: calculadora", "Um projeto integrador exige layout consistente, entradas, operações, tratamento de erro e testes manuais.", "Monte a versão mínima de uma calculadora e teste divisão por zero e números negativos.", "project"),
]),
("A cripta dos dados: SQLite e MySQL", "Tabelas, consultas, CRUD, parâmetros seguros, cursores e modelagem relacional", "As memórias da cidade estão em cofres. Você aprenderá a registrar dados sem misturar comandos e entradas perigosas.", [
 ("Criar uma base SQLite", "SQLite armazena dados num arquivo local e é útil para começar a entender SQL e persistência.", "Crie uma base temporária e uma tabela de tarefas.", "database"),
 ("Tabelas, colunas e chaves", "Tabelas organizam registros; tipos e chaves devem refletir as regras dos dados.", "Modele uma tabela com chave primária e campos obrigatórios.", "database"),
 ("INSERT e placeholders", "INSERT adiciona linhas. Placeholders fazem o driver enviar valores como parâmetros em vez de concatená-los ao comando.", "Insira três registros usando parâmetros.", "database"),
 ("SELECT, WHERE e ordenação", "SELECT consulta dados; WHERE filtra; ORDER BY define a ordem apresentada.", "Liste registros filtrados e ordenados por uma coluna.", "sql"),
 ("UPDATE e DELETE com segurança", "UPDATE altera dados e DELETE remove linhas; confira a cláusula WHERE antes de confirmar alterações.", "Atualize e remova um único registro identificando-o pela chave.", "database"),
 ("CRUD completo com Python", "CRUD reúne criar, ler, atualizar e apagar; funções bem separadas tornam operações mais fáceis de testar.", "Implemente as quatro operações para um pequeno cadastro.", "database"),
 ("Conexões MySQL e credenciais", "Servidores MySQL usam conexão, cursor e credenciais; segredos devem ficar fora do repositório.", "Leia credenciais de variáveis de ambiente e nunca as grave em código público.", "database"),
 ("Transações e erros de banco", "Transações ajudam a manter alterações relacionadas consistentes; falhas devem levar a rollback quando apropriado.", "Simule uma operação que falha e explique como preservar a consistência.", "database"),
]),
("A primeira cidade web: Django básico", "Projeto, apps, URLs, views, templates, estáticos e fluxo request-response", "O próximo reino tem uma regra: cada pedido exige uma resposta clara. O Django divide esse caminho em peças que cooperam.", [
 ("Criar projeto e app Django", "Um projeto reúne configurações; apps agrupam funcionalidades. manage.py expõe comandos de administração.", "Crie um projeto mínimo e um app dedicado a uma funcionalidade.", "web"),
 ("URLs e views", "O URL dispatcher liga caminhos a views; uma view recebe uma requisição e retorna uma resposta.", "Crie uma rota que mostre uma página simples.", "web"),
 ("Templates e contexto", "Templates separam apresentação da lógica; o contexto transporta dados da view para a página.", "Renderize uma lista de itens usando um template.", "web"),
 ("Herança, includes e arquivos estáticos", "Templates-base evitam repetição; includes reutilizam trechos e arquivos estáticos guardam CSS, JS e imagens.", "Crie uma base com cabeçalho comum e uma folha CSS própria.", "web"),
 ("URLs dinâmicas e erros", "Parâmetros de rota identificam recursos. Erros 404 devem representar recursos inexistentes sem exibir informação sensível.", "Crie uma rota de detalhe e teste um identificador inexistente.", "web"),
]),
("A agenda perdida: projeto Django", "Models, migrations, admin, relacionamentos, listagem, busca e CRUD", "Íria encontra um livro de contatos apagado. Não basta exibir uma página: agora o aplicativo precisa preservar registros ao fechar.", [
 ("Models e migrations", "Models descrevem dados; migrations versionam alterações de esquema e são aplicadas ao banco.", "Crie um model Contact e aplique as migrações.", "database"),
 ("Área administrativa", "O admin do Django oferece uma interface rápida de gestão interna, que pode ser personalizada.", "Registre seu model no admin e configure colunas e busca.", "web"),
 ("QuerySets: filtrar e ordenar", "QuerySets representam consultas; filter e order_by permitem recuperar subconjuntos de registros.", "Liste contatos por nome e filtre uma pesquisa.", "database"),
 ("Criar formulários e validar campos", "Formulários validam dados recebidos; validação deve acontecer no servidor mesmo quando a interface também valida.", "Crie um formulário e apresente erros sem descartar entradas válidas.", "web"),
 ("Atualizar e excluir registros", "Um CRUD completo precisa identificar o recurso, confirmar ações destrutivas e preservar integridade.", "Implemente edição e exclusão de um contato de teste.", "database"),
 ("Uploads e relacionamentos", "Arquivos enviados exigem validação e configuração; chaves estrangeiras representam relações entre entidades.", "Modele categorias de contatos com ForeignKey e descreva limites de upload.", "web"),
]),
("Identidade e acesso: Django seguro", "Autenticação, formulários, sessão, mensagens, permissões e CSRF", "A agenda agora contém informações pessoais. Um sistema útil não pode permitir que qualquer visitante altere os dados de outra pessoa.", [
 ("Autenticação e sessão", "Autenticar identifica o usuário; sessões mantêm o estado de login entre requisições conforme as configurações.", "Descreva o fluxo de login e logout e teste os dois caminhos.", "web"),
 ("Criar usuário e validar dados", "Cadastro precisa validar campos e usar os mecanismos de autenticação fornecidos pelo framework.", "Liste os campos que devem ser validados antes de criar conta.", "web"),
 ("login_required e autorização", "Estar autenticado não significa poder acessar todo recurso; autorização deve verificar a relação do usuário com o dado.", "Garanta conceitualmente que somente o proprietário atualize um contato.", "web"),
 ("Proteção CSRF e mensagens", "Tokens CSRF ajudam a defender formulários; mensagens dão feedback após ações sem expor detalhes internos.", "Verifique o token nos formulários e escreva mensagens amigáveis de sucesso e falha.", "web"),
]),
("A linguagem da fachada: HTML e CSS", "Estrutura semântica, formulários, seletores, caixas, layout e responsividade", "Do lado de fora, a cidade parece quebrada. Você descobre que estrutura e apresentação são responsabilidades diferentes, e que essa separação torna mudanças menos perigosas.", [
 ("HTML semântico", "Elementos semânticos dão significado ao conteúdo e ajudam acessibilidade, manutenção e ferramentas de leitura.", "Crie uma página com header, main, section, listas e links apropriados.", "htmlcss"),
 ("Links, imagens e formulários", "Formulários precisam de labels e controles identificados; imagens informativas precisam de texto alternativo relevante.", "Construa um formulário simples com label associado a cada campo.", "htmlcss"),
 ("Seletores CSS e cascata", "Seletores escolhem elementos; cascata, especificidade e herança determinam qual estilo prevalece.", "Crie estilos para títulos, botões e estados de foco.", "htmlcss"),
 ("Box model e espaçamento", "Conteúdo, padding, borda e margem afetam as dimensões e o espaço entre elementos.", "Use o inspetor do navegador para explicar por que um elemento está desalinhado.", "htmlcss"),
 ("Flexbox, Grid e responsividade", "Flexbox ajuda a organizar um eixo e Grid organiza linhas e colunas; media queries adaptam a interface a larguras diferentes.", "Faça um layout de cartões passar de duas colunas para uma em tela estreita.", "htmlcss"),
]),
("O livro de consultas: SQL", "SELECT, filtros, ordenação, agregação, JOINs, chaves e alterações seguras", "Os registros estão separados em tabelas. Você precisa reunir as peças sem contar histórias que os dados não sustentam.", [
 ("SELECT e projeção de colunas", "Selecione apenas as colunas necessárias para que a consulta seja clara e eficiente.", "Escreva uma consulta que retorne só dois campos de uma tabela.", "sql"),
 ("WHERE, AND, OR e LIKE", "Filtros combinam comparações e padrões textuais; parênteses deixam explícita a precedência lógica.", "Monte uma consulta com dois critérios e explique os parênteses usados.", "sql"),
 ("ORDER BY e LIMIT", "Ordenar e limitar resultados ajuda a analisar conjuntos grandes com uma saída controlada.", "Liste os cinco registros mais recentes conforme uma coluna de data.", "sql"),
 ("GROUP BY e agregações", "COUNT, SUM, AVG, MIN e MAX resumem grupos; HAVING filtra grupos agregados.", "Calcule a quantidade de registros por categoria.", "sql"),
 ("JOINs e chaves", "JOIN combina linhas relacionadas por uma condição de junção; chaves evitam relações ambíguas.", "Junte uma tabela de contatos e outra de categorias.", "sql"),
 ("Transações e SQL injection", "Comandos de alteração devem ser deliberados; parâmetros e transações ajudam a proteger integridade e entradas externas.", "Revise uma query concatenada e reescreva-a com placeholders.", "database"),
]),
("O observatório da automação", "Requests, BeautifulSoup, Selenium, subprocess, notebooks e bibliotecas auxiliares", "O trabalho manual se repete pela cidade. O desafio é automatizar com responsabilidade: respeitando limites, falhas e regras dos sistemas acessados.", [
 ("HTTP e requests", "Requests envia solicitações HTTP e permite inspecionar status, cabeçalhos e conteúdo retornado.", "Consuma um endpoint público de teste e trate status de erro.", "web"),
 ("BeautifulSoup e extração", "Um parser HTML permite localizar elementos e extrair texto sem depender de índices frágeis.", "Analise um HTML local e extraia títulos e links.", "automation"),
 ("Selenium e seletores", "Selenium automatiza navegador; seletores e esperas explícitas tornam o fluxo mais robusto.", "Automatize uma interação num site de teste autorizado.", "automation"),
 ("Esperas e falhas em navegador", "Páginas dinâmicas podem carregar em tempos diferentes; capturar screenshots e registrar erros ajuda a depurar.", "Identifique uma espera explícita e um ponto de falha possível.", "automation"),
 ("Subprocess e comandos externos", "subprocess executa processos externos; evite shell desnecessário e valide argumentos quando há entrada externa.", "Execute um comando inofensivo capturando código de saída.", "automation"),
 ("Threads e tarefas demoradas", "Concorrência exige planejar compartilhamento de estado, cancelamento e erros de worker.", "Desenhe como um worker informaria conclusão sem travar a interface.", "automation"),
 ("PDF, imagens e Excel", "Bibliotecas como PyPDF2, Pillow e openpyxl automatizam documentos, imagens e planilhas com validação de arquivos.", "Escolha uma pequena tarefa com arquivo de teste e documente a biblioteca necessária.", "automation"),
]),
("O servidor e suas rotas: HTTP e APIs", "Request-response, status codes, JSON, endpoints, autenticação e erros", "A última ponte depende de mensagens entre sistemas. Cada pedido precisa de um contrato claro, e cada erro precisa ser interpretável.", [
 ("Métodos HTTP e status codes", "Métodos comunicam intenção; códigos de status indicam sucesso, redirecionamento, erro do cliente ou do servidor.", "Classifique cenários de consulta, criação e recurso inexistente por método/status.", "web"),
 ("JSON como formato de troca", "JSON representa objetos e listas em texto, mas os tipos precisam ser validados ao entrar no sistema.", "Transforme um dicionário em JSON e recupere-o novamente.", "modules"),
 ("Desenhar endpoints úteis", "Um endpoint deve representar um recurso ou operação com contrato, dados de entrada e resposta documentados.", "Escreva o contrato de uma rota para listar e criar tarefas.", "web"),
 ("Tratar falhas e dados externos", "Não presuma que uma resposta externa sempre vem válida; valide status, estrutura e tipos antes de usar seus dados.", "Crie uma tabela de erro de rede, status inesperado e JSON inválido.", "web"),
]),
("Os padrões dos antigos mestres", "Princípios de design, SOLID introdutório e padrões de criação, estrutura e comportamento", "Os mestres antigos deixaram diagramas, não leis sagradas. O valor do padrão aparece quando simplifica um problema real.", [
 ("Reconhecer problemas de design", "Antes de aplicar um padrão, descreva o problema: repetição, dependência excessiva, criação complexa ou responsabilidades misturadas.", "Encontre um ponto de acoplamento numa aplicação pequena e proponha uma separação.", "patterns"),
 ("Responsabilidade única e interfaces", "Separar responsabilidades ajuda cada componente a mudar por um motivo claro; contratos estreitos facilitam substituição e teste.", "Divida leitura de arquivo e regra de negócio em funções diferentes.", "patterns"),
 ("Strategy e Factory", "Strategy troca um algoritmo através de uma interface; Factory centraliza a criação quando a construção precisa ser desacoplada.", "Imagine dois métodos de cálculo de frete e decida se uma Strategy ajudaria.", "patterns"),
 ("Adapter, Decorator e Observer", "Esses padrões adaptam interfaces, acrescentam comportamento ou notificam dependentes; não devem ser usados só por moda.", "Escolha qual padrão se encaixaria em um caso e justifique por escrito.", "patterns"),
 ("Revisar a implementação", "Um padrão só vale quando melhora entendimento, flexibilidade ou teste frente à alternativa simples.", "Compare uma solução simples e outra com padrão; escolha a mais legível para o caso.", "patterns"),
]),
("A última subida: publicação e ambiente", "Git, configuração, dependências, Linux/WSL, logs, documentação e entrega", "A aplicação funciona na sua máquina, mas a cidade inteira ainda não consegue usá-la. A última subida é tornar a execução reproduzível.", [
 ("Versionar com Git", "Commits pequenos e mensagens objetivas ajudam a rastrear mudanças e recuperar versões.", "Faça um commit com uma mudança isolada e descreva o motivo.", "modules"),
 ("Não versionar segredos", "Tokens, senhas e arquivos pessoais não devem entrar no repositório; use variáveis de ambiente e ignore arquivos locais.", "Revise os arquivos rastreados e identifique algo que não deveria ser publicado.", "modules"),
 ("Configuração por ambiente", "Desenvolvimento e produção podem usar bancos e parâmetros diferentes; centralize configurações sem embutir segredos.", "Crie uma lista de variáveis de ambiente documentadas sem valores secretos.", "modules"),
 ("Logs e diagnóstico", "Logs relevantes registram contexto de falhas sem expor dados sensíveis; diagnósticos devem ser reproduzíveis.", "Escreva o que registrar quando uma operação de importação falhar.", "tests"),
 ("Instalação e execução reproduzível", "Uma entrega precisa informar dependências, comandos, configuração e passos para validar uma instalação limpa.", "Escreva instruções de instalação para alguém que nunca viu o projeto.", "project"),
]),
("O último tomo: projeto e portfólio", "Requisitos, arquitetura simples, implementação incremental, testes, documentação e apresentação", "O Rei da Última Página aguarda. Não basta chegar ao fim dos tópicos: você precisa mostrar que consegue construir, explicar e revisar algo seu.", [
 ("Escolher um problema real", "Um bom projeto de portfólio resolve um problema delimitado e pode ser explicado com clareza.", "Escreva uma frase para o problema, público e resultado esperado do projeto.", "project"),
 ("Definir requisitos mínimos", "Requisitos observáveis permitem decidir quando uma funcionalidade está concluída e como testá-la.", "Escreva cinco critérios de aceitação objetivos.", "project"),
 ("Implementar em pequenos incrementos", "Um incremento útil deve poder ser executado e conferido antes de adicionar novas camadas.", "Divida uma funcionalidade em três entregas pequenas e ordenadas.", "project"),
 ("Testar, corrigir e refatorar", "A revisão final procura comportamentos errados, nomes confusos, duplicação e caminhos não testados.", "Faça uma revisão de código e registre três melhorias justificadas.", "tests"),
 ("Documentar e demonstrar", "O portfólio precisa explicar problema, tecnologias, configuração, execução, testes e limitações honestas.", "Prepare um README e um roteiro de demonstração de dois minutos.", "project"),
]),
]

CAIXA_CHAPTERS = [
("Língua Portuguesa", "Interpretação, gramática aplicada, coesão e redação oficial", "O Arquivo dos Ecos protege a primeira chave: compreender com precisão antes de responder.", [
 ("Compreensão literal e inferência", "Separe informação explícita, pressuposto e inferência. A alternativa correta precisa ser sustentada pelo texto.", "Leia um texto curto, resuma a tese e marque uma inferência que não pode ser provada.", "portuguese"),
 ("Argumentação e persuasão", "Identifique tese, argumentos, evidências, contra-argumentos e estratégia de persuasão.", "Reconstrua o argumento principal de um texto em três frases.", "portuguese"),
 ("Comunicação objetiva e organização textual", "Linguagem clara, concisa e organizada reduz ambiguidade em textos formais.", "Reescreva um parágrafo redundante preservando a informação.", "portuguese"),
 ("Coesão, coerência e tipologia", "Coesão conecta partes por mecanismos linguísticos; coerência mantém sentido; tipologia ajuda a reconhecer a organização do texto.", "Identifique conectores e explique a relação lógica que cada um expressa.", "portuguese"),
 ("Ortografia, acentuação e acordo ortográfico", "Regras oficiais precisam ser dominadas em uso contextual, incluindo casos frequentes de acentuação e grafia.", "Crie uma lista própria de erros recorrentes e revise-a sem consulta.", "portuguese"),
 ("Crase, sintaxe e pontuação", "Crase depende de contexto sintático; pontuação e estrutura da oração podem alterar relações e sentidos.", "Analise cinco frases e justifique o uso ou ausência de crase.", "portuguese"),
 ("Concordância e regência", "Concordância relaciona termos; regência define relações exigidas por verbos e nomes.", "Corrija frases com desvios e explique a regra aplicada.", "portuguese"),
 ("Semântica e colocação pronominal", "Sentido depende de contexto; colocação pronominal segue fatores sintáticos e registros formais.", "Explique como uma troca de palavra ou pronome altera o enunciado.", "portuguese"),
 ("Redação oficial", "Textos oficiais devem prezar por clareza, impessoalidade, concisão e estrutura adequada à finalidade.", "Escreva um parágrafo formal e revise clareza e tratamento do destinatário.", "portuguese"),
]),
("Língua Inglesa", "Vocabulário e gramática básica para compreensão de textos", "A próxima chave está numa língua diferente. Você não precisa traduzir tudo: precisa identificar estrutura, contexto e ideia central.", [
 ("Skimming e scanning", "Skimming busca a ideia geral; scanning procura informação específica, nomes, números ou datas.", "Leia título e primeiro parágrafo para inferir tema, depois localize um dado solicitado.", "english"),
 ("Cognatos e falsos cognatos", "Cognatos ajudam a inferir significado, mas falsos cognatos podem induzir a erros.", "Monte cinco pares de cognatos e falsos cognatos encontrados em textos.", "english"),
 ("Pronomes, artigos e preposições", "Palavras funcionais indicam referência, quantidade e relação; seu sentido deve ser lido no contexto.", "Identifique referências pronominais em dois parágrafos.", "english"),
 ("Tempos verbais e conectores básicos", "Tempos e conectores sinalizam tempo, causa, contraste e consequência.", "Marque verbos e conectores numa notícia curta e explique a relação temporal.", "english"),
 ("Vocabulário bancário e inferência", "Termos do domínio financeiro podem ser inferidos pelo contexto, cognatos e exemplos próximos.", "Leia um pequeno texto financeiro e escreva a ideia central em português.", "english"),
]),
("Matemática Financeira", "Juros, valor do dinheiro, séries, equivalência, amortização e descontos", "A Câmara dos Números pune quem troca intuição por cálculo. Você vai registrar capital, taxa, prazo e regime antes de escolher uma fórmula.", [
 ("Valor do dinheiro no tempo", "Capital, taxa, prazo, valor presente e futuro descrevem partes diferentes de uma operação financeira.", "Liste os dados e a incógnita em três enunciados financeiros.", "finance"),
 ("Juros simples", "J = C × i × t quando taxa e prazo usam a mesma unidade e a base é o capital inicial.", "Resolva dois exercícios mudando taxa e prazo, sempre convertendo unidades.", "finance"),
 ("Juros compostos", "No regime composto, cada período capitaliza sobre o montante anterior: M = C(1+i)^t.", "Compare o montante de uma aplicação em juros simples e compostos.", "finance"),
 ("Taxas e períodos", "A taxa deve ser compatível com o período; equivalência de taxas requer a transformação adequada ao regime.", "Converta uma taxa nominal de período para o prazo indicado no enunciado.", "finance"),
 ("Séries uniformes e equivalência", "Fluxos regulares podem ser comparados por valor presente/futuro conforme taxa e datas.", "Desenhe uma linha do tempo de pagamentos antes de calcular.", "finance"),
 ("SAC e sistema Price", "No SAC, amortização é constante; no Price, prestações tendem a ser constantes em condições padronizadas, com composição variável.", "Monte uma pequena tabela ilustrativa comparando amortização e juros nos dois sistemas.", "finance"),
 ("Descontos", "Desconto comercial simples e racional composto usam relações distintas entre valor nominal, taxa e prazo.", "Identifique qual regime o enunciado pede antes de substituir os valores.", "finance"),
 ("Sequências, PA e PG", "PA tem diferença constante; PG tem razão constante. Leis de formação podem ser gerais ou recursivas.", "Encontre o próximo termo e a regra de duas sequências diferentes.", "finance"),
]),
("Probabilidade e Estatística", "Dados, gráficos, tendência central, dispersão e probabilidades", "O Cartógrafo exige que você leia os dados em vez de escolher a resposta que parece mais intuitiva.", [
 ("Variáveis, população e amostra", "Variável é a característica observada; população é o conjunto de interesse; amostra é a parte observada.", "Classifique variáveis e descreva população e amostra num cenário de clientes.", "statistics"),
 ("Frequências e representações", "Frequências absolutas e relativas resumem contagens; gráficos adequados facilitam comparações sem distorcer a escala.", "Construa uma tabela de frequência e escolha um gráfico apropriado.", "statistics"),
 ("Média, moda e mediana", "Medidas de tendência central resumem dados de modos diferentes e reagem de forma distinta a valores extremos.", "Calcule média, moda e mediana de uma amostra curta e compare-as.", "statistics"),
 ("Média ponderada e geométrica", "A ponderação dá pesos diferentes a observações; média geométrica é adequada a certas taxas multiplicativas.", "Resolva um exemplo de média ponderada indicando o peso de cada componente.", "statistics"),
 ("Quartis e percentis", "Medidas de posição localizam valores relativos dentro dos dados ordenados.", "Explique em palavras o que representa o percentil 80.", "statistics"),
 ("Variância, desvio padrão e amplitude", "Medidas de dispersão descrevem variabilidade; confirme se a fórmula usa população ou amostra.", "Compare dois conjuntos com mesma média e dispersões diferentes.", "statistics"),
 ("Probabilidade e eventos", "O espaço amostral descreve resultados possíveis; probabilidade de Laplace pressupõe casos equiprováveis.", "Desenhe o espaço amostral de um experimento simples.", "statistics"),
 ("Probabilidade condicional e binomial", "A probabilidade condicional restringe o espaço aos eventos informados; binomial modela contagens de sucessos sob premissas específicas.", "Resolva um problema simples e explicite as hipóteses usadas.", "statistics"),
]),
("Ética e Compliance", "Ética profissional, prevenção a ilícitos, sigilo, privacidade e governança", "O próximo guardião oferece atalhos tentadores. Você avançará se conseguir identificar deveres, riscos e limites de atuação.", [
 ("Ética e conduta profissional", "Ética envolve respeito, responsabilidade e decisões coerentes com normas e valores organizacionais.", "Analise um dilema de atendimento e liste as condutas adequadas.", "ethics"),
 ("Prevenção à lavagem de dinheiro", "Controles de prevenção identificam e comunicam operações suspeitas pelos canais apropriados; não se deve alertar indevidamente pessoas investigadas.", "Descreva sinais de alerta e por que a equipe deve seguir o procedimento oficial.", "ethics"),
 ("Assédio moral e sexual", "É necessário reconhecer comportamentos abusivos, prevenir retaliação e utilizar canais apropriados de orientação/denúncia.", "Diferencie conflito pontual de padrão abusivo, considerando contexto e conduta.", "ethics"),
 ("Segurança da informação", "Confidencialidade, integridade e disponibilidade orientam controles como autenticação, menor privilégio e resposta a incidentes.", "Classifique três riscos e indique um controle preventivo para cada um.", "ethics"),
 ("Princípios do art. 37", "Legalidade, impessoalidade, moralidade, publicidade e eficiência são os princípios expressos conhecidos como LIMPE.", "Associe uma situação hipotética a cada princípio.", "ethics"),
 ("Sigilo bancário e LGPD", "Sigilo e proteção de dados limitam acesso, uso e divulgação de informações segundo bases e hipóteses aplicáveis.", "Avalie quem deveria acessar um dado de cliente e para qual finalidade.", "ethics"),
 ("Anticorrupção e governança", "Programas de integridade combinam prevenção, detecção, canais de relato, investigação e resposta proporcional.", "Descreva como registrar um conflito de interesses sem omitir informações relevantes.", "ethics"),
 ("Responsabilidade socioambiental", "Políticas socioambientais e governança conectam decisões organizacionais a impactos, riscos e prestação de contas.", "Identifique indicadores que ajudariam a avaliar uma prática sustentável.", "ethics"),
]),
("Conhecimentos Bancários", "Sistema Financeiro Nacional, mercados, produtos, moeda, políticas e serviços", "O Cofre Central abre em camadas: instituição, mercado, produto e operação. Cada etapa usa o vocabulário financeiro do edital.", [
 ("Estatuto da CAIXA e papel institucional", "Estude a natureza, a missão e as competências descritas no estatuto da instituição, conferindo a versão oficial aplicável.", "Faça uma ficha de revisão com missão, funções e pontos do estatuto previstos no material.", "banking"),
 ("Estrutura do Sistema Financeiro Nacional", "O SFN envolve órgãos normativos, supervisores, executores e operadores, com atribuições distintas.", "Desenhe um mapa relacionando os principais participantes e suas funções.", "banking"),
 ("Mercados monetário, de crédito, capitais e câmbio", "Os mercados se distinguem por finalidade, instrumentos e participantes; não trate os termos como sinônimos.", "Classifique quatro operações hipotéticas conforme o mercado predominante.", "banking"),
 ("Bancos digitais, fintechs e shadow banking", "Modelos digitais e novos participantes mudam distribuição de serviços, competição e riscos; regulação e atividade importam.", "Compare banco tradicional e fintech por serviço, infraestrutura e risco.", "banking"),
 ("PIX, internet banking e mobile banking", "Canais e meios de pagamento têm características, regras e riscos próprios; segurança faz parte do serviço.", "Monte uma tabela com uso, vantagem e cuidado de segurança de cada canal.", "banking"),
 ("Open Finance, blockchain e Drex", "Compartilhamento de dados, registros distribuídos e moeda digital de banco central são temas distintos e sujeitos a regras específicas.", "Explique em três frases a diferença entre PIX, Open Finance e blockchain.", "banking"),
 ("Moeda, política monetária e SELIC", "Taxas básicas, operações compromissadas e instrumentos monetários influenciam condições financeiras e custo do crédito.", "Explique uma possível cadeia entre mudança de juros e custo de financiamento.", "banking"),
 ("Orçamento público, títulos e dívida", "Orçamento, títulos do Tesouro e dívida pública se relacionam ao financiamento e à gestão de recursos do setor público.", "Distinga título público, orçamento e dívida em suas próprias palavras.", "banking"),
 ("Produtos bancários e benefícios", "Contas, cartões, crédito, poupança, capitalização, previdência, consórcio, investimentos e seguros têm características e riscos diferentes.", "Compare três produtos por objetivo, liquidez, risco e custo.", "banking"),
 ("Mercado de capitais e câmbio", "Operações cambiais envolvem instituições autorizadas, taxas e fluxos de capitais; juros e risco afetam preços e decisões.", "Explique como uma variação cambial pode afetar importador e exportador.", "banking"),
 ("Tesouraria e mercado interbancário", "Operações de tesouraria e interbancárias apoiam gestão de liquidez, funding e posicionamento financeiro.", "Faça um glossário com os termos de mercado citados no material didático.", "banking"),
 ("Garantias e autorregulação", "Aval, fiança, penhor, alienação fiduciária e hipoteca são instrumentos distintos; autorregulação complementa regras aplicáveis.", "Associe garantias aos bens/direitos envolvidos e identifique diferenças.", "banking"),
 ("FGTS, PIS e benefícios do trabalhador", "Estude regras, beneficiários, critérios e documentos com base na legislação indicada e em fontes oficiais atualizadas.", "Faça uma tabela benefício, finalidade e condição geral indicada no edital.", "banking"),
 ("Contas, capacidade civil e atendimento", "Abertura e movimentação de contas dependem de identificação, capacidade, representação e documentação adequadas.", "Resolva um caso hipotético identificando dados que precisam ser verificados.", "banking"),
 ("Estratégia, CRM e qualidade de serviços", "Segmentação, posicionamento, gestão de relacionamento e qualidade ajudam a analisar necessidades sem perder integridade no atendimento.", "Desenhe uma jornada do cliente e identifique um ponto de melhoria.", "banking"),
]),
("Tecnologia da Informação e Comunicação", "Office, arquivos, redes, navegadores, colaboração, IA, nuvem e inovação", "O terminal de comunicação está cheio de sinais. Para atravessá-lo, você precisa dominar ferramentas e reconhecer riscos digitais.", [
 ("Word, Excel, PowerPoint e Outlook", "Ferramentas de produtividade têm finalidades distintas e recursos para editar documentos, planilhas, apresentações e correio.", "Liste a ferramenta adequada para quatro tarefas administrativas.", "it"),
 ("Arquivos, pastas e programas", "Organização de arquivos exige nomes claros, hierarquia, extensões compreendidas e cuidado com anexos inesperados.", "Crie uma estrutura de pastas coerente para um projeto e explique as regras.", "it"),
 ("Redes, internet e intranet", "Redes conectam equipamentos; internet e intranet diferem no alcance e no controle de acesso.", "Explique a diferença usando um exemplo de serviço público interno e outro público.", "it"),
 ("Navegadores, pesquisa e e-mail", "Pesquisa eficiente avalia termos, fontes e resultados; e-mail precisa de destinatários corretos e cautela com links/anexos.", "Identifique sinais de phishing numa mensagem hipotética.", "it"),
 ("Segurança e normas de gestão", "Políticas, controles e gestão de risco ajudam a proteger informação; conheça o propósito geral das normas citadas no edital.", "Relacione um risco de informação com prevenção, detecção e resposta.", "it"),
 ("Redes sociais e colaboração remota", "Cada ferramenta tem públicos e funções diferentes; colaboração remota exige comunicação, controle de acesso e registro adequado.", "Escolha um canal apropriado para três tipos de comunicação profissional.", "it"),
 ("BI, multimídia e ferramentas de reunião", "BI organiza dados para apoiar decisões; ferramentas multimídia e de reunião apoiam consumo e trabalho colaborativo.", "Desenhe um fluxo básico de dados até um painel de decisão.", "it"),
 ("IA, analytics, blockchain e nuvem", "Essas tecnologias têm propósitos distintos. Avalie finalidade, riscos, privacidade e limitações antes de sugerir uso.", "Compare dois conceitos e dê um exemplo de uso responsável de cada um.", "it"),
 ("Transformação digital e Open Finance", "Transformação digital combina processo, pessoas, tecnologia e governança; Open Finance segue regras próprias de compartilhamento.", "Descreva um serviço digital e os dados/consentimentos necessários.", "it"),
]),
("Conhecimentos e Comportamentos Digitais", "Mentalidade de crescimento, métodos ágeis, dados, liderança e produtividade", "A Câmara da Mudança só se abre para quem aprende a aprender, coopera e transforma problemas complexos em passos executáveis.", [
 ("Mentalidade de crescimento", "Erros são dados para ajustar estratégias; mentalidade de crescimento não significa ignorar limites ou dispensar feedback.", "Registre um erro recente, sua causa provável e uma próxima ação.", "digital"),
 ("Intraempreendedorismo e design thinking", "Iniciativas internas partem de problemas reais; design thinking explora necessidades, gera hipóteses, prototipa e testa.", "Descreva uma necessidade do usuário antes de propor uma solução.", "digital"),
 ("Ágil, Scrum e Lean", "Métodos ágeis dão ênfase a entregas incrementais e feedback; Scrum organiza responsabilidades, eventos e artefatos.", "Desenhe um pequeno ciclo de trabalho com objetivo, entrega e retrospectiva.", "digital"),
 ("Problemas complexos e pensamento sistêmico", "Pensamento sistêmico procura relações, causas e efeitos entre partes em vez de tratar sintomas isoladamente.", "Faça um diagrama de causa e efeito de um problema operacional.", "digital"),
 ("Ciência de dados e análise de negócios", "Dados exigem pergunta clara, qualidade, análise e interpretação alinhada à decisão pretendida.", "Defina uma pergunta de negócio e quais dados ajudariam a respondê-la.", "digital"),
 ("Colaboração, liderança e inteligência emocional", "Autoliderança e colaboração incluem escuta, feedback, adaptação e gestão construtiva de conflitos.", "Descreva como conduzir uma discordância sem perder o objetivo comum.", "digital"),
 ("CX, OKR e produtividade", "Experiência do consumidor observa a jornada; OKRs ligam objetivos a resultados-chave verificáveis; gestão do tempo exige prioridade.", "Defina um objetivo e dois resultados mensuráveis para melhorar uma jornada.", "digital"),
 ("Sustentabilidade e aprendizagem contínua", "ODS, trabalho remoto e aprendizagem ao longo da vida pedem responsabilidade, autonomia e revisão periódica de hábitos.", "Monte um plano de aprendizagem com revisão semanal e indicador de constância.", "digital"),
]),
("Atendimento Bancário", "Experiência, vendas éticas, canais, negociação, proteção do consumidor e inclusão", "A última chave antes do cofre central não responde à pressa. Ela exige escuta, comunicação acessível e solução adequada à necessidade real.", [
 ("Valor percebido e experiência do cliente", "Experiência se forma em todos os pontos de contato; reduzir atrito e cumprir o combinado contribui para confiança.", "Mapeie cinco etapas da jornada de um cliente e um atrito possível.", "service"),
 ("Pré-abordagem, venda e pós-venda", "Uma venda ética entende a necessidade, apresenta opções adequadas, esclarece custos e acompanha a experiência.", "Simule perguntas de descoberta sem presumir o que o cliente precisa.", "service"),
 ("Marketing digital e gatilhos mentais", "Leads, copywriting e inbound marketing devem comunicar valor sem enganar ou pressionar indevidamente.", "Reescreva uma mensagem comercial para torná-la clara e verificável.", "service"),
 ("Escuta ativa e negociação", "Escuta empática confirma o problema antes da resposta; negociação procura alternativas sem prometer o que não pode cumprir.", "Resuma uma reclamação fictícia e proponha duas soluções realistas.", "service"),
 ("Canais remotos e ouvidoria", "Canais devem manter identificação, registro, acessibilidade e encaminhamento adequado; ouvidoria tem papel próprio.", "Diferencie atendimento inicial, reclamação e demanda de ouvidoria.", "service"),
 ("CDC e relacionamento com cliente", "Regras de proteção e relacionamento sustentam informação clara, tratamento adequado e resposta a problemas.", "Identifique informações que precisam ser apresentadas antes de contratar um produto.", "service"),
 ("Diversidade, inclusão e prioridade", "Atendimento acessível respeita direitos e normas, evitando suposições e barreiras desnecessárias.", "Planeje atendimento inclusivo num cenário com necessidade de acessibilidade.", "service"),
 ("Qualidade, segmentação e CRM", "CRM organiza o relacionamento; indicadores de qualidade devem ser interpretados com foco no resultado para o cliente.", "Proponha uma métrica de qualidade e uma salvaguarda contra incentivo inadequado.", "service"),
]),
("Redação: a última prova", "Planejar, argumentar, estruturar, revisar e respeitar o tema", "A última ponte é feita de palavras. O examinador não pode adivinhar uma boa ideia que não foi organizada no papel.", [
 ("Interpretar o comando da proposta", "Antes de escrever, identifique tema, recorte, gênero e o que precisa ser defendido ou discutido.", "Transforme uma proposta em pergunta central e liste o que ela exige.", "portuguese"),
 ("Tese e plano de argumentos", "A tese responde ao problema; cada argumento deve sustentá-la com explicação, exemplo ou evidência pertinente.", "Escreva uma tese e dois tópicos frasais que a sustentem.", "portuguese"),
 ("Introdução, desenvolvimento e conclusão", "Parágrafos devem ter função clara e se conectar por progressão lógica; conclusão não deve introduzir argumento solto.", "Monte um esqueleto de quatro parágrafos antes de redigir.", "portuguese"),
 ("Coesão, clareza e revisão final", "Revisar inclui conferir aderência ao tema, coerência, pontuação, concordância, repetição e legibilidade.", "Revise um texto próprio e registre três mudanças justificadas.", "portuguese"),
]),
]

CAIXA_BANKS = {
"portuguese": [
 Q("Português", "Ao responder uma questão de interpretação, qual critério é central?", ["Escolher a opinião mais popular", "Sustentar a resposta no texto e nas inferências permitidas", "Usar só conhecimento externo", "Escolher a alternativa mais longa"], 1, "A resposta precisa ter apoio textual."),
 Q("Português", "Coesão textual trata principalmente de…", ["Conexões linguísticas entre partes do texto", "Somente ortografia", "A velocidade de leitura", "O tamanho da página"], 0, "Conectores, referências e substituições ajudam a conectar partes."),
 Q("Português", "Em redação oficial, uma diretriz importante é…", ["Clareza e concisão", "Ambiguidade deliberada", "Excesso de ornamentação", "Uso obrigatório de gírias"], 0, "A comunicação oficial deve priorizar clareza, concisão e adequação."),
 Q("Português", "Antes de usar uma regra de crase, convém analisar…", ["A relação sintática e a regência no contexto", "Apenas o tamanho da palavra", "A cor do parágrafo", "O número de linhas"], 0, "A ocorrência de crase depende da estrutura sintática e do contexto."),
 Q("Português", "Qual prática melhora uma dissertação?", ["Definir tese e organizar argumentos", "Repetir a mesma frase", "Ignorar o comando", "Introduzir temas sem conexão"], 0, "Tese e progressão argumentativa dão unidade ao texto."),
],
"english": [
 Q("Inglês", "A técnica de skimming é usada para…", ["Entender a ideia geral rapidamente", "Traduzir cada palavra", "Memorizar verbos isolados", "Contar letras"], 0, "Skimming prioriza o sentido geral do texto."),
 Q("Inglês", "Um falso cognato é uma palavra que…", ["Parece familiar, mas pode ter significado diferente", "Sempre significa exatamente o mesmo", "Não tem relação com vocabulário", "Só existe em contratos"], 0, "Falsos cognatos podem induzir a traduções incorretas."),
 Q("Inglês", "Ao inferir uma palavra desconhecida, o melhor é…", ["Combinar contexto, estrutura e pistas próximas", "Ignorar a frase inteira", "Escolher aleatoriamente", "Assumir que todo cognato está correto"], 0, "O contexto sustenta inferências mais confiáveis."),
 Q("Inglês", "Scanning procura…", ["Uma informação específica", "A estrutura de todo o idioma", "A opinião do leitor", "Só a primeira palavra"], 0, "Scanning localiza dados como nomes, datas e números."),
],
"finance": [
 Q("Matemática Financeira", "Em juros simples, o juro incide sobre…", ["O capital inicial", "Todo montante passado a cada período", "Apenas a inflação", "O último juro sempre"], 0, "A base permanece o capital inicial."),
 Q("Matemática Financeira", "R$ 1.000 a 2% ao mês por 3 meses, a juros simples, gera…", ["R$ 20", "R$ 40", "R$ 60", "R$ 120"], 2, "J = C × i × t = 1.000 × 0,02 × 3 = 60."),
 Q("Matemática Financeira", "Em juros compostos, o montante é calculado por…", ["C(1+i)^t", "C+i+t", "C-i×t", "C/t"], 0, "A capitalização composta eleva (1+i) ao número de períodos."),
 Q("Matemática Financeira", "No SAC, a característica típica é…", ["Amortização constante", "Juros constantes para sempre", "Ausência de amortização", "Prestação necessariamente fixa"], 0, "No SAC a amortização é constante e a prestação tende a cair."),
 Q("Matemática Financeira", "Uma PA possui…", ["Diferença constante entre termos consecutivos", "Razão multiplicativa constante", "Somente termos iguais", "Probabilidades condicionais"], 0, "A diferença entre termos consecutivos da PA é constante."),
],
"statistics": [
 Q("Estatística", "Uma amostra é…", ["Um subconjunto observado da população", "Todos os elementos possíveis por definição", "Uma medida de dispersão", "Um gráfico circular"], 0, "A amostra é a parte observada da população."),
 Q("Estatística", "A mediana é…", ["Sempre o maior valor", "O valor central dos dados ordenados", "A soma das observações", "A diferença entre máximo e mínimo"], 1, "A mediana divide os dados ordenados em metades."),
 Q("Estatística", "O desvio padrão descreve principalmente…", ["A dispersão dos dados em torno da média", "A quantidade de colunas", "O maior valor necessariamente", "A dimensão da população"], 0, "Desvio padrão é uma medida de variabilidade."),
 Q("Probabilidade", "Na probabilidade condicional, a chance é avaliada…", ["Dada a ocorrência de uma condição/evento", "Sem qualquer espaço amostral", "Somente em eventos impossíveis", "Apenas em dados contínuos"], 0, "A condição restringe as informações consideradas."),
 Q("Estatística", "Frequência relativa é…", ["A proporção de ocorrências em relação ao total", "O número máximo apenas", "Uma taxa de juros", "A raiz quadrada da média"], 0, "Frequência relativa divide a contagem pelo total."),
],
"ethics": [
 Q("Ética", "Qual alternativa traz os princípios expressos no art. 37?", ["Legalidade, impessoalidade, moralidade, publicidade e eficiência", "Liberdade, lucro, mercado, sigilo e hierarquia", "Exclusividade, rapidez, conveniência, lucro e segredo", "Pessoalidade, informalidade, preferência e eficiência"], 0, "O conjunto é conhecido pela sigla LIMPE."),
 Q("Compliance", "Qual atitude é adequada diante de possível operação suspeita?", ["Seguir o procedimento interno aplicável e os canais definidos", "Avisar a pessoa para evitar investigação", "Publicar dados do cliente", "Ignorar o procedimento"], 0, "Siga o fluxo de prevenção e comunicação previsto."),
 Q("LGPD", "A LGPD trata de…", ["Tratamento de dados pessoais", "Cálculo de juros simples", "Somente câmbio", "Pontuação em redação"], 0, "A lei dispõe sobre tratamento de dados pessoais."),
 Q("Segurança", "Confidencialidade significa…", ["Permitir acesso apenas a pessoas autorizadas", "Garantir que todo dado seja público", "Eliminar cópias de segurança", "Aumentar o volume de e-mails"], 0, "Confidencialidade limita o acesso de acordo com autorização."),
 Q("Ética", "Um programa de integridade busca…", ["Prevenir, detectar e responder a desvios", "Apenas divulgar publicidade", "Substituir toda legislação", "Eliminar a necessidade de registro"], 0, "Integridade combina controles e resposta a riscos."),
],
"banking": [
 Q("Conhecimentos Bancários", "O Sistema Financeiro Nacional inclui…", ["Órgãos normativos, supervisores e instituições operadoras", "Somente bancos comerciais", "Apenas fintechs", "Somente a CAIXA"], 0, "O SFN inclui participantes com funções distintas."),
 Q("Conhecimentos Bancários", "O PIX é…", ["Um sistema de pagamentos instantâneos", "Um título público", "Uma modalidade de previdência", "Uma moeda estrangeira"], 0, "PIX é um arranjo de pagamentos instantâneos."),
 Q("Conhecimentos Bancários", "Open Finance está associado a…", ["Compartilhamento padronizado sob regras e consentimento aplicáveis", "Abertura automática de contas sem autorização", "Fim de todo sigilo", "Uso exclusivo de dinheiro físico"], 0, "O compartilhamento depende das condições regulatórias e consentimento aplicável."),
 Q("Conhecimentos Bancários", "Qual exemplo corresponde a produto de crédito?", ["Financiamento", "Senha de e-mail", "Arquivo CSV", "Gráfico de setores"], 0, "Financiamento é uma operação de crédito."),
 Q("Conhecimentos Bancários", "Uma garantia real como hipoteca ou alienação fiduciária envolve…", ["Um bem ou direito vinculado ao cumprimento da obrigação", "Somente reputação do vendedor", "Uma taxa de câmbio", "Uma senha de acesso"], 0, "Garantias vinculam bens/direitos nos termos jurídicos aplicáveis."),
 Q("Câmbio", "Uma taxa de câmbio relaciona…", ["O valor de uma moeda em termos de outra", "A média de uma turma", "O número de questões da prova", "A duração de um contrato de trabalho"], 0, "A taxa informa a relação de valor entre moedas."),
 Q("Conhecimentos Bancários", "O FGTS está relacionado principalmente…", ["A contas vinculadas e regras legais de utilização/saque", "Ao cálculo de CSS", "À autenticação de API", "A progressão geométrica"], 0, "O fundo segue critérios legais de depósitos e movimentação."),
 Q("Conhecimentos Bancários", "A segmentação de mercado serve para…", ["Agrupar públicos com características ou necessidades semelhantes", "Eliminar todas as diferenças entre produtos", "Substituir o atendimento", "Evitar qualquer análise de cliente"], 0, "Segmentação organiza a análise de públicos e necessidades."),
],
"it": [
 Q("Tecnologia", "Qual ferramenta é mais adequada para cálculos tabulares e fórmulas?", ["Excel", "PowerPoint", "Outlook", "Paint"], 0, "Planilhas apoiam cálculos, organização e análise tabular."),
 Q("Segurança", "Qual é um sinal comum de phishing?", ["Mensagem urgente com link suspeito e pedido de credenciais", "Atualização verificada pelo canal oficial", "Uso de autenticação multifator", "Endereço confirmado por canal independente"], 0, "Urgência e links suspeitos são sinais de alerta."),
 Q("Tecnologia", "A intranet é geralmente…", ["Uma rede privada para uma organização", "Sinônimo de toda a internet pública", "Uma linguagem de programação", "Um sistema de juros"], 0, "Intranet é uma rede interna com acesso controlado."),
 Q("IA", "Ao usar uma ferramenta de IA, é prudente…", ["Validar resultados e proteger dados sensíveis", "Considerar toda resposta infalível", "Inserir senhas e dados sigilosos", "Ignorar a finalidade do uso"], 0, "IA pode errar; verificação e privacidade continuam necessárias."),
 Q("Tecnologia", "Uma cópia de segurança ajuda principalmente a…", ["Recuperar dados após perda ou corrupção", "Impedir toda fraude", "Substituir autenticação", "Garantir internet mais rápida"], 0, "Backups recuperam dados, conforme sua integridade e atualização."),
],
"digital": [
 Q("Comportamentos Digitais", "O que melhor representa mentalidade de crescimento?", ["Usar feedback e prática para ajustar estratégias", "Acreditar que não é possível aprender", "Ignorar erros", "Evitar qualquer desafio"], 0, "A mentalidade de crescimento usa esforço e feedback de modo estratégico."),
 Q("Ágil", "Uma retrospectiva serve para…", ["Refletir sobre o processo e escolher melhorias", "Distribuir culpa sem plano", "Substituir o cliente", "Apagar o trabalho feito"], 0, "Retrospectivas procuram melhorias para o próximo ciclo."),
 Q("Dados", "Antes de analisar dados, é importante…", ["Definir a pergunta e avaliar a qualidade dos dados", "Escolher um gráfico aleatório", "Assumir que toda correlação é causalidade", "Ignorar valores ausentes"], 0, "A análise deve responder uma pergunta com dados adequados."),
 Q("OKR", "Um resultado-chave bem formulado tende a ser…", ["Mensurável e ligado a um objetivo", "Uma lista sem medida", "Uma tarefa sem propósito", "Uma meta impossível de verificar"], 0, "KRs tornam o progresso observável."),
],
"service": [
 Q("Atendimento", "Escuta ativa começa por…", ["Compreender e confirmar a necessidade do cliente", "Interromper a fala para vender", "Prometer qualquer resultado", "Ignorar contexto"], 0, "A escuta ativa verifica se a necessidade foi entendida corretamente."),
 Q("Atendimento", "Uma venda ética deve…", ["Apresentar opções e condições com clareza", "Omitir custos", "Pressionar mesmo sem adequação", "Prometer aprovação garantida"], 0, "Transparência e adequação protegem o cliente e a instituição."),
 Q("Atendimento", "A ouvidoria tem como papel…", ["Receber e tratar demandas conforme suas atribuições e regras", "Substituir todos os canais", "Garantir qualquer pedido sem análise", "Vender exclusivamente produtos"], 0, "A ouvidoria é componente organizacional com atribuições próprias."),
 Q("Inclusão", "Um atendimento inclusivo deve…", ["Remover barreiras e respeitar as necessidades de acessibilidade", "Presumir necessidades pela aparência", "Negar adaptações", "Usar sempre um único canal"], 0, "Acessibilidade exige respeito a direitos e necessidades relevantes."),
 Q("Atendimento", "CRM ajuda a…", ["Organizar informações e relacionamento com clientes conforme regras", "Dispensar sigilo", "Substituir comunicação", "Garantir venda automática"], 0, "CRM estrutura interações, com respeito à privacidade e aos controles."),
],
}

PYTHON_STORIES = [
"A Cidade Sem Aurora está presa num ciclo de começos abandonados. Íria entrega ao aprendiz a primeira página e diz: 'Não procure velocidade. Procure uma próxima ação clara.'",
"Na entrada da Forja, o guardião das ferramentas exige que o aprendiz faça o ambiente funcionar antes de pedir poder. 'Um herói que não consegue executar o próprio código está lutando às cegas.'",
"A primeira muralha é uma sequência de instruções. Cada condição abre uma passagem e cada repetição ilumina um degrau. Íria: 'A máquina segue exatamente o que você escreveu, não o que quis dizer.'",
"O caminho se divide em tarefas menores. A Voz da Cidade sussurra: 'Transforme uma solução em ferramenta e poderá usá-la em mais de um lugar.'",
"No salão das formas, objetos ganham nome, estado e responsabilidade. Íria: 'Estrutura boa não é enfeite. É o que permite que partes diferentes cooperem.'",
"O guardião oculto tenta vencer com complexidade. Íria não desembainha a espada: 'Entenda o mecanismo antes de usá-lo. O avançado sem propósito é apenas ruído.'",
"A biblioteca foi saqueada pela névoa. O aprendiz recupera dados, arquivos e pequenos módulos. Cada registro salvo torna a cidade um pouco menos frágil.",
"Um espelho de símbolos devolve falsos padrões. A Oráculo ensina: 'Uma expressão só é útil quando sabes quais casos ela aceita e quais deixa passar.'",
"O Oráculo da Confiança altera os resultados a cada visita. O aprendiz começa a registrar provas repetíveis. 'Não confie só na memória do sucesso; construa evidência.'",
"As janelas da cidade voltam a acender. Botões respondem, formulários validam e a interface deixa de ser uma pintura imóvel.",
"Os registros perdidos estão atrás de um cofre. O chaveiro avisa: 'Dados precisam sobreviver ao fechamento e resistir às entradas que tentam quebrar suas regras.'",
"A primeira cidade web surge do nada. Cada pedido encontra uma rota, cada rota uma função, e cada função uma resposta que alguém consegue compreender.",
"Um livro de contatos aparece no chão da praça. O aprendiz restaura os registros, primeiro um de cada vez; depois aprende a procurar, alterar e preservar cada entrada.",
"A cidade pede identidade: nem todo visitante pode abrir qualquer porta. O aprendiz aprende que autenticar alguém e autorizar uma ação são perguntas diferentes.",
"A fachada se reconstrói com estrutura e estilo separados. Íria: 'Uma página acessível explica o conteúdo antes de tentar impressionar os olhos.'",
"O Livro de Consultas mostra tabelas ligadas por chaves. O aprendiz aprende a unir informações sem criar resultados que os dados não sustentam.",
"O trabalho repetitivo começa a desaparecer, mas só depois que o aprendiz aprende a respeitar limites, falhas e as regras dos sistemas externos.",
"Mensagens cruzam a ponte entre cliente e servidor. Cada endpoint promete uma resposta específica, e cada erro precisa dizer o bastante sem revelar demais.",
"Os mestres antigos deixaram padrões. Íria alerta: 'Use a ferramenta pelo problema que resolve, não pelo prestígio do seu nome.'",
"A aplicação funciona no laboratório, mas falha na estrada. O aprendiz aprende a registrar dependências, proteger segredos e explicar a instalação.",
"O Rei da Última Página não aceita um amontoado de código. Quer um problema claro, requisitos verificáveis, testes e uma demonstração honesta.",
]
CAIXA_STORIES = [
"O Arquivo dos Ecos está coberto por anotações contraditórias. A primeira chave é ler com cuidado: só avança quem distingue o que o texto afirma do que apenas parece sugerir.",
"A inscrição seguinte está escrita em outra língua. Não é preciso traduzir cada pedra; é preciso descobrir a mensagem e justificar a leitura pelas pistas disponíveis.",
"A Câmara dos Números recusa palpites. O aprendiz anota capital, taxa, prazo e regime antes de escolher a fórmula.",
"O Cartógrafo exige que o aprendiz leia as distribuições, localize o centro dos dados e reconheça quando a dispersão muda a história.",
"Um caminho rápido promete poder, mas cobra integridade. A Guardiã dos Princípios pede que cada decisão respeite os deveres, os dados e a lei.",
"O Cofre Central está protegido por conceitos que se conectam: instituições, mercados, produtos, pagamentos e regras.",
"O terminal de comunicação está cheio de ferramentas e riscos. O aprendiz deve escolher a tecnologia apropriada e manter a informação protegida.",
"A Câmara da Mudança só se abre para quem aprende, coopera e transforma problemas complexos em passos observáveis.",
"A última chave antes do cofre exige escuta, clareza e inclusão. Um atendimento só funciona se a necessidade real for compreendida.",
"A ponte final é feita de palavras. O examinador não pode adivinhar uma boa ideia que não foi organizada no papel.",
]


def _make_question_set(bank_key: str, index: int, source: dict, count: int = 4):
    banks = PYTHON_BANKS if source == "python" else CAIXA_BANKS
    bank = banks.get(bank_key, banks.get("project" if source == "python" else "portuguese", []))
    if not bank:
        bank = (PYTHON_BANKS if source == "python" else CAIXA_BANKS)["project" if source == "python" else "portuguese"]
    count = min(count, len(bank))
    return [deepcopy(bank[(index + j) % len(bank)]) for j in range(count)]


def _topic_question(subject: str, title: str, prompt: str, correct_text: str, index: int, explanation: str):
    """Create a topic-specific retrieval question, rotating answer position to avoid answer-position learning."""
    distractors = [
        "Pular a atividade e marcar como concluído sem demonstrar compreensão.",
        "Memorizar somente o título, sem explicar ou aplicar o conceito.",
        "Consultar a resposta primeiro e copiar sem verificar o raciocínio.",
    ]
    answer_index = index % 4
    options = list(distractors)
    options.insert(answer_index, correct_text)
    return Q(subject, prompt, options, answer_index, explanation)


def build_campaign_missions(profile_key: str, custom_topics=None):
    missions = []
    if profile_key == "python":
        chapters = PYTHON_CHAPTERS
        narrative = PYTHON_STORIES
        prefix = "py"
        source = "python"
    elif profile_key == "caixa":
        chapters = CAIXA_CHAPTERS
        narrative = CAIXA_STORIES
        prefix = "cx"
        source = "caixa"
    else:
        topics = [t.strip() for t in (custom_topics or ["Fundamentos", "Prática guiada", "Aplicação", "Projeto livre", "Revisão final"]) if t.strip()]
        chapters = []
        for i, topic in enumerate(topics):
            chapters.append((topic, "Trilha pessoal editável", f"Esta é sua jornada. Transforme {topic.lower()} em uma competência que você consegue demonstrar.", [
                ("Definir o objetivo", f"Escreva com clareza o que quer aprender em {topic} e como reconhecerá que aprendeu.", "Escreva um resultado observável para esta etapa.", "project"),
                ("Estudar o conceito", f"Consulte sua fonte principal sobre {topic}. Reescreva a ideia com suas palavras e diferencie fatos de dúvidas.", "Faça um resumo curto sem copiar a fonte.", "project"),
                ("Praticar com apoio", f"Use {topic} numa atividade pequena, consultando o material quando necessário e registrando obstáculos.", "Resolva um exemplo simples e documente um erro ou descoberta.", "project"),
                ("Aplicar sem consulta", f"Tente executar uma tarefa relacionada a {topic} antes de olhar a solução.", "Faça uma aplicação sem consultar a resposta e depois confira.", "project"),
                ("Explicar e consolidar", f"Explique {topic} com suas palavras. Acrescente questões próprias na Configuração para transformar esta etapa em um teste específico.", "Explique a ideia em voz alta e crie uma pergunta de revisão.", "project"),
            ]))
        narrative = ["Esta jornada foi criada por você. Íria entrega uma página em branco: 'O caminho pertence a quem define o que vale a pena aprender.'"] * len(chapters)
        prefix = "cu"
        source = "python"

    chapter_last_ids = []
    global_index = 0
    total_chapters = len(chapters)
    for ci, chapter in enumerate(chapters):
        if len(chapter) == 4:
            chapter_title, chapter_summary, story, lessons = chapter
        else:
            chapter_title, chapter_summary, story, lessons = chapter[0], chapter[1], chapter[2], chapter[3]
        # Every chapter has its own story fragment; each lesson adds a unique line to keep the campaign linear.
        for li, lesson in enumerate(lessons):
            title, concept, practice, qbank = lesson
            global_index += 1
            lesson_id = f"{prefix}_{ci+1:02d}_{li+1:02d}"
            if source == "python":
                question_offset = li + ci * 2
                bank_quiz = _make_question_set(qbank, question_offset, "python", 4)
            else:
                question_offset = li + ci
                bank_quiz = _make_question_set(qbank, question_offset, "caixa", 4)
            topic_subject = chapter_title
            concept_question = _topic_question(
                topic_subject, title,
                f"IDEIA-CHAVE · {title}: qual afirmação corresponde à lição?",
                concept, global_index,
                "Esta alternativa representa a ideia-chave desta etapa. Tente explicá-la com suas palavras antes de avançar.")
            practice_question = _topic_question(
                topic_subject, title,
                f"MISSÃO PRÁTICA · {title}: qual ação demonstra que você trabalhou este tópico?",
                practice, global_index + 1,
                "A atividade indicada conecta a ideia à prática. Faça-a no seu material e registre as dúvidas antes de marcar como concluída.")
            # Two domain-bank questions plus two questions specific to this exact topic.
            quiz = [bank_quiz[0], concept_question, bank_quiz[1], practice_question]
            story_text = narrative[min(ci, len(narrative)-1)]
            if li == 0:
                story_intro = (f"{story_text}\n\nÍria aponta para a entrada do capítulo {ci+1}: '{chapter_title}'. "
                               f"'Esta região guarda {len(lessons)} selos. O primeiro só responde quando você transformar a ideia em prática.'")
            else:
                previous_title = lessons[li-1][0]
                story_intro = (f"O selo de '{previous_title}' ainda brilha no seu diário. A passagem seguinte se abre, revelando '{title}'. "
                               f"Íria: 'Não recomeçamos do zero: usamos o que já aprendemos para enfrentar o próximo obstáculo.'")
            if li == len(lessons)-1:
                story_outro = (f"O último selo de '{chapter_title}' desperta. Íria recolhe o fragmento e aponta para a passagem seguinte: "
                               "'A região ficou para trás. Prepare-se: os guardiões surgem quando conhecimento suficiente se transforma em domínio.'")
            else:
                story_outro = (f"O selo de '{title}' brilha e encaixa-se no mapa. Íria: 'Uma ideia compreendida é uma ferramenta. "
                               "Leve-a para a próxima página — ela poderá ser a chave de uma prova futura.'")
            missions.append({
                "id": lesson_id,
                "topic": chapter_title,
                "chapter_title": chapter_title,
                "chapter_index": ci + 1,
                "chapter_total": total_chapters,
                "lesson_index": li + 1,
                "lessons_in_chapter": len(lessons),
                "global_index": global_index,
                "title": title,
                "description": concept,
                "lesson_text": f"IDEIA-CHAVE\n{concept}\n\nROTEIRO DE ESTUDO\n1. Leia esta ideia e, se estiver seguindo o curso de Python ou seu material da Caixa, abra o tópico correspondente.\n2. Antes de olhar a solução, tente prever o resultado ou explicar o raciocínio.\n3. Faça a atividade prática sem copiar; consulte o material para corrigir erros.\n4. Feche o material e explique o conceito com suas palavras.\n\nCHECAGEM DE DOMÍNIO\nVocê só precisa avançar depois de conseguir demonstrar o conceito e passar na prova desta página.",
                "practice": practice,
                "success_criteria": f"Você consegue explicar '{title}' com suas palavras e concluir a atividade prática sem apenas copiar a solução.",
                "chapter_story": story_text,
                "story_intro": story_intro,
                "story_outro": story_outro,
                "quiz": quiz,
                "xp": 30 + min(ci, 10) * 2,
                "coins": 10 + (ci % 4) * 2,
                "weight": (15 if chapter_title == "Conhecimentos Bancários" else 10 if chapter_title == "Atendimento Bancário" else 5) if source == "caixa" else 0,
                "block": ("Redação" if "Redação" in chapter_title else "Conhecimentos Básicos" if ci < 5 else "Conhecimentos Específicos") if source == "caixa" else "",
                "kind": "lesson",
            })
        chapter_last_ids.append(missions[-1]["id"])
    # Attach chapter boundary metadata and five ordered boss checkpoints.
    for m in missions:
        m["chapter_last_lesson_id"] = chapter_last_ids[m["chapter_index"] - 1]
        m["is_chapter_start"] = m["lesson_index"] == 1
        m["is_chapter_end"] = m["id"] == m["chapter_last_lesson_id"]
        m["boss_checkpoint"] = m["chapter_index"] in sorted(set(max(1, round((i+1)*len(chapters)/5)) for i in range(5))) and m["is_chapter_end"]
    return missions


def chapter_boss_thresholds(missions, boss_count=5):
    if not missions:
        return [1] * boss_count
    chapter_ends = [m["global_index"] for m in missions if m.get("is_chapter_end")]
    thresholds = []
    for i in range(1, boss_count + 1):
        target = len(missions) * i / boss_count
        eligible = [x for x in chapter_ends if x >= target]
        thresholds.append(min(eligible) if eligible else len(missions))
    for i in range(1, len(thresholds)):
        thresholds[i] = max(thresholds[i], thresholds[i-1] + 1)
    thresholds[-1] = len(missions)
    return thresholds
