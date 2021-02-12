class Request:
    def __init__(self):
        self.STATUS = {1: "Ended", 0: "Pending", 2: "Declined", 3: "Accepted", 4: "OnGoing", 5: "Cancelled"}
        self.tel_id = None
        self.tel_to = None
        self.status = 0

    def make(self, tel_id: int, tel_to: int, status: int):
        self.tel_id = tel_id
        self.tel_to = tel_to
        self.status = status
