import threading
import multiprocessing
import logging
from threading import Thread
import time
import datetime
from pydriller import Repository, repository
from flask import current_app
import os
import random
from msr.dao import Repositories
from msr import handler_files
from queue import Queue

repositoryCollection = Repositories()

logging.basicConfig(format='%(levelname)s - %(asctime)s.%(msecs)03d: %(message)s', datefmt='%H:%M:%S', level=logging.INFO)

# List of producers of dictionaries
list_of_producers_dictionaries = list()

work_of_dictionaries = Queue()
finished_of_dictionaries = Queue()

def atualizar_repositorio(app, user_id, repository):
    try:
        with app.app_context():
            repositoryCollection.update_repository_by_name( pega_nome_repositorio(repository), user_id, 2)
    except Exception as e:
        display(f'Error during access data base to update in {repository} error: {e}')

def salvar_dicionario_em_arquivo_json(app, name, user_id, my_dictionary, path_repositories):
    try:
        with app.app_context():
            handler_files.save_dictionary_in_json_file(name, user_id, my_dictionary, path_repositories)
    except Exception as e:
        display(f'Error during try to save the dictionary {name} as a json file!: {e}')
    
def display(msg):
    threadname = threading.current_thread().name
    processname = multiprocessing.current_process().name
    logging.info(f'{processname}\{threadname}: {msg}')

# List all Commits from Authors
# return a dictionary like this: hash, author, date, list of files in commit
# dictionary = {'hash': ['author', 'date of commit', [file1, file2, ...]]}
def dictionaryWithAllCommmits(client, repository):
    dictionaryAux = {}
    try: 
        for commit in Repository(repository).traverse_commits():
            commitAuthorNameFormatted = '{}'.format(commit.author.name)
            commitAuthorDateFormatted = '{}'.format(commit.author_date)
            listFilesModifiedInCommit = []
            for modification in commit.modified_files:
                itemMofied = '{}'.format(modification.filename)
                listFilesModifiedInCommit.append(itemMofied)
            dictionaryAux[commit.hash] = [commitAuthorNameFormatted, commitAuthorDateFormatted, listFilesModifiedInCommit] 
    except Exception as e:
        display(f'Error during processing dictionaryWithAllCommmits in {repository} error: {e}')
        dictionaryAux = None
    produzir_dicionario(client, pega_nome_repositorio(repository), dictionaryAux, work_of_dictionaries, finished_of_dictionaries)
    return dictionaryAux

def create_new_thread_save_dictionary(app, client, name, my_dictionary):
    thread = Thread(target=salvar_dicionario_em_arquivo_json, args=[app, name, client, my_dictionary, Constants.PATH_REPOSITORIES], daemon=True)
    display('It was created a new Thread ' + thread.getName() + ' to save dictionary' + name + ' in json file')
    thread.start()
    thread.join()
    display('Thread ' + thread.getName() + ' save ' + name + 'in json file')

def create_new_thread_banco(app, user_id, repository):
    thread = Thread(target=atualizar_repositorio, args=[app, user_id, repository], daemon=True)
    display('It was created a new Thread ' + thread.getName() + ' to access database to update repository ' + repository)
    thread.start()
    thread.join()
    display('Thread ' + thread.getName() + ' save ' + repository + 'in the database')

def create_new_thread_analyse_commits(client, repository):
    thread = Thread(target=dictionaryWithAllCommmits, args=[client, repository], daemon=True) 
    display('It was created a new Thread ' + thread.getName() + ' to analyse repository ' + repository)
    thread.start()
    thread.join()
    display('Thread ' + thread.getName() + ' finished analysing of repository ' + repository)
    
def create_new_thread_default_dictionaries(argumentos):
    thread = Thread(target=create_work_save_dictionary_in_json_file, args=[argumentos[0], argumentos[1], argumentos[2], argumentos[3], argumentos[4]], daemon=True)
    display('It was created a new Thread ' + thread.getName() + ' to enqueue dictionary ')
    thread.start()
    display('Thread ' + thread.getName() + ' finished enqueueing of dictionary')
    return thread

# Producer: the client send a dictionary to queue of dictionary
def create_work_save_dictionary_in_json_file(client, nome, my_dictionary, queue, finished):
    #lock
    finished.put(False)
    # insert element in queue
    my_request = (client, nome, my_dictionary)
    queue.put(my_request)
    display(f'Producing request from client {str(client)} to save the dictionary of {nome} to enqueue')
    finished.put(True)
    #unlock 
    display(f'The request to save dictionary to enqueue has done')

# Consumer - For each request inserted in the Queue the consumer fire one thread to process each repository stored in the Queue
def perform_work_consume_dictionaries(app, work, finished):
    counter = 0
    v =  None
    while True:
        if not work.empty():
            v = work.get()
            display(f'Consuming {counter}: {v}')
            create_new_thread_save_dictionary(app, v[0], v[1], v[2])
            counter += 1
        else:
            q = finished.get()
            display(f'There is no itens to consume!')
            if q == True:
                break
        if v is not None: 
            display(f'The item {v} has consumed with success!')

def create_new_thread_default(argumentos):
    thread = Thread(target=create_work, args=[argumentos[0], argumentos[1], argumentos[2], argumentos[3]], daemon=True)
    display('It was created a new Thread ' + thread.getName() + ' to enqueue repository ' + argumentos[1])
    thread.start()
    display('Thread ' + thread.getName() + ' finished enqueueing of repository ' + argumentos[1])
    return thread

# Producer: the client send a request to the queue
def create_work(client, repository, queue, finished):
    #lock
    finished.put(False)
    # insert element in queue
    my_request = (client, pega_nome_repositorio(repository), repository)
    queue.put(my_request)
    display(f'Producing request from client {str(client)} and {repository} to enqueue')
    finished.put(True)
    #unlock 
    display(f'The request {my_request} has done')

# Consumer - For each request inserted in the Queue the consumer fire one thread to process each repository stored in the Queue
def perform_work(app, work, finished):
    counter = 0
    v =  None
    while True:
        if not work.empty():
            v = work.get()
            display(f'Consuming {counter}: {v}')
            print(f'Cloning repository {v[2]} from client {str(v[0])}')
            create_new_thread_analyse_commits(v[0],v[2])
            create_new_thread_banco(app, v[0], v[2])
            processar_fila_dedicionarios_em_background(app, work_of_dictionaries, finished_of_dictionaries)
            counter += 1
        else:
            q = finished.get()
            display(f'There is no itens to consume!')
            if q == True:
                break
        if v is not None: 
            display(f'The item {v} has consumed with success!')

def produzir_dicionario(client, nome, dicionario, work, finished):
    thread = create_new_thread_default_dictionaries([client, nome, dicionario, work, finished])
    list_of_producers_dictionaries.append(thread)
        
    return 'produzido o dicionario'

def processar_fila_dedicionarios_em_background(app, work, finished):
    # Create the thread consumer dictionaries stored in the Queue
    consumer = Thread(target=perform_work_consume_dictionaries, args=[app, work, finished], daemon=True)

    print('Start the consumer of dictionaries')
    # Start the consumer of queue of dictionaries
    consumer.start()

    if len(list_of_producers_dictionaries) > 0:
        for each in list_of_producers_dictionaries:
            each.join()
            display('Producer ' + each.getName() + 'of dictionary has finished with success!')
        list_of_producers_dictionaries.clear()

    consumer.join()
    display('Consumer of dictionary has finished')
    display('Finished the main process of consumer of dictionary.')

    return '<p> processamento dos repositórios foi concluído com sucesso!'

def pega_nome_repositorio(url):
    temp = url.split('/')
    nome_com_extensao = ''
    for each in temp:
        if '.git' in each:
          nome_com_extensao = each
    lista = nome_com_extensao.split('.')
    return lista[0]

class Constants:
    PATH_MYADMIN = os.path.abspath(os.getcwd())
    PATH_MYAPP = PATH_MYADMIN + '/msr'
    PATH_STATIC = PATH_MYADMIN + '/msr/static'
    PATH_IMG = PATH_MYADMIN + '/msr/static/img'
    PATH_JSON = PATH_MYADMIN + '/msr/static/json'
    PATH_UPLOADS = PATH_MYADMIN + '/msr/static/uploads'
    PATH_REPOSITORIES = PATH_MYADMIN + '/msr/static/repositories'