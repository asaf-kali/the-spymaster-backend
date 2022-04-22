from django.templatetags.static import static
from django.views.generic import RedirectView, TemplateView

from api.views import ViewContextMixin

icon_view = RedirectView.as_view(url=static("images/icon.png"))


class IndexView(TemplateView, ViewContextMixin):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user
        return context
