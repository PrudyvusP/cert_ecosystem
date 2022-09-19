from flask import Flask
from flask_admin import Admin

from cert_ecosystem.config import DevConfig, ProdConfig, TestConfig
from cert_ecosystem.organizations.commands import index
from cert_ecosystem.organizations.extentions import db, babel, migrate
from cert_ecosystem.organizations.models import (Organization, Resource,
                                                 OrgAdmDoc, Message)
from cert_ecosystem.organizations.views.home_view import HomeView
from cert_ecosystem.organizations.views.message import MessageModelView
from cert_ecosystem.organizations.views.orgadmdoc import OrgAdmDocModelView
from cert_ecosystem.organizations.views.organization import OrganizationModelView
from cert_ecosystem.organizations.views.resource import ResourceModelView
from cert_ecosystem.organizations.views.workspace import WorkspaceView


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


def create_app(config='dev'):
    """Создает инстанс приложения."""

    conf_types = {'dev': DevConfig,
                  'test': TestConfig,
                  'prod': ProdConfig}

    app = Flask(__name__)
    app.config.from_object(conf_types.get(config))
    db.init_app(app)
    migrate.init_app(app, db)
    init_admin(app)
    babel.init_app(app)
    app.cli.add_command(index)

    @app.shell_context_processor
    def make_shell_context():
        return {'Organization': Organization, 'db': db}

    return app
