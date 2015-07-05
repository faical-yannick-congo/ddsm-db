from ..core import db
from ..models import ProjectModel
from ..models import ContainerModel
import datetime
import json
from bson import ObjectId

class RecordModel(db.Document):
    project = db.ReferenceField(ProjectModel, reverse_delete_rule=db.CASCADE, required=True)
    label = db.StringField(max_length=300)
    created_at = db.DateTimeField(default=datetime.datetime.now())
    updated_at = db.DateTimeField(default=datetime.datetime.now())
    system = db.DictField() # {''}
    program = db.DictField() # {'version_control':'git|hg|svn|cvs', 'scope':'local|remote', 'location':'hash|https://remote_version.com/repository_id'}
    inputs = db.ListField(db.DictField()) # [{}]
    outputs = db.ListField(db.DictField()) # [{}]
    dependencies = db.ListField(db.DictField())# [{}]
    possible_status = ["starting", "started", "paused", "finished", "crashed", "resumed", "running", "unknown"]
    status = db.StringField(default="unknown", choices=possible_status)
    container = db.ReferenceField(ContainerModel, reverse_delete_rule=db.CASCADE)

    def clone(self):
        del self.__dict__['_id']
        del self.__dict__['_created']
        del self.__dict__['_changed_fields']
        self.id = ObjectId()

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super(RecordModel, self).save(*args, **kwargs)
    
    def update_fields(self, data):
        for k, v in self._fields.iteritems():
            if not v.required:
                if k != 'created_at':
                        yield k, v
    
    def update(self, data):
        for k, v in self.update_fields(data):
            if k in data.keys():
                if k == 'created_at':
                    self.created_at = datetime.datetime.strptime(data[k], '%Y-%m-%d %X')
                else:
                    setattr(self, k, data[k])
                del data[k]
        self.save() 
        # print str(data)       
        if data:
            body, created = RecordBodyModel.objects.get_or_create(head=self)
            body.data.update(data)
            body.save()

    @property
    def body(self):
        return RecordBodyModel.objects(head=self).first()

    @property
    def duration(self):
        try:
            print str(datetime.datetime.strptime(str(self.updated_at), '%Y-%m-%d %H:%M:%S.%f')-datetime.datetime.strptime(str(self.created_at), '%Y-%m-%d %H:%M:%S.%f'))
            return datetime.datetime.strptime(str(self.updated_at), '%Y-%m-%d %H:%M:%S.%f')-datetime.datetime.strptime(str(self.created_at), '%Y-%m-%d %H:%M:%S.%f')
        except:
            print str(datetime.datetime.strptime(str(self.updated_at), '%Y-%m-%d %H:%M:%S')-datetime.datetime.strptime(str(self.created_at), '%Y-%m-%d %H:%M:%S'))
            return datetime.datetime.strptime(str(self.updated_at), '%Y-%m-%d %H:%M:%S')-datetime.datetime.strptime(str(self.created_at), '%Y-%m-%d %H:%M:%S')

    def info(self):
        data = {'updated':str(self.updated_at),
         'id': str(self.id), 'project':self.project.name, 
         'label': self.label, 'created':str(self.created_at), 'status' : self.status}
        return data

    def to_json(self):
        data = {}
        data['head'] = self.info()
        data['head']['program'] = self.program
        data['head']['system'] = self.system
        data['head']['inputs'] = self.inputs
        data['head']['outputs'] = self.outputs
        data['head']['dependencies'] = self.dependencies
        if self.body:
            data['body'] = self.body.info()
        if self.container:
            data['container'] = self.container.info()
        else:
            data['container'] = {}
        return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
    
    def summary_json(self):
        data = self.info()
        data['inputs'] = len(self.inputs)
        data['outputs'] = len(self.outputs)
        data['dependencies'] = len(self.dependencies)
        if self.container:
            data["container"] = True
        else:
            data['container'] = False
        return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))

class RecordBodyModel(db.Document):
    updated_at = db.DateTimeField(default=datetime.datetime.now())
    head = db.ReferenceField(RecordModel, reverse_delete_rule=db.CASCADE, unique=True)
    data = db.DictField()

    def info(self):
        data = {'updated':str(self.updated_at), 'id':str(self.id), 'content':self.data['data']}
        return data

    def to_json(self):
        data = {}
        data['body'] = self.info()
        data['head'] = json.loads(self.head.info())
        return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))

    def summary_json(self):
        data = {}
        data['body'] = self.info()
        data['head'] = json.loads(self.head.summary_json())
        # print "Data: "+str(data)
        return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))


        

