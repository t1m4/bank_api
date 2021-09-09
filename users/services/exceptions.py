class SmallBalanceException(Exception):
    def __init__(self, message: str, amount, sender_balance):
        self.error_message = message
        self.amount = amount
        self.sender_balance = sender_balance

    def __str__(self):
        return "{} {} > {}".format(self.error_message, self.amount, self.sender_balance)


class SenderReceiverEqualException(Exception):
    def __init__(self, message: str, sender, receiver):
        self.error_message = message
        self.sender = sender
        self.receiver = receiver

    def __str__(self):
        return "{} {} == {}".format(self.error_message, self.sender, self.receiver)
