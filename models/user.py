class User:
    def __init__(self, tel_id: int) -> None:
        self.tel_id: int = tel_id
        self.name: str = "Not Provided"
        self.instagram_id: str = "Not Provided"
        self.gender: int = 0
        self.GENDER = {-1: "She/Her",
                       0: "Prefer Not To Say",
                       1: "He/Him", }
        self.batch: str = "Not Provided"
        self.askedName = True
        self.askedGender = True
        self.askedId = True
        self.askedBatch = True
        self.connected = 0
        self.askedSkill = True
        self.block = 0

    def set_name(self, name: str) -> None:
        self.name = name

    def set_gender(self, gender: int) -> None:
        self.gender = gender

    def set_id(self, inst_id: str) -> None:
        self.instagram_id = inst_id

    def set_batch(self, batch: str) -> None:
        self.batch = batch

    def make(self, name: str, gender: int, insta_id: str, batch: str):
        self.set_id(insta_id)
        self.set_name(name)
        self.set_gender(gender)
        self.set_batch(batch)
