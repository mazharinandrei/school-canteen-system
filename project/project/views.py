from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView
from django.views.generic.detail import DetailView

class ProjectBaseListView(PermissionRequiredMixin, ListView):
    """
    Базовый List View для всего приложения. Пагинация по 100 объектов.
    PermissionRequired: can view model.
    """
    paginate_by = 100
    template_name="base_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.model._meta.verbose_name_plural.title()
        return context
    
    def get_permission_name_for_model(self):
        app, model = self.model._meta.label.split('.')
        return f"{app}.view_{model.lower()}"
    
    def get_permission_required(self):
        print([self.get_permission_name_for_model()])
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
        context["title"] = f"Добавить {self.model._meta.verbose_name.capitalize()}"
        return context
    
    def get_permission_name_for_model(self):
        app, model = self.model._meta.label.split('.')
        return f"{app}.add_{model.lower()}"
    
    def get_permission_required(self):
        print([self.get_permission_name_for_model()])
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
        app, model = self.model._meta.label.split('.')
        return f"{app}.view_{model.lower()}"
    
    def get_permission_required(self):
        print([self.get_permission_name_for_model()])
        return [self.get_permission_name_for_model()]
