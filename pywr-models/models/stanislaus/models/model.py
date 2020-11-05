from pywr.core import Model
from pywr.nodes import Storage


class PlanningModel(Model):
    reservoirs = []
    mode = 'planning'

    def setup(self):
        super(PlanningModel, self).setup()
        self.reservoirs = [n.name for n in self.nodes if type(n) == Storage and '(storage)' not in n.name]


class SchedulingModel(Model):
    planning = None
    reservoirs = []
    mode = 'scheduling'

    def __init__(self, *args, **kwargs):
        planning_model_path = kwargs.pop('planning_model_path', None)
        if planning_model_path:
            self.planning = PlanningModel.load(planning_model_path, path=planning_model_path)

        super(SchedulingModel, self).__init__(*args, **kwargs)

    def setup(self):
        super(SchedulingModel, self).setup()
        self.reservoirs = [n.name for n in self.nodes if type(n) == Storage and '(storage)' not in n.name]
        if self.planning:
            self.planning.setup()

    @classmethod
    def loads(cls, *args, **data):
        return cls(*args, **data)
