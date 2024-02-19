import logging

from flask import Flask
from flask_admin import Admin

from .commands import index, notify, parse
from .config import DevConfig, ProdConfig, TestConfig
from .extentions import db, babel, migrate
from .models import (Cert, Organization, Message, MethodicalDoc, OrgAdmDoc,
                     Resource, Responsibility)
from .views import (CertModelView, HomeView, MessageModelView,
                    MethodDocModelView, OrgAdmDocModelView,
                    OrganizationModelView, ResourceModelView,
                    ResponseModelView, WorkspaceView)


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
        CertModelView(
            Cert,
            db.session,
            name="Центры мониторинга",
            category="Организации",
            endpoint='certs')
    )

    admin.add_view(
        ResourceModelView(
            Resource,
            db.session,
            name='Информационные ресурсы',
            category='Организации',
            endpoint='resources')
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
        ResponseModelView(
            Responsibility,
            db.session,
            name='Зоны ответственности',
            endpoint='responsibilities')
    )

    admin.add_view(
        WorkspaceView(
            name='Поиск в ЕГРЮЛ',
            endpoint='workspace')
    )

    admin.add_view(
        MethodDocModelView(
            MethodicalDoc,
            db.session,
            name='Методические материалы',
            endpoint='method-docs')
    )


def create_app():
    """Создает инстанс приложения."""

    conf_types = {'development': DevConfig,
                  'testing': TestConfig,
                  'production': ProdConfig}

    app = Flask(__name__)
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    app.config.from_object(conf_types.get(app.config['ENV']))
    db.init_app(app)
    migrate.init_app(app, db)
    init_admin(app)
    babel.init_app(app)
    app.cli.add_command(index)
    app.cli.add_command(notify)
    app.cli.add_command(parse)

    @app.shell_context_processor
    def make_shell_context():
        return {'Organization': Organization, 'db': db}

    return app
