# Third part
from django.db import models


class SkillPerJobCategoryTable(models.Model):
    """
    This table store all scraped skills after analyzed them.
    """

    class Meta:
        ordering = ("-amount",)

    job_category = models.CharField(max_length=10)
    skill = models.CharField(max_length=40)
    amount = models.IntegerField(null=False)
