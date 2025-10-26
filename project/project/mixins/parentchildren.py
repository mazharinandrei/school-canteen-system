from django.forms import inlineformset_factory
from django.db import transaction

from django import forms

class ParentChildrenMixin:
    """
    Создан для форм, в которых одновременно создаётся:
    - один объект parent_model
    - множество объектов children_model, имеющих ForeignKey на parent_model
    """
    parent_model = None
    child_model = None

    parent_form_class = None
    child_form_class = None

    formset_kwargs = {}

    template_name = "parent_form_and_children_formset.html"

    def get_formset_class(self):
        assert self.parent_model is not None, "Не задан parent_model"
        assert self.child_model is not None, "Не задан child_model"
        return inlineformset_factory(
            parent_model=self.parent_model,
            model= self.child_model,
            form=self.child_form_class,
            **self.formset_kwargs,
        )

    def get_formset(self):
        Formset = self.get_formset_class()
        Formset.deletion_widget = forms.HiddenInput
        if self.request.method == "POST":
            return Formset(
                data=self.request.POST,
                files=self.request.FILES,
                instance=self.object)
        
        else:
            return Formset(instance=self.object)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if "formset" not in kwargs:
            context["formset"] = self.get_formset()

        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context["formset"]
        if formset.is_valid():
            with transaction.atomic():
                self.object = form.save()
                formset.instance = self.object
                formset.save()
            return super().form_valid(form)
        else:
            return self.form_invalid(form)
        
    def form_invalid(self, form):
        context = self.get_context_data(
            form = form,
            formset = self.get_formset())
        return self.render_to_response(context)
    
    def get_model(self):
        assert self.parent_model is not None, "Не задан parent_model"
        return self.parent_model

    def get_queryset(self):
        return self.get_model()._default_manager.all()
    
    def get_form_class(self):
        assert self.parent_form_class is not None, "Не задан parent_form_class"
        return self.parent_form_class