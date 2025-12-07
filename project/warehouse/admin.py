from django.contrib import admin

from .models import (
    Warehouse,
    Acceptance,
    WriteOff,
    Availability,
    WriteOffCause,
    FactAvailability,
    ProductTransfer,
    ProductLimit,
)

admin.site.register(Warehouse)
admin.site.register(Acceptance)
admin.site.register(WriteOffCause)
admin.site.register(WriteOff)
admin.site.register(Availability)
admin.site.register(ProductTransfer)
admin.site.register(FactAvailability)
admin.site.register(ProductLimit)
