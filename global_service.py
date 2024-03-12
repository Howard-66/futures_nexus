import dataworks

class GlobalService:
    def __init__(self) -> None:
        self.variety_id_name_map = None
        self.variety_name_id_map = None
        self.dataworks = dataworks.DataWorks()
        self.variety_id_name_map, self.variety_name_id_map = self.dataworks.get_variety_map()

gs = GlobalService()