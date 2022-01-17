from robinson_flow.pyflow_nodes.Robinson.Nodes.ExternalNodes import ExternalSink, ExternalSource
from robinson_flow.pyflow_nodes.Robinson.UI.UIExternalNode import UIExternalSink, UIExternalSource
from PyFlow.UI.Canvas.UINodeBase import UINodeBase


def createUINode(raw_instance):
    # if isinstance(raw_instance, DemoNode):
        # return UIDemoNode(raw_instance)
    if isinstance(raw_instance, ExternalSource):
        return UIExternalSource(raw_instance)
    if isinstance(raw_instance, ExternalSink):
        return UIExternalSink(raw_instance)

    return UINodeBase(raw_instance)
