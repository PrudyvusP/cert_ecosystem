from flask import Flask
from flask_admin import Admin

from .commands import index
from .config import DevConfig, ProdConfig, TestConfig
from .extentions import db, babel, migrate
from .models import (Organization, Resource,
                     OrgAdmDoc, Message)
from .views.home_view import HomeView
from .views.message import MessageModelView
from .views.orgadmdoc import OrgAdmDocModelView
from .views.organization import OrganizationModelView
from .views.resource import ResourceModelView
from .views.workspace import WorkspaceView


def init_admin(app):
    admin = Admin(name='GP',
                  template_mode='bootstrap4',
                  url='/',
                  base_template='admin/custom_master.html',
                  index_view=HomeView(name='Главная',
                                      template='admin/index.html',
                                      url='/'))

    admin.init_app(app)

    admin.add_view(
        OrganizationModelView(
            Organization,
            db.session,
            name='Организации',
            category="Организации",
            endpoint='organizations')
    )

    admin.add_view(
        OrgAdmDocModelView(
            OrgAdmDoc,
            db.session,
            name='Документы',
            category="Организации",
            endpoint='documents')
    )

    admin.add_view(
        MessageModelView(
            Message,
            db.session,
            name='Письма',
            endpoint='messages')
    )

    admin.add_view(
        ResourceModelView(
            Resource,
            db.session,
            name='Информационные ресурсы',
            endpoint='resources')
    )

    admin.add_view(
        WorkspaceView(
            name='Поиск в ЕГРЮЛ',
            endpoint='workspace')
    )


def create_app():
    """Создает инстанс приложения."""

    conf_types = {'development': DevConfig,
                  'testing': TestConfig,
                  'production': ProdConfig}

    app = Flask(__name__)
    app.config.from_object(conf_types.get(app.config['ENV']))
    db.init_app(app)
    migrate.init_app(app, db)
    init_admin(app)
    babel.init_app(app)
    app.cli.add_command(index)

    @app.shell_context_processor
    def make_shell_context():
        return {'Organization': Organization, 'db': db}

    return app
