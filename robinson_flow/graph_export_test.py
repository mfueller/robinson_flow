#!/usr/bin/env python3

import json
import yaml
import pickle

from pprint import pprint

from pydantic import BaseModel
from typing import Any, List
import traceback
import ipdb
    # def export_to_python(self):

    #     from io import StringIO
    #     buf = StringIO()

    #     buf.write("#!/usr/bin/env python3\n")
    #     buf.write("\n")
    #     buf.write("from robinson.components import ComponentRunner\n")
    #     buf.write("\n")

    #     for name, (module, classname) in self.import_modules.items():
    #         buf.write(f"from {module} import {classname} as {name}_component\n")

    #     buf.write("\n")
    #     for name, (module, classname) in self.components_init.items():
    #         buf.write(f"{name} = {name}_component('{name}')\n")

    #     buf.write("\n")

    #     for c in self.connections:
    #         buf.write(f"{c.from_name()}.{c.from_port()}.connect({c.to_name()}.{c.to_port()})\n")


    #     buf.write("\n")
    #     buf.write("\n")

    #     buf.write("runner = ComponentRunner('runner')\n")
    #     for name, fqn in self.components_init.items():
    #         buf.write(f"runner += {name}\n")

    #     buf.write("\n")
    #     buf.write(f"runner.run()\n")
    #     # print(buf.getvalue())

    #     # with open('testrun.py', mode='w') as f:
    #         # print(buf.getvalue(), file=f)

class CDir(BaseModel):
    from_node:Any = None
    from_idx:int = None
    to_node:Any = None
    to_idx:int = None


    def from_name(self):
        try:
            return self.from_node.name()
        except Exception as e:
            print(e, self.from_node)
            return "ERROR_from_name"

    def to_name(self):
        try:
            return self.to_node.name()
        except Exception as e:
            print(e, self.to_node)
            return "ERROR_to_name"

    def from_port(self):
        try:
            # return self.from_node["robinson"]["output_names"][self.from_idx - 2]
            return self.from_node.output_portname_by_index(self.from_idx)
        except Exception as e:
            print("Error from_port", e, self.from_node, self.from_idx)
            print(traceback.format_exc())
            return "ERROR"

    def to_port(self):
        try:
            # return self.to_node["robinson"]["input_names"][self.to_idx - 2]
            return self.to_node.input_portname_by_index(self.to_idx)

        except Exception as e:
            print("Error to_port", e, self.to_node, self.to_idx)
            print(traceback.format_exc())
            return "ERROR"


    def __repr__(self):
        # ipdb.set_trace()
        return f"Connection({self.from_name()}.{self.from_port()} -> {self.to_name()}.{self.to_port()})"


    # json.load(open("graph_export_test.py"), strict=False)
# with open("graph_export_test.py", "rb") as read_file:
   # data = json.load(read_file, strict=False)

# data = pickle.load(open("/home/matthias/src/pyflow/PyFlow/graph_export.pickle"))

data = yaml.load(open("/home/matthias/src/pyflow/PyFlow/graph_export.yaml"), Loader=yaml.CLoader)
# %%


class PortDefinition():

    def __init__(self, name, data):
        self.name = name
        self.data = data

    def __repr__(self):
        return f"<Port  {self.name}>"

class InputPortDefinition(PortDefinition):

    def __repr__(self):
        return f"<InputPort  {self.name}>"

class OutputPortDefinition(PortDefinition):

    def __repr__(self):
        return f"<OutputPort  {self.name}>"


class NodeDefinition():

    def __init__(self, name, data) -> None:
        self._name = name
        self.data = data

    def __getitem__(self, key):
        # print("__getitem__", key)
        if isinstance(key, int):
            return list(self.data)[key]

        return self.data[key]

    def name(self):
        return self._name

    def is_robinson(self,n):
        return "robinson" in n

    def is_compound(self, n):
        return "graphData" in n

    def is_external_source(self, n):
        return "type" in n and n["type"] == "ExternalSource"

    def is_external_sink(self, n):
        return "type" in n and n["type"] == "ExternalSink"

    def is_external(self, n):
        return self.is_external_sink(n) or self.is_external_source(n)

    def is_graph_input(self, n):
        return "type" in n and n["type"] == "graphInputs"

    def is_graph_output(self, n):
        return "type" in n and n["type"] == "graphOutputs"

    def is_graph_port(self, n):
        return self.is_graph_input(n) or self.is_graph_output(n)

    def _nodes(self):
        return self.data["nodes"]

    def robinson_nodes(self):
        nodes = [n for n in self._nodes() if self.is_robinson(n)]
        nodes = {n["uuid"]:NodeDefinition(n['name'],n) for n in nodes}
        return nodes

    def robinson_external_sources(self):
        nodes = [n for n in self._nodes() if self.is_external_source(n)]
        nodes = {n["uuid"]:ExternalSourceDefinition(n['name'],n) for n in nodes}
        return nodes

    def robinson_external_sinks(self):
        nodes = [n for n in self._nodes() if self.is_external_sink(n)]
        nodes = {n["uuid"]:ExternalSinkDefinition(n['name'],n) for n in nodes}
        return nodes

    def graph_outputs(self):
        nodes = [n for n in self._nodes() if self.is_graph_output(n)]
        # ipdb.set_trace()
        nodes = {n["uuid"]:GraphOutputDefinition(n['name'],self,n) for n in nodes}
        return nodes

    def graph_inputs(self):
        nodes = [n for n in self._nodes() if self.is_graph_input(n)]
        # ipdb.set_trace()
        nodes = {n["uuid"]:GraphInputDefinition(n['name'],self,n) for n in nodes}
        return nodes

    def compound_nodes(self):
        compounds = [n for n in self._nodes() if self.is_compound(n)]
        compounds = {n["uuid"]:CompositeDefinition(n["name"], n) for n in compounds}
        return compounds

    def computation_nodes(self):
        return {**self.robinson_nodes(), **self.compound_nodes()}

    # def external_nodes(self):
        # return {**self.robinson_nodes(), **self.compound_nodes()}

    def nodes(self):
        nodes = self.robinson_nodes()

        external_sources = self.robinson_external_sources()
        external_sinks = self.robinson_external_sinks()

        graph_inputs = self.graph_inputs()
        graph_outputs = self.graph_outputs()

        compounds = self.compound_nodes()

        nodes = {**nodes, **external_sources, **external_sinks, **graph_inputs, **graph_outputs, **compounds}

        return nodes

    def outputs(self):
        if "outputs" in self.data:
            return self.data["outputs"]
        return []

    def inputs(self):
        if "inputs" in self.data:
            return self.data["inputs"]
        return []

    def input_ports(self):
        ports = []
        for p in self.inputs():
            ports.append(InputPortDefinition(p["name"], p))

        return ports

    def output_ports(self):
        ports = []
        for p in self.outputs():
            ports.append(OutputPortDefinition(p["name"], p))

        return ports

    def robinson_def(self):
        if "robinson" in self.data:
            return self.data["robinson"]
        return {}

    def module(self):
        return self.robinson_def()["module"]

    def classname(self):
        return self.robinson_def()["class"]

    def input_portname_by_index(self, idx):
        return self.robinson_def()["input_names"][idx - 2]

    def output_portname_by_index(self, idx):
        return self.robinson_def()["output_names"][idx - 2]

    def __repr__(self) -> str:
        return f"<Node {self.name()}>"

class ExternalSourceDefinition(NodeDefinition):

    def topic(self):
        return self.data["topic"]

    def input_portname_by_index(self, idx):
        return f"ExternalSourceInput_{idx}"

    def output_portname_by_index(self, idx):
        return f"ExternalSourceOutput_{idx}"

class ExternalSinkDefinition(NodeDefinition):

    def topic(self):
        return self.data["topic"]

    def input_portname_by_index(self, idx):
        return f"ExternalSinkInput_{idx}"

    def output_portname_by_index(self, idx):
        return f"ExternalSinkOutput_{idx}"

class GraphInputDefinition(NodeDefinition):


    def __init__(self, name, compound, data) -> None:
        self._name = name
        self.compound = compound
        self.data = data

    def input_portname_by_index(self, idx):
        return f"NOT_IMPLEMENTED_GraphInput_Input_{idx}"

    def output_portname_by_index(self, idx):
        r = [n["name"] for n in self.data["outputs"] if n["pinIndex"] == idx]

        if len(r) > 0:
            return r[0]

        return f"NOT_FOUND_GraphInput_output_{idx}"

    def name(self):
        # ipdb.set_trace()
        return self.compound.name()

class GraphOutputDefinition(NodeDefinition):

    def __init__(self, name, compound, data) -> None:
        self._name = name
        self.compound = compound
        self.data = data

    def input_portname_by_index(self, idx):
        # pprint(self.data)
        r = [n["name"] for n in self.data["inputs"] if n["pinIndex"] == idx]

        # ipdb.set_trace()
        if len(r) > 0:
            return r[0]

        return f"GraphOutput_input_{idx}"

    def output_portname_by_index(self, idx):
        # pprint(self.data)
        return f"NOT_IMPLEMENTED_GraphOuput_output_{idx}"

    def name(self):
        # ipdb.set_trace()
        return self.compound.name()


class CompositeDefinition(NodeDefinition):

    def __init__(self, name, data):
        self._name = name
        self.data = data

    def __getitem__(self, key):
        # print("__getitem__", key)
        if isinstance(key, int):
            return list(self.data)[key]

        return self.data[key]

    def _nodes(self):

        try:
            return self.data["nodes"]
        except Exception as e:
            return self.data["graphData"]["nodes"]

    def module(self):
        return "composite_module"

    def classname(self):
        return "CompositeClass"

    def input_portname_by_index(self, idx):
        r = [n["name"] for n in self.data["inputs"] if n["pinIndex"] == idx]

        if len(r) > 0:
            return r[0]

        return f'UNKNOWN_{idx}'

    def output_portname_by_index(self, idx):
        r = [n["name"] for n in self.data["outputs"] if n["pinIndex"] == idx]

        if len(r) > 0:
            return r[0]

        return f'UNKNOWN_{idx}'


    def import_modules(self):

        import_modules = {}
        nodes = self.nodes()

        for uuid,n in nodes.items():
            component_name = n["name"]

            if self.is_robinson(n):
                # rob = n.robinson_def()
                module = n.module()
                classname = n.classname()
                fqn = f"{module}.{classname}"

                import_modules[component_name] = module, classname

            if self.is_compound(n):
                # print("Compound Node", n["name"])
                pass
            if self.is_external(n):
                # print("External Node", n["name"])
                pass

        return import_modules

    def connections(self):
        nodes = self.nodes()
        connections = []
        for uuid,n in nodes.items():
            out = n.outputs()

            for o in out:
                output_links = o["linkedTo"]
                if len(output_links) == 0:
                    continue

                for link in output_links:

                    from_node = n
                    from_idx = link["outPinId"]
                    # from_name = n["name"]
                    # from_port = rob["output_names"][from_idx - 2]
                    to_uuid = link["rhsNodeUid"]
                    to_idx = link['inPinId']
                    # try:
                    to_node = nodes[to_uuid]
                    # print("to_node", to_node)
                    connections.append(CDir(from_node=from_node, from_idx=from_idx, to_node=to_node, to_idx=to_idx))

        return connections



cd = CompositeDefinition("test",data)

cd.import_modules()

cd.connections()
cd.input_ports()
cd.output_ports()


# %%

cd.outputs()
cd.inputs()

list(cd.nodes().values())[0].output_ports()

cca = list(cd.nodes().values())[0]
cca
cca.input_ports()
cca.output_ports()

ccd = list(cd.compound_nodes().values())[0]
type(ccd)
ccd.inputs()
ccd.outputs()
ccd.connections()

ccd.input_ports()
ccd.output_ports()

cd.input_ports()
cd.output_ports()

cd

# %%
#
from io import StringIO
buf = StringIO()


# %%
import mako

from mako.template import Template
from mako.lookup import TemplateLookup

tmp = Template(filename="composite_def.py.tpl")

for c in cd.compound_nodes().values():
    print(tmp.render(base=c))

# print(tmp.render(base=cd))

# %%
tmp = Template(filename="composite_init.py.tpl")

print(tmp.render(base=cd))


# %%

tmp = Template(filename="components_import.py.tpl")

cd.nodes()
print(tmp.render(base=cd))


# %%


tmp = Template(filename="components_init.py.tpl")

cd.nodes()
print(tmp.render(base=cd))

# %%
tmp = Template(filename="connections_init.py.tpl")

print(tmp.render(base=cd))

# cd.connections()

# %%

tmp = Template(filename="runner_init.py.tpl")

print(tmp.render(base=cd))


# %%
mylookup = TemplateLookup(directories=["."])
tmp = mylookup.get_template("main.py.tpl")

print(tmp.render(base=cd))
