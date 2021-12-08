# Third part
from django.views.generic import TemplateView

# Own
from jobs.models import SkillPerJobCategoryTable


class MostWantedSkillsView(TemplateView):
    """
    This view show most wanted skills based on job category.
    """

    template_name = "charts/chart.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context[
            "skill_per_job_category"
        ] = SkillPerJobCategoryTable.objects.filter(
            job_category=self.request.GET.get("job-category")
        )[
            :40
        ]
        return context
