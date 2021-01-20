
class PickUp:
    is_pickup = True
    is_dropoff = False

    def __init__(self, loc, request):
        self.loc = loc
        self.request = request


class DropOff:
    is_pickup = False
    is_dropoff = True

    def __init__(self, loc, request):
        self.loc = loc
        self.request = request


