from msr import app
from flask import render_template, redirect, url_for, flash
from msr.dao import User, Users, Repository, Repositories
from msr.forms import RegisterForm, LoginForm, RepositoryForm
from msr import db
from flask_login import login_user, logout_user, login_required, current_user
import datetime
from queue import Queue
from functools import wraps
from werkzeug.exceptions import HTTPException, InternalServerError
from flask import current_app, request, abort
import uuid
import threading
import multiprocessing
import logging
from threading import Thread
from msr import utilidades

tasks = {}

# List of producers
list_of_producers = list()

# Lista da strings de repositorios
lista_de_repositorios = list()

link_processar_repositorios = ""

work = Queue()
finished = Queue()

consumer = None

usersCollection = Users()
repositoryColletion = Repositories()

def flask_async(f):
    """
    This decorator transforms a sync route to asynchronous by running it in a background thread.
    """
    @wraps(f)
    def wrapped(*args, **kwargs):
        def task(app, environ):
            # Create a request context similar to that of the original request
            with app.request_context(environ):
                try:
                    # Run the route function and record the response
                    tasks[task_id]['result'] = f(*args, **kwargs)
                except HTTPException as e:
                    tasks[task_id]['result'] = current_app.handle_http_exception(e)
                except Exception as e:
                    # The function raised an exception, so we set a 500 error
                    tasks[task_id]['result'] = InternalServerError()
                    if current_app.debug:
                        # We want to find out if something happened so reraise
                        raise

        # Assign an id to the asynchronous task
        task_id = uuid.uuid4().hex

        # Record the task, and then launch it
        tasks[task_id] = {'task': threading.Thread(
            target=task, args=(current_app._get_current_object(), request.environ))}
        tasks[task_id]['task'].start()

        # Return a 202 response, with an id that the client can use to obtain task status
        return {'TaskId': task_id}, 202

    return wrapped

def produzir_repositorios(lista_de_repositorios, work, finished):
    client = current_user.get_id()
    for each in lista_de_repositorios: 
        thread = utilidades.create_new_thread_default([client, each, work, finished])
        list_of_producers.append(thread)
        repository = Repository(name=utilidades.pega_nome_repositorio(each), link=each, owner=current_user.get_id())
        repositoryColletion.insert_repository(repository)
        
    return url_for('processar_em_background')

def repositorios_ja_existem(lista_de_repositorios, user_id):
    lista_de_repositorios_ja_existem = list()
    try: 
        for each in lista_de_repositorios:
            resultado = repositoryColletion.query_repositories_by_name_and_user_id(utilidades.pega_nome_repositorio(each), user_id)
            if len(resultado) > 0:
                lista_de_repositorios_ja_existem.append( resultado )
    except Exception as e:
        print(f'Erro ao consultar repositorio no banco: {e}')
    return lista_de_repositorios_ja_existem

@app.route("/criar", methods=["GET", "POST"])
@login_required
def criar():
    """Create a new repository for the current user."""
    if request.method == "POST":
        error = None
        error_processing_repository = None
        cadeia_de_repositorios = request.form["repositorios"]

        # Nenhum repositorio foi passado
        if len(cadeia_de_repositorios) == 0:
            error = "List of repositories is required."
            flash(error, 'danger')
            return render_template("criar.html")
        else:
            lista_de_repositorios = cadeia_de_repositorios.split(",")
            testa_repositorios = repositorios_ja_existem(lista_de_repositorios, current_user.get_id() )

        # Checa se ja existe algum repositorio no banco
        if len(testa_repositorios) > 0: 
            lista = list()
            for each in testa_repositorios:
                lista.append(each.name)

            error = f'O(s) repositorio(s) {lista} já foi(forão) cadastrado(s) no banco!'
            flash(error, category='danger')
            return render_template("criar.html")

        try:
            # Produtor que enfileira o repositorio na lista de repositorios
            link_processar_repositorios = produzir_repositorios(lista_de_repositorios, work, finished)
            # Limpa a lista de string de repositórios
            lista_de_repositorios.clear()
        except Exception as e:
            error_processing_repository = "Erro na produção dos repositorios" + str(e)
            if error_processing_repository is not None:
                flash(error_processing_repository, category='danger')
                return redirect(url_for("msr_page"))
        
        message = "Repositório(s) criado(s) com sucesso!"
        flash(message, 'success')
        return redirect(url_for("msr_page"))

    return render_template('criar.html')

@app.route("/processar")
@login_required
@flask_async
def processar_em_background():
    # Create the thread consumer repositories stored in the Queue
    consumer = Thread(target=utilidades.perform_work, args=[current_app._get_current_object(), work, finished], daemon=True)

    print('Start the consumer')
    # Start the consumer of queue of requests
    consumer.start()

    if len(list_of_producers) > 0:
        for each in list_of_producers:
            each.join()
            utilidades.display('Producer ' + each.getName() + ' has finished with success!')
        list_of_producers.clear()

    consumer.join()
    utilidades.display('Consumer has finished')
    utilidades.display('Finished the main process.')

    return '<p> processamento dos repositórios foi concluído com sucesso!'

@app.context_processor
def utility_processor():
    def status_repositorio(status):
        valor = ''
        try:
            lista_de_status = list()
            lista_de_status = ['Erro','Registrado', 'Analisado']
            valor = lista_de_status[status]
        except Exception as e:
            utilidades.display('Erro de status: valor ' + valor + ' - status:  ' + str(status) + ' - ' + str(e))
        return valor
    return dict(status_repositorio=status_repositorio)
    
@app.route("/repositorio/<int:id>/analisado", methods=["GET"])
@login_required
def visualizar_analise_repositorio(id):
    repositorio = repositoryColletion.query_repository_by_id(id)
    link = repositorio.link
    name = repositorio.name
    creation_date = repositorio.creation_date
    analysis_date = repositorio.analysis_date
    status = repositorio.analysed

    relative_path = 'repositories' + '/' + str(current_user.get_id()) + '/' + name + '.json'
    relative_path_file_name = url_for('static', filename=relative_path)

    return render_template("analisado.html", my_link=link, my_name=name, my_creation_date=creation_date,
                                my_analysis_date=analysis_date, my_status=status,
                                my_relative_path_file_name=relative_path_file_name)

@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')

@app.route('/msr')
@login_required
def msr_page():
    repositories = Repository.query.filter_by(owner=current_user.get_id()).all()
    print(f'Fila de repositórios: {work.queue}')
    return render_template('msr.html', repositories=repositories)

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(username=form.username.data, email_address=form.email_address.data, password=form.password1.data)
        usersCollection.insert_user(user_to_create)
        login_user(user_to_create)
        flash(f"Account created successfully! You are now logged in as {user_to_create.username}", category='success')
        return redirect(url_for('msr_page'))
    if form.errors != {}: #If there are not errors from the validations
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', category='danger')

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(attempted_password=form.password.data):
            login_user(attempted_user)
            flash(f'Success! You are logged in as: {attempted_user.username}', category='success')
            return redirect(url_for('msr_page'))
        else:
            flash('Username and password are not match! Please try again', category='danger')

    return render_template('login.html', form=form)

@app.route('/logout')
def logout_page():
    logout_user()
    flash("You have been logged out!", category='info')
    return redirect(url_for("home_page"))

def exist_repository_in_user(name, link, lista):
    checa = False
    if len(lista) > 0:
        for each in lista:
            if each.name == name or each.link == link:
                checa = True
    return checa

@app.route('/repository', methods=['GET', 'POST'])
@login_required
def repository_page():
    form = RepositoryForm()

    if form.validate_on_submit():
        name = form.name.data
        link = form.link.data

        list_user_repositories = repositoryColletion.query_repositories_by_user_id(current_user.get_id())
        if not exist_repository_in_user(name, link, list_user_repositories):
            repository = Repository(name=name, link=link, creation_date=datetime.datetime.now(), 
                                            analysis_date=None, analysed=0, owner=current_user.get_id())
            repositoryColletion.insert_repository(repository)
            flash(f'Repository {repository.name} created with success!', category='success')
            return redirect(url_for('msr_page'))

        flash('Repository already exist!', category='danger')

    if form.errors != {}: #If there are not errors from the validations
        for err_msg in form.errors.values():
            flash(f'There was an error with new repository: {err_msg}', category='danger')

    return render_template('repository.html', form=form)  