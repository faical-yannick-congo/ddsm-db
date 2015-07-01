import datetime
from ..core import db
import json
from bson import ObjectId
          
class ContainerModel(db.Document):
    created_at = db.DateTimeField(default=datetime.datetime.now())
    possible_system = ["docker", "rocket", "kubernetes", "unknown"]
    system = db.StringField(default="unknown", choices=possible_system)
    version = db.DictField() #{'branch':'branch_name', commit':'tag', 'timestamp':''}
    image = db.DictField() #{'scope':'local|remote', 'location':'hash|https://container.host.com/id'}

    def clone(self):
        del self.__dict__['_id']
        del self.__dict__['_created']
        del self.__dict__['_changed_fields']
        self.id = ObjectId()

    def info(self):
        data = {'created':str(self.created_at), 'id': str(self.id), 
        'system':self.system, 'version': self.version, 'image':self.image}
        return data

    def to_json(self):
        data = self.info()
        return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))