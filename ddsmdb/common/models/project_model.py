import datetime
from ..core import db
from ..models import UserModel
from ..models import ContainerModel
import json
from bson import ObjectId
          
class ProjectModel(db.Document):
    created_at = db.DateTimeField(default=datetime.datetime.now())
    owner = db.ReferenceField(UserModel, reverse_delete_rule=db.CASCADE, required=True)
    name = db.StringField(max_length=300, required=True)
    description = db.StringField(max_length=10000)
    goals = db.StringField(max_length=500)
    private = db.BooleanField(default=False)
    history = db.ListField(db.StringField(max_length=256))

    def clone(self):
        del self.__dict__['_id']
        del self.__dict__['_created']
        del self.__dict__['_changed_fields']
        self.id = ObjectId()

    def info(self):
        data = {'created':str(self.created_at), 'updated':str(self.last_updated), 'id': str(self.id), 
        'owner':str(self.owner.id), 'name': self.name, 'private':self.private, 
        'duration': str(self.duration), 'total_records':self.record_count,
        'total_diffs':self.diff_count}
        # data['status'] = self.status
        return data

    def to_json(self):
        data = self.info()
        data['goals'] = self.goals
        data['history'] = self.history
        data['description'] = self.description
        return data
        # return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
    
    def summary_json(self):
        data = self.info()
        data['goals'] = self.goals[0:96]+"..." if len(self.goals) >=100 else self.goals
        data['description'] = self.description[0:96]+"..." if len(self.description) >=100 else self.description
        data['history'] = len(self.history)
        return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))

    def activity_json(self):
        records_summary = [json.loads(r.summary_json()) for r in self.records]
        return json.dumps({'project':json.loads(self.summary_json()), "records":records_summary}, sort_keys=True, indent=4, separators=(',', ': '))
        # return json.dumps(self.summary_json(), sort_keys=True, indent=4, separators=(',', ': '))

    @property
    def record_count(self):
        return self.records.count()

    @property
    def diff_count(self):
        from ..models import DiffModel
        diffs = []
        for diff in DiffModel.objects():
            if diff.record_from.project == self:
                diffs.append(diff)
            if diff.record_to.project == self:
                diffs.append(diff)
        return len(diffs)
    @property
    def records(self):
        from ..models import RecordModel
        return RecordModel.objects(project=self)
    
    @property
    def last_updated(self):
        if self.record_count >0:
            return self.records.order_by('-updated_at').limit(1).first().updated_at
        else:
            return self.created_at

    @property
    def duration(self):
        if self.records == None or len(self.records) == 0:
            return 0
        else:
            # print str(self.records)
            
            # try:
            #     return self.records.sum('duration')
            # except:
            #     return 0.0
            try:
                last_updated_strp = datetime.datetime.strptime(str(self.last_updated), '%Y-%m-%d %H:%M:%S.%f')
            except:
                last_updated_strp = datetime.datetime.strptime(str(self.last_updated), '%Y-%m-%d %H:%M:%S')

            try:
                created_strp = datetime.datetime.strptime(str(self.created_at), '%Y-%m-%d %H:%M:%S.%f')
            except:
                created_strp = datetime.datetime.strptime(str(self.created_at), '%Y-%m-%d %H:%M:%S')

            print str(last_updated_strp-created_strp)
            return last_updated_strp-created_strp