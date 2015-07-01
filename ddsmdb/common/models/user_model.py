import datetime
from ..core import db
import json
import hashlib

class UserModel(db.Document):
    created_at = db.DateTimeField(default=datetime.datetime.now())
    email = db.StringField(max_length=120, required=True, unique=True)
    api_token = db.StringField(max_length=256, default=hashlib.sha256(b'DDSM%s_%s'%(email, str(created_at))).hexdigest(), unique=True)
    session = db.StringField(max_length=256, default=hashlib.sha256(b'Session%s_%s'%(email, str(created_at))).hexdigest(), unique=True)

    def __repr__(self):
        return '<User %r>' % (self.email)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.id)  # python 2
        except NameError:
            return str(self.id)  # python 3

    def renew(self, unic):
        self.session = hashlib.sha256(b'Session%s_%s'%(self.email, unic)).hexdigest()
        self.save()

    def retoken(self):
        self.api_token = hashlib.sha256(b'DDSM%s_%s'%(email, str(datetime.datetime.now()))).hexdigest()
        self.save()

    def allowed(self, unic):
        return hashlib.sha256(b'Session%s_%s'%(self.email, unic)).hexdigest()

    def to_json(self):
        return json.dumps({'created':str(self.created_at), 'id': str(self.id), 'email' : self.email, 'total_projects' : len(self.projects), 'total_duration':self.duration, 'total_records':self.record_count}, sort_keys=True, indent=4, separators=(',', ': '))

    def activity_json(self, admin=False):
        projects_summary = [json.loads(p.summary_json()) for p in self.projects if not p.private or admin]
        return json.dumps({'user':json.loads(self.to_json()), 'projects' : projects_summary}, sort_keys=True, indent=4, separators=(',', ': '))

    @property
    def projects(self):
        from ..models import ProjectModel
        return ProjectModel.objects(owner=self)

    @property
    def records(self):
        records = []
        for project in self.projects:
            records += project.records
        return records

    @property
    def quota(self):
        occupation = 0
        for project in self.projects:
            for record in project.records:
                occupation += record.image['size']
        return occupation
    
    @property
    def record_count(self):
        return sum([p.record_count for p in self.projects])

    @property
    def duration(self):
        try:
            return sum([p.duration for p in self.projects])
        except:
            return 0.0


            
