from pywr.nodes import Domain, PiecewiseLink, Storage
from pywr.parameters import load_parameter, load_parameter_values


class Reservoir(Storage):
    """
    Like a storage node, only better
    """

    def __init__(self, *args, **kwargs):

        self.gauge = kwargs.pop("gauge", None)
        super(Reservoir, self).__init__(*args, **kwargs)

class PiecewiseReservoir(Storage):
    """
    Like a storage node, only better
    """

    def __init__(self, *args, **kwargs):

        self.gauge = kwargs.pop("gauge", None)
        super(PiecewiseReservoir, self).__init__(*args, **kwargs)

    @classmethod
    def load(cls, data, model):
        name = data.pop('name')
        num_inputs = int(data.pop('inputs', 1))
        num_outputs = int(data.pop('outputs', 1))

        if 'initial_volume' not in data and 'initial_volume_pc' not in data:
            raise ValueError('Initial volume must be specified in absolute or relative terms.')

        initial_volume = data.pop('initial_volume', 0.0)
        initial_volume_pc = data.pop('initial_volume_pc', None)
        max_volume = data.pop('max_volume')
        min_volume = data.pop('min_volume', 0.0)
        level = data.pop('level', None)
        area = data.pop('area', None)
        cost = data.pop('cost', 0.0)

        data.pop('type', None)
        # Create the instance
        node = cls(model=model, name=name, num_inputs=num_inputs, num_outputs=num_outputs, **data)

        # Load the parameters after the instance has been created to prevent circular
        # loading errors

        # Try to coerce initial volume to float.
        try:
            initial_volume = float(initial_volume)
        except TypeError:
            initial_volume = load_parameter_values(model, initial_volume)
        node.initial_volume = initial_volume
        node.initial_volume_pc = initial_volume_pc

        max_volume = load_parameter(model, max_volume)
        if max_volume is not None:
            node.max_volume = max_volume

        min_volume = load_parameter(model, min_volume)
        if min_volume is not None:
            node.min_volume = min_volume

        cost = load_parameter(model, cost)
        if cost is None:
            cost = 0.0
        node.cost = cost

        if level is not None:
            level = load_parameter(model, level)
        node.level = level

        if area is not None:
            area = load_parameter(model, area)
        node.area = area

        return node


class InstreamFlowRequirement(PiecewiseLink):
    """A river gauging station, with a minimum residual flow (MRF)
    """

    def __init__(self, *args, **kwargs):
        """Initialise a new RiverGauge instance
        Parameters
        ----------
        """
        # create keyword arguments for PiecewiseLink
        kwargs['cost'] = kwargs.pop('cost', [0.0, 0.0, 0.0])
        # kwargs['cost'].extend([0.0] * (3 - len(kwargs['cost'])))
        kwargs['max_flow'] = kwargs.pop('max_flow', [0.0, 0.0, 0.0])
        kwargs['max_flow'].append(None)
        try:
            assert (len(kwargs['cost']) == len(kwargs['max_flow']))
        except:
            raise

        super(InstreamFlowRequirement, self).__init__(*args, **kwargs)

    @classmethod
    def load(cls, data, model):
        cost = data.pop("cost", 0.0)
        min_flow = data.pop("min_flow", 0.0)
        min_flow_cost = data.pop("min_flow_cost", 0.0)
        max_flow = data.pop("max_flow", 0.0)
        max_flow_cost = data.pop("max_flow_cost", 0.0)

        if type(max_flow) == list:
            max_flow = [load_parameter(model, x) for x in max_flow]
        else:
            max_flow = [load_parameter(model, min_flow), load_parameter(model, max_flow)]

        if type(cost) == list:
            cost = [load_parameter(model, x) for x in cost]
        else:
            cost = [load_parameter(model, min_flow_cost),
                    load_parameter(model, 0.0),
                    load_parameter(model, max_flow_cost)]

        data['max_flow'] = max_flow
        data['cost'] = cost

        del data["type"]
        node = cls(model, **data)
        return node


# class Hydropower(PiecewiseLink):
#     """A river gauging station, with a minimum residual flow (MRF)
#     """
#
#     type = 'hydropower'
#     head = 0.0
#
#     def __init__(self, *args, **kwargs):
#         """Initialise a new Hydropower instance
#         Parameters
#         ----------
#         mrf : float
#             The minimum residual flow (MRF) at the gauge
#         mrf_cost : float
#             The cost of the route via the MRF
#         excess_cost : float
#             The cost of the other (constrained) route
#         unconstrained_cost : float
#             The cost of unconstrained flows (for RoR hydropower in a river)
#         turbine_capacity : float
#             The total capacity of the hydropower turbine
#         """
#         # create keyword arguments for PiecewiseLink
#         base_flow = kwargs.pop('base_flow', 0.0)
#         base_cost = kwargs.pop('base_cost', 0.0)
#         excess_cost = kwargs.pop('excess_cost', 0.0)
#         # turbine_capacity = kwargs.pop('turbine_capacity', None)
#         # unconstrained_cost = kwargs.pop('unconstrained_cost', 0.0)
#         # excess_capacity = None
#         # if turbine_capacity is not None:
#         #     base_flow = min(base_flow, turbine_capacity)
#         #     excess_capacity = turbine_capacity - base_flow
#         # if base_flow < 0.0:
#         #     base_flow = max(base_flow, 0.0)
#
#         max_flow = kwargs.pop('max_flow', None)
#
#         self.head = kwargs.pop('head', 0.0)
#
#         kwargs['cost'] = [base_cost, excess_cost]
#         kwargs['max_flow'] = [base_flow, None]
#         super(Hydropower, self).__init__(*args, **kwargs)
#
#         self.output.max_flow = max_flow
#
#     @classmethod
#     def load(cls, data, model):
#         base_flow = load_parameter(model, data.pop("base_flow", 0.0))
#         base_cost = load_parameter(model, data.pop("base_cost", 0.0))
#         excess_cost = load_parameter(model, data.pop("excess_cost", 0.0))
#         max_flow = load_parameter(model, data.pop("max_flow", None))
#         # turbine_capacity = load_parameter(model, data.pop("turbine_capacity", 0.0))
#         # unconstrained_cost = load_parameter(model, data.pop("unconstrained_cost", 0.0))
#         del (data["type"])
#         node = cls(model, max_flow=max_flow, base_flow=base_flow, base_cost=base_cost, excess_cost=excess_cost, **data)
#         return node


class PiecewiseHydropower(PiecewiseLink):
    """
    A piecewise hydropower plant.
    """

    _type = 'piecewisehydropower'

    def __init__(self, model, max_flow, **kwargs):
        """Initialise a new Hydropower instance
        Parameters
        ----------
        """

        if max_flow is None:
            raise ValueError("Hydropower max_flow must be provided.")

        head = kwargs.pop('head', None)  # Fixed head

        max_flows = kwargs.pop('max_flows', [])
        costs = kwargs.pop('costs', [])

        # Add an unconstrained block with a default cost of zero
        max_flows.append(None)
        if len(costs) < len(max_flows):
            costs.append(0.0)  # PiecewiseLink will raise an error if not same length

        kwargs['max_flow'] = max_flows
        kwargs['cost'] = costs

        super(PiecewiseHydropower, self).__init__(model, **kwargs)

        self.output.max_flow = max_flow
        self.head = head

    @classmethod
    def load(cls, data, model):
        max_flows = [load_parameter(model, c) for c in data.pop('max_flows', [])]
        costs = [load_parameter(model, c) for c in data.pop('costs', [])]
        max_flow = load_parameter(model, data.pop('max_flow', None))
        head = data.pop('head', 0.0)
        del (data["type"])
        node = cls(model, max_flow, max_flows=max_flows, costs=costs, head=head, **data)
        return node


class Hydropower(PiecewiseLink):
    """
    A hydropower plant.
    """

    _type = 'hydropower'

    def __init__(self, model, turbine_capacity=None, spinning_flow=0.0, spinning_cost=0.0, **kwargs):
        """Initialise a new Hydropower instance
        Parameters
        ----------
        """

        # if turbine_capacity is None:
        #     res_name = kwargs.get('name', '').split('/')[0]
        #     raise ValueError("Hydropower turbine_capacity must be provided for {}".format(res_name))

        head = kwargs.pop('head', None)  # Fixed head

        max_flows = kwargs.pop('max_flows', [])
        costs = kwargs.pop('costs', [])

        # Add an unconstrained block with a default cost of zero
        max_flows.append(None)
        if len(costs) < len(max_flows):
            costs.append(0.0)  # PiecewiseLink will raise an error if not same length

        kwargs['max_flow'] = max_flows
        kwargs['cost'] = costs

        super(Hydropower, self).__init__(model, **kwargs)

        self.output.max_flow = turbine_capacity
        self.turbine_capacity = turbine_capacity
        self.head = head
        self.spinning_flow = spinning_flow
        self.spinning_cost = spinning_cost

    @classmethod
    def load(cls, data, model):
        max_flow = data.pop('max_flow', data.pop('max_flows', None))
        if type(max_flow) == list:
            max_flows = max_flow
        else:
            max_flows = [max_flow]
        max_flows = [load_parameter(model, x) for x in max_flows]
        cost = data.pop('cost', data.pop('costs', None))
        if type(cost) == list:
            costs = cost
        else:
            costs = [cost]
        costs = [load_parameter(model, c) for c in costs]
        turbine_capacity = load_parameter(model, data.pop('turbine_capacity', None))
        head = data.pop('head', 0.0)
        spinning_flow = data.pop('spinning_flow', 0.0)
        spinning_cost = data.pop('spinning_cost', 0.0)
        param_type = data.pop('type')
        try:
            node = cls(model, turbine_capacity, spinning_flow, spinning_cost, max_flows=max_flows, costs=costs, head=head, **data)
        except:
            raise Exception('{} {} failed to load'.format(param_type, data['name']))
        return node


class PiecewiseInstreamFlowRequirement(PiecewiseLink):
    """
    A piecewise instream flow requirement, defined with:
    N costs and N - 1 requirements
    """

    _type = 'piecewiseinstreamflowrequirement'

    def __init__(self, model, **kwargs):
        """Initialize
        Parameters
        ----------
        """
        kwargs['max_flow'] = kwargs.pop('max_flow', [])
        kwargs['cost'] = kwargs.pop('cost', [])
        if len(kwargs['cost']) == 0:
            kwargs['cost'].append(0.0)
        if len(kwargs['max_flow']) < len(kwargs['cost']):
            kwargs['max_flow'].append(None)
        assert (len(kwargs['cost']) == len(kwargs['max_flow']))
        super(PiecewiseInstreamFlowRequirement, self).__init__(model, **kwargs)

    @classmethod
    def load(cls, data, model):
        max_flow = [load_parameter(model, c) for c in data.pop('max_flow', [])]
        cost = [load_parameter(model, c) for c in data.pop('cost', [0.0])]
        del (data["type"])
        node = cls(model, max_flow=max_flow, cost=cost, **data)
        return node
