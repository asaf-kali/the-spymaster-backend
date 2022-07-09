from django.templatetags.static import static
from django.views.generic import RedirectView, TemplateView

icon_view = RedirectView.as_view(url=static("images/icon.png"))


class IndexView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user
        return context
