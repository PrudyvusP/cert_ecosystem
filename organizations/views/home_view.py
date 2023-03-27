from flask_admin import AdminIndexView


class HomeView(AdminIndexView):
    """View для главной страницы админки
    Создана, чтобы скрыть кнопку в меню."""
    pass
