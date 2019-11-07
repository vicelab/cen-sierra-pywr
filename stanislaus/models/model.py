from pywr.core import Model
from pywr.nodes import Storage

from .utils import prepare_planning_model

class Sierra(Model):

    def setup(self):
        super(Sierra).setup()

