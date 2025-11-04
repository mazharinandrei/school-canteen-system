from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView
from django.views.generic.detail import DetailView

from .mixins.parentchildren import ParentChildrenMixin


class ProjectBaseListView(PermissionRequiredMixin, ListView):
    """
    Базовый List View для всего приложения. Пагинация по 100 объектов.
    PermissionRequired: can view model.
    """

    paginate_by = 100
    template_name = "base_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.model._meta.verbose_name_plural
        return context

    def get_permission_name_for_model(self):
        app, model = self.model._meta.label.split(".")
        return f"{app}.view_{model.lower()}"

    def get_permission_required(self):
        return [self.get_permission_name_for_model()]


class ProjectBaseCreateView(PermissionRequiredMixin, CreateView):
    """
    Базовый Create View для всего приложения.
    PermissionRequired: can add model.
    """

    template_name = "base_form.html"
    fields = "__all__"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = f"Добавить {self.model._meta.verbose_name}"
        return context

    def get_permission_name_for_model(self):
        app, model = self.model._meta.label.split(".")
        return f"{app}.add_{model.lower()}"

    def get_permission_required(self):
        return [self.get_permission_name_for_model()]


class ProjectBaseDetailView(PermissionRequiredMixin, DetailView):
    """
    Базовый Detail View для всего приложения.
    PermissionRequired: can view model.
    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(self.object, "name"):
            context["title"] = self.object.name
        else:
            context["title"] = str(self.object)
        return context

    def get_permission_name_for_model(self):
        app, model = self.model._meta.label.split(".")
        return f"{app}.view_{model.lower()}"

    def get_permission_required(self):
        return [self.get_permission_name_for_model()]


class ParentChildrenCreateView(
    PermissionRequiredMixin, ParentChildrenMixin, CreateView
):
    """
    CreateView, наследующий классы ParentChildrenMixin, PermissionRequiredMixin и CreateView.
    Создан для страниц, в которых одновременно создаётся:
    - один объект parent_model
    - множество объектов children_model, имеющих ForeignKey на parent_model
    Permission Required: add_model
    """

    def get_context_data(self, **kwargs):
        """
        не знаю, где этому лучше быть. в классе createview или mixin
        """
        context = super().get_context_data(**kwargs)

        context["title"] = f"Добавить {self.parent_model._meta.verbose_name}"
        context["formset_title"] = f"{self.child_model._meta.verbose_name}:"
        return context

    def get_permission_name_for_model(self):
        app, parent_model_meta_name = self.parent_model._meta.label.split(".")
        return f"{app}.add_{parent_model_meta_name.lower()}"

    def get_permission_required(self):
        return [self.get_permission_name_for_model()]
