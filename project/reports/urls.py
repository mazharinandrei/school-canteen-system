from django.urls import path
from . import views


app_name = "reports"

urlpatterns = [
    path(
        "nutrients-normative-report",
        views.render_nutrients_normative_report_first_page,
        name="nutrients_normative_report_first_page",
    ),
    path(
        "generate-nutrients-normative-report",
        views.render_nutrients_normative_report,
        name="generate_nutrients_normative_report",
    ),
    path(
        "cost-of-dishes-report",
        views.render_costs_of_dishes_report,
        name="cost_of_dishes_report",
    ),
    path(
        "abc-analysis-report",
        views.render_abc_analysis_report,
        name="abc_analysis_report",
    ),
    path(
        "abc-analysis-table", views.render_abc_analysis_table, name="abc_analysis_table"
    ),
]
