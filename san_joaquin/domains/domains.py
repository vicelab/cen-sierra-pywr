from pywr.nodes import Domain, PiecewiseLink
from pywr.parameters import load_parameter

DEFAULT_RIVER_DOMAIN = Domain(name='river', color='#33CCFF')


class RiverDomainMixin(object):
    def __init__(self, *args, **kwargs):
        # if 'domain' not in kwargs:
        #     kwargs['domain'] = DEFAULT_RIVER_DOMAIN
        # if 'color' not in kwargs:
        #     self.color = '#6ECFF6'  # blue
        super(RiverDomainMixin, self).__init__(*args, **kwargs)


class InstreamFlowRequirement(RiverDomainMixin, PiecewiseLink):
    """A river gauging station, with a minimum residual flow (MRF)
    """

    def __init__(self, *args, **kwargs):
        """Initialise a new RiverGauge instance
        Parameters
        ----------
        mrf : float
            The minimum residual flow (MRF) at the gauge
        mrf_cost : float
            The cost of the route via the MRF
        unconstrained_cost : float
            The cost of the other (unconstrained) route
        """
        # create keyword arguments for PiecewiseLink
        kwargs['cost'] = [kwargs.pop('mrf_cost', 0.0), kwargs.pop('unconstrained_cost', 0.0)]
        kwargs['max_flow'] = [kwargs.pop('mrf', 0.0), None]
        super(InstreamFlowRequirement, self).__init__(*args, **kwargs)

    def mrf():
        def fget(self):
            return self.sublinks[0].max_flow

        def fset(self, value):
            self.sublinks[0].max_flow = value

        return locals()

    mrf = property(**mrf())

    def mrf_cost():
        def fget(self):
            return self.sublinks[0].cost

        def fset(self, value):
            self.sublinks[0].cost = value

        return locals()

    mrf_cost = property(**mrf_cost())

    def unconstrained_cost():
        def fget(self):
            return self.sublinks[0].cost

        def fset(self, value):
            self.sublinks[0].cost = value

        return locals()

    unconstrained_cost = property(**unconstrained_cost())

    @classmethod
    def load(cls, data, model):
        mrf = load_parameter(model, data.pop("mrf", 0.0))
        mrf_cost = load_parameter(model, data.pop("mrf_cost", 0.0))
        unconstrained_cost = load_parameter(model, data.pop("unconstrained_cost", 0.0))
        del data["type"]
        node = cls(model, mrf=mrf, mrf_cost=mrf_cost, unconstrained_cost=unconstrained_cost, **data)
        return node


class Hydropower(RiverDomainMixin, PiecewiseLink):
    """A river gauging station, with a minimum residual flow (MRF)
    """

    def __init__(self, *args, **kwargs):
        """Initialise a new Hydropower instance
        Parameters
        ----------
        mrf : float
            The minimum residual flow (MRF) at the gauge
        mrf_cost : float
            The cost of the route via the MRF
        excess_cost : float
            The cost of the other (constrained) route
        unconstrained_cost : float
            The cost of unconstrained flows (for RoR hydropower in a river)
        turbine_capacity : float
            The total capacity of the hydropower turbine
        """
        # create keyword arguments for PiecewiseLink
        base_flow = kwargs.pop('base_flow', 0.0)
        base_cost = kwargs.pop('base_cost', 0.0)
        excess_cost = kwargs.pop('excess_cost', 0.0)
        # turbine_capacity = kwargs.pop('turbine_capacity', None)
        # unconstrained_cost = kwargs.pop('unconstrained_cost', 0.0)
        # excess_capacity = None
        # if turbine_capacity is not None:
        #     base_flow = min(base_flow, turbine_capacity)
        #     excess_capacity = turbine_capacity - base_flow
        # if base_flow < 0.0:
        #     base_flow = max(base_flow, 0.0)
        kwargs['cost'] = [base_cost, excess_cost]
        kwargs['max_flow'] = [base_flow, None]
        super(Hydropower, self).__init__(*args, **kwargs)

    def base_flow():
        def fget(self):
            if self.sublinks[1].max_flow is None:
                return self.sublinks[0].max_flow
            else:
                return min(self.sublinks[1].max_flow, self.sublinks[0].max_flow)

        def fset(self, value):
            if self.sublinks[1].max_flow is None:
                self.sublinks[0].max_flow = value
            else:
                if self.sublinks[0].max_flow is None:
                    capacity = self.sublinks[1].max_flow
                else:
                    capacity = self.sublinks[0].max_flow + self.sublinks[1].max_flow
                self.sublinks[0].max_flow = min(capacity, value)
                self.sublinks[1].max_flow = capacity - self.sublinks[0].max_flow
                if self.sublinks[0].max_flow < 0:
                    raise Exception("Hydropower base flow cannot be negative.")

        return locals()

    base_flow = property(**base_flow())

    def base_cost():
        def fget(self):
            return self.sublinks[0].cost

        def fset(self, value):
            self.sublinks[0].cost = value

        return locals()

    base_cost = property(**base_cost())

    def turbine_capacity():
        def fget(self):
            return self.sublinks[0].max_flow + self.sublinks[1].max_flow

        def fset(self, value):
            if self.sublinks[0].max_flow is None:
                self.sublinks[0].max_flow = 0.0
                self.sublinks[1].max_flow = value
            else:
                self.sublinks[0].max_flow = min(self.sublinks[0].max_flow, value) if value in [int, float] else value
                self.sublinks[1].max_flow = max(value - self.sublinks[0].max_flow, 0.0)

        return locals()

    turbine_capacity = property(**turbine_capacity())

    def excess_cost():
        def fget(self):
            return self.sublinks[1].cost

        def fset(self, value):
            self.sublinks[1].cost = value

        return locals()

    excess_cost = property(**excess_cost())

    def unconstrained_cost():
        def fget(self):
            return self.sublinks[2].cost

        def fset(self, value):
            self.sublinks[2].cost = value

        return locals()

    unconstrained_cost = property(**unconstrained_cost())

    @classmethod
    def load(cls, data, model):
        base_flow = load_parameter(model, data.pop("base_flow", 0.0))
        base_cost = load_parameter(model, data.pop("base_cost", 0.0))
        excess_cost = load_parameter(model, data.pop("excess_cost", 0.0))
        # turbine_capacity = load_parameter(model, data.pop("turbine_capacity", 0.0))
        # unconstrained_cost = load_parameter(model, data.pop("unconstrained_cost", 0.0))
        del (data["type"])
        node = cls(model, base_flow=base_flow, base_cost=base_cost, excess_cost=excess_cost, **data)
        return node


class PiecewiseHydropower(RiverDomainMixin, PiecewiseLink):
    """A river gauging station, with a minimum residual flow (MRF)
    """

    def __init__(self, *args, **kwargs):
        """Initialise a new Hydropower instance
        Parameters
        ----------
        """
        kwargs['max_flow'] = kwargs.pop('max_flow', [None])
        kwargs['cost'] = kwargs.pop('cost', [0.0])
        super(PiecewiseHydropower, self).__init__(*args, **kwargs)

    def max_flow():
        def fget(self):
            return [self.sublinks[i].max_flow for i in self.sublinks]

        def fset(self, value):
            for i, v in enumerate(value):
                self.sublinks[i].max_flow = v

        return locals()

    max_flow = property(**max_flow())

    def cost():
        def fget(self):
            return [self.sublinks[i].cost for i in self.sublinks]

        def fset(self, value):
            for i, v in enumerate(value):
                self.sublinks[i].cost = v

        return locals()

    cost = property(**cost())

    @classmethod
    def load(cls, data, model):
        max_flow = load_parameter(model, data.pop("max_flow", [None]))
        cost = load_parameter(model, data.pop("cost", [0.0]))
        del (data["type"])
        node = cls(model, max_flow=max_flow, cost=cost, **data)
        return node
