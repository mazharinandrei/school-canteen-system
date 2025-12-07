from django.contrib import admin

from .models import Counterparty, Contract, ContractComposition


admin.site.register(Counterparty)
admin.site.register(Contract)
admin.site.register(ContractComposition)
