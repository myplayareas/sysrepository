# sysrepository
MVP do SysRepository para análise de repositório de software

Estrutura básica
```bash
├── msr
│   ├── __init__.py
│   ├── forms.py
│   ├── models.py
│   ├── msr.db
│   ├── routes.py
│   ├── static
│   │   └── img
│   │       └── repository.png
│   └── templates
│       ├── base.html
│       ├── home.html
│       ├── login.html
│       ├── msr.html
│       └── register.html
└── run.py
```

Dentro do diretório base existe o diretório msr referente a pasta da aplicação. 

O script **run.py** é responsável por importar a aplicação e executá-la em um servidor web, por exemplo o [WSGI](https://en.wikipedia.org/wiki/Web_Server_Gateway_Interface). Para esta aplicação de exemplo vamos usar o [werkzeug](https://www.palletsprojects.com/p/werkzeug)

A pasta templates é responsável por abrigar as views em arquivos html. Além disso, também pode existir uma pasta static para abrigar os arquivos estáticos da aplicação, como por exemplo imagens, css, plugins, entre outros. 

Dentro do diretório da aplicação msr existe o arquivo **__init__.py** que é responsável por preparar a configuração da aplicação. 

Além do módulo flask, existem mais 3 outros módulos: [flask_sqlalchemy](https://flask-sqlalchemy.palletsprojects.com), [flask_bcrypt](https://flask-bcrypt.readthedocs.io) e [flask_login](https://flask-login.readthedocs.io). Eles são módulos de extensão do flask responsáveis respectivamente por acesso ORM (Obeject-relational mapping) ao banco de dados via sqlalchemy, extensão que prover hashing para a aplicação via, e por fim, extensão que prover gerenciamento de sessão de usuário para a aplicação flask.

Módulos base: [SQLAlchemy](https://www.sqlalchemy.org) e [bcrypt](https://pypi.org/project/bcrypt)

Em linhas gerais é preciso criar os seguintes elementos e estruturas para configurar a aplicação: 

- app - objeto que representa a aplicação Flask
- bcrypt - objeto que representa ações de hashing sobre a aplicação Flask app
- db - objeto que gerencia ações de manipulação ORM de banco de dados, via SQLAlchemy, sobre a aplicação Flask app
- login_manager - objeto que gerencia a sessão do usuário na aplicação Flask app

A aplicação precisa ter a configuração de banco de dados informando onde se encontra o arquivo do banco. 

O objeto login_manager precisa informar qual a view que representa a tela de login da aplicação. 

Por fim, o **__init__.py** também precisa importar as rotas da aplicação que carregam e manipulam as views da aplicação.

O arquivo **msr.db** representa o arquivo [SQLite](https://www.sqlite.org/index.html) que armazena as informações do banco de dados msr.

O arquivo **models.py** representa os modelos da aplicação através das classes User e Repository. Mais detalhes sobre o funcionamento da criação de modelos usando o [flask_sqlalchemy](https://flask-sqlalchemy.palletsprojects.com/en/2.x/quickstart)

O arquivo models.py também carrega dados do usuário logado através da função load_user que tem o decorator @login_manager.user_loader do módulo login_manager para gerenciar a sessão do usuário logado na aplicação.

O arquivo **routes.py** gerencia as rotas da aplicação, ou seja - de forma simplificada, ele é responsável por gerenciar os requests e responses da aplicação carregando e devolvendo as views da aplicação. 

Para esta aplicação existem as seguintes rotas básicas:
1. / ou /home para carregar a página principal da aplicação representada pela view home.html
2. /msr para carregar a página com os repositorios do usário da aplicação representada pela view msr.html
3. /register para carregar o formulário de registro de usuário da aplicação representada pela view register.html
4. /login para para fazer o controle de acesso da aplicação, esta página é representada pela view login.html para carregar o formulário de login e a view msr_page para carregar a view msr caso o usário seja autenticado com sucesso. 
5. /logout para realizar o encerramento da sessão do usuário e redirecionar o usuário deslogado para a página inicial da aplicação

Os seguintes módulos são usados para auxiliar o gerenciamento das chamadas das rotas e devolução de suas respostas:  render_template, redirect, url_for, flash, login_user, logout_user, login_required, além dos objetos da aplicação db, User, Repository, RegisterForm e LoginForm. 

Seguem os links de cada um dos módulos e extensões usadas: [render_template](https://flask.palletsprojects.com/en/2.0.x/api/#flask.render_template), 
[redirect](https://flask.palletsprojects.com/en/2.0.x/api/#flask.render_template), [url_for](https://flask.palletsprojects.com/en/2.0.x/api/#flask.url_for),
[flash](https://flask.palletsprojects.com/en/2.0.x/patterns/flashing), [login_user, logout_user e login_required](https://flask-login.readthedocs.io/en/latest/#flask_login.login_user)

Por fim, existe o script **forms.py** para gerenciar a entrada e validação dos dados dos formulários da aplicação. Basicamente existem duas classes para validar dois forms nessa aplicação: a classe RegisterForm que valida os dados de registro de novos usuários e a classe LoginForm que valida os dados do formulário de login da alicação. 

Para fazer a validação dos dados de entrada da aplicação são usados os seguintes módulos e extensões do Flask: [flask_wtf](https://flask-wtf.readthedocs.io) e [wtforms](https://flask-wtf.readthedocs.io)

Esses módulos usam [FlaskForm](https://flask-wtf.readthedocs.io/en/0.15.x/quickstart/#validating-forms), [StringField e PasswordField](https://wtforms.readthedocs.io/en/2.3.x/fields),
[SubmitField](https://wtforms.readthedocs.io/en/2.3.x/fields/#wtforms.fields.SubmitField) e [Length, EqualTo, Email, DataRequired e ValidationError](https://wtforms.readthedocs.io/en/2.3.x/validators) para manipular os dados de entrada. 

Para executar a aplicação é preciso instalar todos os módulos e extensões supracitadas. Além disso, é preciso setas as seguintes variáveis de ambiente: 

Para o ambiente Posix:
```bash
export FLASK_APP=run.py
export FLASK_ENV=development
```
Mais detalhes em [CLI Flask](https://flask.palletsprojects.com/en/2.0.x/cli/)

Executar a aplicação via CLI: 
```bash
$flask run
```
