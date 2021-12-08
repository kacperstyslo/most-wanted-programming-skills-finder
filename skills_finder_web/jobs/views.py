# Third part
from django.views.generic import TemplateView


class JobsCategoriesView(TemplateView):
    """
    This view shows all jobs categories.
    """

    template_name = "jobs/jobs_categories_page.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["jobs_categories"] = ["backend", "big-data"]
        return context
