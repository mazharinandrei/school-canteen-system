class NotEnoughProductToTransfer(Exception):
    def __init__(
        self,
        warehouse_from_name: str = None,
        product_name: str = None,
        custom_message: str = None,
    ):
        self.warehouse_from_name = warehouse_from_name
        self.product_name = product_name
        self.custom_message = custom_message

    def __str__(self):
        if self.custom_message:
            return self.custom_message
        elif self.warehouse_from_name and self.product_name:
            return (
                f'There is not enough "{self.product_name}" product '
                f'in the "{self.warehouse_from_name}" warehouse to transfer'
            )


class NotEnoughProductToWriteOff(Exception):
    def __init__(
        self,
        warehouse_name: str = None,
        product_name: str = None,
        custom_message: str = None,
    ):
        self.warehouse_name = warehouse_name
        self.product_name = product_name
        self.custom_message = custom_message

    def __str__(self):
        if self.custom_message:
            return self.custom_message
        elif self.warehouse_name and self.product_name:
            return (
                f'There is not enough "{self.product_name}" product '
                f'in the "{self.warehouse_name}" warehouse to be written off'
            )
        else:
            return "Not enough product to write off"
