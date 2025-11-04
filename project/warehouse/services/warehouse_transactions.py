from django.db import transaction
from django.utils.timezone import localtime

from main.models import MenuRequirement
from staff.models import Staff
from ..exceptions import NotEnoughProductToWriteOff, NotEnoughProductToTransfer
from ..models import Availability, WriteOff, ProductTransfer, Warehouse, WriteOffCause

from contracts.models import ContractComposition


def accept_to_warehouse(contract_id, product, volume, warehouse):
    availability, created = Availability.objects.get_or_create(
        product=product, warehouse=warehouse
    )
    availability.volume += volume
    availability.save()

    cp = ContractComposition.objects.get(contract=contract_id, product=product)
    cp.received_volume += volume
    cp.save()


def get_availability_or_zero(product, warehouse):
    try:
        return Availability.objects.get(product=product, warehouse=warehouse)
    except Availability.DoesNotExist:
        return 0


def is_volume_more_than_availability(product, warehouse, volume):
    availability = get_availability_or_zero(product, warehouse)
    if type(availability) == Availability:
        return availability.volume < volume
    else:
        return availability < volume


def write_off_from_warehouse(product, volume, warehouse, cause, created_by, note):
    availability = get_availability_or_zero(product, warehouse)

    if is_volume_more_than_availability(product, warehouse, volume):
        raise NotEnoughProductToWriteOff(
            warehouse_name=warehouse.name, product_name=product.name
        )

    write_off = WriteOff.objects.create(
        product=product,
        volume=volume,
        warehouse=warehouse,
        cause=cause,
        note=note,
        datetime=localtime(),
        staff=created_by,
    )

    availability.volume -= volume
    availability.save()

    return write_off


def product_transfer(warehouse_from, warehouse_to, product, volume, staff, note):
    if is_volume_more_than_availability(product, warehouse_from, volume):
        raise NotEnoughProductToTransfer(
            warehouse_from_name=warehouse_from, product_name=product
        )

    ProductTransfer.objects.create(
        warehouse_from=warehouse_from,
        warehouse_to=warehouse_to,
        product=product,
        volume=volume,
        datetime=localtime(),
        staff=staff,
        note=note,
    )

    availability_warehouse_from = get_availability_or_zero(product, warehouse_from)
    availability_warehouse_to = get_availability_or_zero(product, warehouse_to)

    if type(availability_warehouse_to) != Availability:
        availability_warehouse_to = Availability.objects.create(
            product=product, warehouse=warehouse_to, volume=0
        )

    availability_warehouse_from.volume -= volume
    availability_warehouse_to.volume += volume

    availability_warehouse_from.save()
    availability_warehouse_to.save()


@transaction.atomic
def issue_menu(
    created_by: Staff,
    menu: MenuRequirement | int,
    from_warehouse_name: str,
    to_warehouse_name: str = "Кухня",
    note: str = None,
):
    if not isinstance(menu, MenuRequirement):
        menu = MenuRequirement.objects.get(pk=menu)

    warehouse_from, _ = Warehouse.objects.get_or_create(name=from_warehouse_name)
    warehouse_to, _ = Warehouse.objects.get_or_create(name=to_warehouse_name)

    if note is None:
        note = f'Отпуск продукта на кухню по "{menu}"'

    for menu_position in menu.composition.all():
        tm = menu_position.dish.get_actual_technological_map()
        for tm_position in tm.composition.all():
            product_transfer(
                warehouse_from=warehouse_from,
                warehouse_to=warehouse_to,
                product=tm_position.product,
                volume=menu_position.volume_per_student * menu.students_number / 1000,
                staff=created_by,
                note=note,
            )
    menu.is_issued = True
    menu.save()


@transaction.atomic
def cook_menu(
    created_by: Staff,
    menu: MenuRequirement | int,
    note: str = None,
    warehouse_name: str = "Кухня",
    cause_name: str = "Приготовление блюд",
):
    if not isinstance(menu, MenuRequirement):
        menu = MenuRequirement.objects.get(pk=menu)

    warehouse, _ = Warehouse.objects.get_or_create(name=warehouse_name)
    cause, _ = WriteOffCause.objects.get_or_create(name=cause_name)

    if note is None:
        note = f'Списание продукта по "{menu}"'

    for menu_position in menu.composition.all():
        tm = menu_position.dish.get_actual_technological_map()
        for tm_position in tm.composition.all():
            write_off_from_warehouse(
                warehouse=warehouse,
                product=tm_position.product,
                volume=menu_position.volume_per_student * menu.students_number / 1000,
                cause=cause,
                note=note,
                created_by=created_by,
            )

    menu.is_cooked = True
    menu.save()
