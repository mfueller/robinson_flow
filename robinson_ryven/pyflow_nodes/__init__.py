PACKAGE_NAME = 'robinson'

from collections import OrderedDict
from PyFlow.UI.UIInterfaces import IPackage
from robinson_ryven.robinson_nodes.Exporters.DemoExporter import DemoExporter
from robinson_ryven.pyflow_nodes.Factories.UINodeFactory import createUINode

# Pins
from robinson_ryven.pyflow_nodes.Pins.DemoPin import DemoPin

# Function based nodes
# from robinson_ryven.pyflow_nodes.FunctionLibraries.DemoLib import DemoLib


# Tools
from robinson_ryven.pyflow_nodes.Tools.DemoShelfTool import DemoShelfTool
from robinson_ryven.pyflow_nodes.Tools.DemoDockTool import DemoDockTool

# Exporters
# from robinson_ryven.pyflow_nodes.Exporters.DemoExporter import DemoExporter

# Factories
# from robinson_ryven.pyflow_nodes.Factories.UIPinFactory import createUIPin
# from robinson_ryven.pyflow_nodes.Factories.UINodeFactory import createUINode
# from robinson_ryven.pyflow_nodes.Factories.PinInputWidgetFactory import getInputWidget
# Prefs widgets
from robinson_ryven.ryven_nodes.nodes.components import PrintOutputComponent, TestComponent

from robinson_ryven.pyflow_nodes.Nodes.ExternalNodes import ExternalSource
from robinson_ryven.pyflow_nodes.Nodes.BaseNode import AddHelloComponent, RobinsonPyFlowBase

_FOO_LIBS = {}
_NODES = {}
_PINS = {}
_TOOLS = OrderedDict()
_PREFS_WIDGETS = OrderedDict()
_EXPORTERS = OrderedDict()

# _FOO_LIBS[DemoLib.__name__] = DemoLib(PACKAGE_NAME)

_PINS[DemoPin.__name__] = DemoPin

_TOOLS[DemoShelfTool.__name__] = DemoShelfTool
_TOOLS[DemoDockTool.__name__] = DemoDockTool

_EXPORTERS[DemoExporter.__name__] = DemoExporter

_PREFS_WIDGETS["Demo"] = DemoPrefs

import inspect
from robinson.components import Component
import sys

def factory(cls):
    name = cls.__name__
    if name.endswith("Component"):
        name = name[:-len("Component")]

    print(f"generate component {name}:{cls}")
    class PyflowTemplateNode(RobinsonPyFlowBase):
        def __init__(self, name, uid=None):
            super().__init__(name, cls=cls, uid=uid)

    cl =  PyflowTemplateNode
    cl.__name__ = name

    return name, cl


def load_components_from_module(module):
    results =  []
    for name, obj in inspect.getmembers(module):
        if inspect.isclass(obj):
            if sys.modules[obj.__module__] == module:
                if issubclass(obj, Component):
                    results.append(obj)
    return results

def export_nodes():

    import vebas.tracking.components.cv #import CVVideoInput, RGB2HSV, BGR2HSV, RGB2BRG, BGR2RGB, ColoredCircleDetection, ImageView, DetectionOverlay, CV_HSVMask_View
    import vebas.tracking.components.control
    import vebas.tracking.components.filter
    import vebas.tracking.components.transform
    import vebas.tracking.kf_ctl_loop.components as kf_ctl

    component_list = []#TestComponent, PrintOutputComponent, AddComponent, RGB2HSV, BGR2HSV, RGB2BRG, BGR2RGB, DetectionOverlay, ColoredCircleDetection, MyPartial]

    # component_list.extend(load_components_from_module(vebas.tracking.components.cv))
    # component_list.extend(load_components_from_module(vebas.tracking.components.control))
    # component_list.extend(load_components_from_module(vebas.tracking.components.filter))
    # component_list.extend(load_components_from_module(vebas.tracking.components.transform))
    # component_list.extend(load_components_from_module(kf_ctl))

    # component_list.append(ExternalSource)
    component_list.append(AddHelloComponent)
    component_list.append(TestComponent)
    component_list.append(PrintOutputComponent)

    rob_comps = {k:v for k,v in [factory(c) for c in component_list]}

    other_comp = {}
    other_comp["ExternalSource"] = ExternalSource

    return {**rob_comps, **other_comp}

class robinson(IPackage):
	def __init__(self):
		super(robinson, self).__init__()

	@staticmethod
	def GetExporters():
		return _EXPORTERS

	@staticmethod
	def GetFunctionLibraries():
		return _FOO_LIBS

	@staticmethod
	def GetNodeClasses():
		return export_nodes()

	@staticmethod
	def GetPinClasses():
		return _PINS

	@staticmethod
	def GetToolClasses():
		return _TOOLS

	@staticmethod
	def UIPinsFactory():
		return None#createUIPin

	@staticmethod
	def UINodesFactory():
		return createUINode

	@staticmethod
	def PinsInputWidgetFactory():
		return getInputWidget

	@staticmethod
	def PrefsWidgets():
		return _PREFS_WIDGETS

