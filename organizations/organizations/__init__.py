import logging

from celery import Celery, Task
from flask import Flask
from flask_admin import Admin

from .commands import index, parse
from .config import DevConfig, ProdConfig, TestConfig
from .extentions import db, babel, migrate
from .models import (Cert, Organization, Message, MethodicalDoc, OrgAdmDoc,
                     Resource, Responsibility)
from .views import (CertModelView, HomeView, MessageModelView,
                    MethodDocModelView, OrgAdmDocModelView,
                    OrganizationModelView, ResourceModelView,
                    ResponseModelView, WorkspaceView)


def init_admin(app: Flask) -> None:
    admin = Admin(name='GP',
                  template_mode='bootstrap4',
                  url='/',
                  base_template='admin/custom_master.html',
                  index_view=HomeView(name='Главная',
                                      template='admin/index.html',
                                      url='/'))
    admin.init_app(app)
    views_to_register = [
        OrganizationModelView(Organization, db.session, name='Организации',
                              category="Организации",
                              endpoint='organizations'),
        CertModelView(Cert, db.session, name="Центры мониторинга",
                      category="Организации", endpoint='certs'),
        ResourceModelView(Resource, db.session, name='Информационные ресурсы',
                          category='Организации', endpoint='resources'),
        OrgAdmDocModelView(OrgAdmDoc, db.session, name='Документы',
                           category="Организации", endpoint='documents'),
        MessageModelView(Message, db.session, name='Письма',
                         endpoint='messages'),
        ResponseModelView(
            Responsibility, db.session, name='Зоны ответственности',
            endpoint='responsibilities'),
        MethodDocModelView(MethodicalDoc, db.session,
                           name='Методические '
                                'материалы', endpoint='method-docs'),
        WorkspaceView(name='Поиск в ЕГРЮЛ', endpoint='workspace')]
    admin.add_views(*views_to_register)


def create_celery(app: Flask) -> Celery:
    """Создает инстанс планировщика заданий."""

    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app


def create_app() -> Flask:
    """Создает инстанс приложения."""

    conf_types = {'development': DevConfig,
                  'testing': TestConfig,
                  'production': ProdConfig}

    app = Flask(__name__)
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    app.config.from_object(conf_types.get(app.config['ENV']))
    app.template_folder = app.config['TEMPLATES_PATH']
    app.static_folder = app.config['STATIC_PATH']
    create_celery(app)
    db.init_app(app)
    migrate.init_app(app, db)
    init_admin(app)
    babel.init_app(app)
    app.cli.add_command(index)
    app.cli.add_command(parse)

    @app.shell_context_processor
    def make_shell_context():
        return {'Organization': Organization, 'db': db}

    return app
