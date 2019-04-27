from bmob import BmobObject


class FRUser:
    object_id = None

    def __init__(self, json):
        self.object_id = json.get('objectId')


class GarbageCan:
    object_id = None
    area_code = None
    block_code = None
    number = None
    latitude = None
    longitude = None
    max_volume = None

    def __init__(self, json):
        self.object_id = json.get('objectId')
        self.area_code = json.get('areaCode')
        self.block_code = json.get('blockCode')
        self.number = json.get('number')
        self.latitude = json.get('latitude')
        self.longitude = json.get('longitude')
        self.max_volume = json.get('maxVolume')


class RecyclerPlace:
    object_id = None
    recycler_user_id = None
    latitude = None
    longitude = None
    area_code = None
    block_code = None

    def __init__(self, json):
        self.object_id = json.get('objectId')
        self.recycler_user_id = json.get('recycler').get('objectId')
        self.latitude = json.get('latitude')
        self.longitude = json.get('longitude')
        self.area_code = json.get('areaCode')
        self.block_code = json.get('blockCode')


class GarbageRecord:
    object_id = None
    garbage_can_id = None
    time = None
    volume = None

    def __init__(self, json):
        self.object_id = json.get('objectId')
        self.garbage_can_id = json.get('garbageCan').get('objectId')
        self.time = json.get('time')
        self.volume = json.get('volume')


class RecycleInstruction:
    pass


class RecycleArrangement:
    pass
