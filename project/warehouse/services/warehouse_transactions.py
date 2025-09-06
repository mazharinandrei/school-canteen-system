from django.utils.timezone import localtime

from ..models import Availability, WriteOff, ProductTransfer

from contracts.models import ContractComposition


def accept_to_warehouse(contract_id, product, volume, warehouse):
    availability, created = Availability.objects.get_or_create(product=product, warehouse=warehouse)
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


def write_off_from_warehouse(product, volume, warehouse, cause, note):
    print(product, volume, warehouse, cause, note)
    availability = get_availability_or_zero(product, warehouse)

    if is_volume_more_than_availability(product, warehouse, volume):
        raise Exception(
            f"На складе {warehouse} продукта {product} меньше, чем планируется списать")
    write_off = WriteOff.objects.create(product=product, volume=volume, warehouse=warehouse, cause=cause, note=note,
                                        datetime=localtime())
    print(write_off)
    availability.volume -= volume
    availability.save()
    print("Списание удалось!")
    return write_off


def product_transfer(warehouse_from, warehouse_to, product, volume, staff, note):

    if is_volume_more_than_availability(product, warehouse_from, volume):
        raise Exception(
            f"Недостаточно {product} для перемещения")

    ProductTransfer.objects.create(warehouse_from=warehouse_from,
                                   warehouse_to=warehouse_to,
                                   product=product,
                                   volume=volume,
                                   datetime=localtime(),
                                   staff=staff,
                                   note=note)

    availability_warehouse_from = get_availability_or_zero(product, warehouse_from)
    availability_warehouse_to = get_availability_or_zero(product, warehouse_to)

    if type(availability_warehouse_to) != Availability:
        availability_warehouse_to = Availability.objects.create(product=product, warehouse=warehouse_to, volume=0)

    availability_warehouse_from.volume -= volume
    availability_warehouse_to.volume += volume

    availability_warehouse_from.save()
    availability_warehouse_to.save()


