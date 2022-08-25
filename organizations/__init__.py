from flask import Flask
from flask_admin import Admin

from config import DevConfig, ProdConfig, TestConfig
from .commands import index
from .extentions import db, babel, migrate
from .models import (Organization, Resource, OrgAdmDoc,
                     Message)
from .views import (OrgAdmDocModelView, MessageModelView,
                    OrganizationModelView, ResourceModelView, HomeView)
from api import api_bp


def init_admin(app):
    admin = Admin(name='GP',
                  template_mode='bootstrap4',
                  url='/',
                  index_view=HomeView(name='Главная',
                                      template='admin/index.html',
                                      url='/'))

    admin.init_app(app)

    admin.add_view(
        OrganizationModelView(
            Organization,
            db.session,
            name='Организации',
            category="Организации")
    )

    admin.add_view(
        OrgAdmDocModelView(
            OrgAdmDoc,
            db.session,
            name='Документы',
            category="Организации")
    )

    admin.add_view(
        MessageModelView(
            Message,
            db.session,
            name='Письма')
    )

    admin.add_view(
        ResourceModelView(
            Resource,
            db.session,
            name='Информационные ресурсы')
    )


def create_app(config='test'):
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
    app.register_blueprint(api_bp, url_prefix='/api')

    @app.shell_context_processor
    def make_shell_context():
        return {'Organization': Organization, 'db': db}

    return app
