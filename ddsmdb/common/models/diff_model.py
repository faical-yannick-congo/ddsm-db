import datetime
from ..core import db
from ..models import UserModel
from ..models import RecordModel
import json
from bson import ObjectId
          
class DiffModel(db.Document):
    created_at = db.DateTimeField(default=datetime.datetime.now())
    sender = db.ReferenceField(UserModel, reverse_delete_rule=db.CASCADE, required=True)
    targeted = db.ReferenceField(UserModel, reverse_delete_rule=db.CASCADE, required=True)
    record_from = db.ReferenceField(RecordModel, reverse_delete_rule=db.CASCADE, required=True)
    record_to = db.ReferenceField(RecordModel, reverse_delete_rule=db.CASCADE, required=True)
    diff = db.DictField() #{'method':'default|visual|custom', 'specific1':'', ...}
    possible_proposition = ["repeated", "reproduced", "non-repeated", "non-reproduced"]
    proposition = db.StringField(default="repeated", choices=possible_proposition)
    possible_status = ["proposed", "agreed", "denied"]
    status = db.StringField(default="proposed", choices=possible_status)

    def clone(self):
        del self.__dict__['_id']
        del self.__dict__['_created']
        del self.__dict__['_changed_fields']
        self.id = ObjectId()

    def info(self):
        data = {'created':str(self.created_at), 'id': str(self.id), 
        'from':str(self.record_from.id), 'to': str(self.record_to.id), 'proposition':self.proposition, 
        'status': self.status}
        return data

    def to_json(self):
        data = self.info()
        data['sender'] = str(self.sender.id)
        data['targeted'] = str(self.targeted.id)
        data['diff'] = str(self.diff)
        return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
    
    def summary_json(self):
        data = self.info()
        return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))