import traceback
from datetime import datetime
from PyFlow.UI.UIInterfaces import IDataExporter
from PyFlow.Core.version import Version

from robinson_flow.pyflow_nodes.Robinson.Exporters.python_exporter import CompositeDefinition
from io import StringIO
from mako.lookup import TemplateLookup
import pathlib
import inspect
import toml

class RobinsonExporter(IDataExporter):
    """docstring for DemoExporter."""

    def __init__(self):
        super(RobinsonExporter, self).__init__()

    @staticmethod
    def createImporterMenu():
        return True

    @staticmethod
    def creationDateString():
        return datetime.now().strftime("%I:%M%p on %B %d, %Y")

    @staticmethod
    def version():
        return Version(1, 0, 0)

    @staticmethod
    def toolTip():
        return "Robinson Export/Import."

    @staticmethod
    def displayName():
        return "Robinson exporter"

    @staticmethod
    def doImport(pyFlowInstance):
        pass

    @staticmethod
    def doExport(instance):

        try:
            data = instance.graphManager.man.serialize()

            python_filename = f"{instance._currentFileName}.py"
            pf = pathlib.Path(python_filename)

            name = pf.name[:pf.name.rfind('.')]
            base = CompositeDefinition(name, data)

            this_folder = pathlib.Path(inspect.getfile(RobinsonExporter)).parent
            template_folder = this_folder / "templates"

            mylookup = TemplateLookup(directories=[template_folder])
            tmp = mylookup.get_template("main.py.tpl")

            buf = StringIO()
            buf.write(tmp.render(base=base))

            with open(python_filename,"w") as fh:
                fh.write(buf.getvalue())


            #TODO read robinson data
            # with open(cfg_filename,"w") as fh:
                # fh.write(buf.getvalue())

            node_configs = {}

            for uuid, node in base.nodes().items():
                cfg = node.config()

                if len(cfg) > 0:
                    node_configs[node.name()] = cfg

            project_cfg = {}

            project_cfg["components"] = node_configs

            cfg_filename = f"{instance._currentFileName}.toml"
            toml.dump(project_cfg, open(cfg_filename, "w"))

        except Exception as e:
            print("Error while exporting graph")
            print(traceback.format_exception(e))
