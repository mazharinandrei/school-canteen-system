from dataclasses import dataclass


@dataclass
class NotEnoughProductToTransfer(Exception):
    warehouse_from_name: str = None
    product_name: str = None
    custom_message: str = None

    @property
    def message(self):
        if self.custom_message:
            return self.custom_message
        elif self.warehouse_from_name and self.product_name:
            return (
                f'There is not enough "{self.product_name}" product '
                f'in the "{self.warehouse_from_name}" warehouse to transfer'
            )
        return "There is not enough product in the warehouse to transfer"


@dataclass
class NotEnoughProductToWriteOff(Exception):
    warehouse_name: str = None
    product_name: str = None
    custom_message: str = None

    @property
    def message(self):
        if self.custom_message:
            return self.custom_message
        elif self.warehouse_name and self.product_name:
            return (
                f'There is not enough "{self.product_name}" product '
                f'in the "{self.warehouse_name}" warehouse to be written off'
            )
        else:
            return "There is not enough product to write off"
