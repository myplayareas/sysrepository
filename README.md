I chose to choose the Flask microframework because it is a simpler framework and requires a smaller set of dependencies and libraries to work with the http environment for request and response.

Flask uses the MTV (Model Template View) standard and with that, our application will follow the conventions recommended by Flask.

Inside the base directory, there is the msr directory referring to the application folder.

Here is a base application structure with its most important directories and files:

```bash
.
├── run.py
├── setvariables.sh
├── msr
│   ├── __init__.py
│   ├── routes.py
│   ├── forms.py
│   ├── dao.py
│   ├── handler_threads.py
│   ├── handler_files.py
│   ├── msr.db
│   ├── static
│   │   ├── img
│   │   │   └── repository.png
│   │   ├── jsonview.bundle.css
│   │   ├── jsonview.bundle.js
│   │   ├── repositories
│   │   │   ├── user 1
│   │   │   │   ├── ...
│   │   │   └── user n
│   │   └── uploads
│   └── templates
│       ├── base.html
│       ├── home.html
│       ├── authenticate
│       │   ├── register.html
│       │   └── login.html
│       ├── user
│       │   ├── profile.html
│       │   └── msr.html (dashboard.html)
│       ├── repository
│       │   ├── criar.html
│       │   ├── repository.html
│       │   └── analisado.html 
│	├── ...
├── docs
│   ├── diagrams
│   │   ├── out
│   │   │       └── ...
│   │   └── src
│   │       ├── ...
│   └── ui
│       ├── ...
└── ...
```

The **run.py** script is responsible for importing the application and running it on a web server, for example [WSGI](https://en.wikipedia.org/wiki/Web_Server_Gateway_Interface). For this example application, we will use [werkzeug](https://www.palletsprojects.com/p/werkzeug)

The templates folder is responsible for holding views in html files. In addition, there may also be a static folder to house the application's static files, such as images, css, plugins, among others.

Inside the msr application directory, there is the **__init__.py** file which is responsible for preparing the application configuration.

In addition to the flask module, there are 3 other modules: [flask_sqlalchemy](https://flask-sqlalchemy.palletsprojects.com), [flask_bcrypt](https://flask-bcrypt.readthedocs.io) and [flask_login](https ://flask-login.readthedocs.io). They are flask extension modules responsible respectively for ORM (Obeject-relational mapping) access to the database via sqlalchemy, extension that provides hashing for the application via, and finally, extension that provides user session management for the flask application .

Base modules: [SQLAlchemy](https://www.sqlalchemy.org) and [bcrypt](https://pypi.org/project/bcrypt)

In general terms, the following elements and structures must be created to configure the application:

- app - object representing the Flask application
- bcrypt - object representing hashing actions on the Flask app
- db - object that manages ORM database manipulation actions, via SQLAlchemy, on the Flask app application
- login_manager - object that manages the user's session in the Flask app

The application must have the database configuration informing where the database file is located.

The login_manager object needs to inform which view represents the application's login screen.

Finally, **__init__.py** also needs to import the application routes that load and manipulate the application views.

The **msr.db** file represents the [SQLite](https://www.sqlite.org/index.html) file which stores the msr database information.

The **dao.py** file represents the application models through User and Repository classes. More details on how model creation works using [flask_sqlalchemy](https://flask-sqlalchemy.palletsprojects.com/en/2.x/quickstart)

The dao.py file also loads data from the logged user through the load_user function which has the @login_manager.user_loader decorator of the login_manager module to manage the session of the user logged into the application.

The **routes.py** file manages the application's routes. That is - in a simplified way, it is responsible for managing the application's requests and responses, loading and returning the application's views.

For this application, there are the following basic routes:
1. / or /home to load the application's main page represented by the home.html view
2. /msr to load the page with the application's user repositories represented by the msr.html view
3. /register to load the user registration form from the application represented by the register.html view
4. /login to do application access control, this page is represented by the login.html view to load the login form and the msr_page view to load the msr view if the user is successfully authenticated.
5. /logout to log out the user and redirect the logged-out user to the application's home page

The following modules are used to help manage route calls and return their responses: render_template, redirect, url_for, flash, login_user, logout_user, login_required, in addition to the db, User, Repository, RegisterForm, and LoginForm application objects.

Here are the links for each of the modules and extensions used: [render_template](https://flask.palletsprojects.com/en/2.0.x/api/#flask.render_template),
[redirect](https://flask.palletsprojects.com/en/2.0.x/api/#flask.render_template), [url_for](https://flask.palletsprojects.com/en/2.0.x/api/#flask.url_for),
[flash](https://flask.palletsprojects.com/en/2.0.x/patterns/flashing), [login_user, logout_user and login_required](https://flask-login.readthedocs.io/en/latest/#flask_login.login_user)

Finally, the **forms.py** script manages the input and validation of the application's forms data. Basically, there are two classes to validate two forms in this application: the RegisterForm class that validates the registration data of new users and the LoginForm class that validates the application's login form data.

To validate the application's input data, the following Flask modules and extensions are used: [flask_wtf](https://flask-wtf.readthedocs.io) and [wtforms](https://flask-wtf.readthedocs.io)

These modules use [FlaskForm](https://flask-wtf.readthedocs.io/en/0.15.x/quickstart/#validating-forms), [StringField and PasswordField](https://wtforms.readthedocs.io/en/2.3.x/fields),
[SubmitField](https://wtforms.readthedocs.io/en/2.3.x/fields/#wtforms.fields.SubmitField) and [Length, EqualTo, Email, DataRequired and ValidationError](https://wtforms.readthedocs.io/en/2.3.x/validators) to manipulate the input data.

To run the application, it is necessary to install all the modules and extensions mentioned above. In addition, you need arrows for the following environment variables:

For the Posix environment:
```bash
export FLASH_APP=run.py
export FLASH_ENV=development
```
More details at [CLI Flask](https://flask.palletsprojects.com/en/2.0.x/cli/)

Run the application via CLI:
```bash
$flask run
```

More details... [wiki](https://github.com/myplayareas/sysrepository/wiki)
