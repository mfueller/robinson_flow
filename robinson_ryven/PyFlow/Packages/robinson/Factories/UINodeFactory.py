from robinson_ryven.PyFlow.Packages.robinson.Nodes.ExternalNodes import ExternalSource
from robinson_ryven.PyFlow.Packages.robinson.UI.UIExternalNode import UIExternalSource
from PyFlow.UI.Canvas.UINodeBase import UINodeBase


def createUINode(raw_instance):
    # if isinstance(raw_instance, DemoNode):
        # return UIDemoNode(raw_instance)
    if isinstance(raw_instance, ExternalSource):
        return UIExternalSource(raw_instance)
        # return UINodeBase(raw_instance)

    return UINodeBase(raw_instance)
