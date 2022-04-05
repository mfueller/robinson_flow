#!/usr/bin/env python3
from robinson.messaging.mqtt import MQTTConnection
from robinson.messaging.mqtt import MQTTConnection
from pymavlink.dialects.v20.ardupilotmega import MAVLink_message
from robinson.messaging.mqtt.serializer import Image, JsonTransform, NoTransform
# from vebas.taskplanner.types import Seedling, SeedlingsList
from robinson.messaging.mavlink import MavlinkConnection, get_mavlink_msg_args, get_mavlink_msg_class

from robinson_flow.logger import getLogger
import copy
from robinson.components import InstanceFilter, ComponentRunner, Composite

class EnvironmentConnector():

    def output_port(self, topic):
        raise NotImplementedError()

    def input_port(self, topic):
        raise NotImplementedError()

class MQTTConnector(EnvironmentConnector, Composite):
    def __init__(self, settings):
        Composite.__init__(self,"EnvironmentConnector")
        self.logger = getLogger(self)
        self.mqtt = MQTTConnection("mqtt", settings.server)

        self.add_component(self.mqtt)

    def output_port(self, topic):
        self.logger.info(f"connect {topic}")
        mqtt_port = self.mqtt.mqtt_output(topic)
        return mqtt_port

    def input_port(self, topic):
        self.logger.info(f"connect {topic}")
        mqtt_port = self.mqtt.mqtt_input(topic)
        return mqtt_port

class MavlinkConnector(EnvironmentConnector, Composite):

    def __init__(self, settings) -> None:
        Composite.__init__(self, "MavlinkConnector")
        self.mavlink = MavlinkConnection("mavlink")
        self.mavlink.config_update(**settings)
        self.add_component(self.mavlink)

    def input_port(self, topic):
        # return super().output_port(topic)
        return self.mavlink.dataport_input_mavlink_msg

    def output_port(self, topic):
        # return super().input_port(topic)
        cls = get_mavlink_msg_class(topic)
        mavlink_filter = InstanceFilter(cls)
        self.mavlink.dataport_output.connect(mavlink_filter)
        return mavlink_filter

class TopicRegistryItem():

    def __init__(self, protocol, topic_pattern, msg_type, transformer, *args, **kwargs) -> None:
        self.protocol = protocol
        self.topic_pattern = topic_pattern
        self.topic = None
        self.msg_type = msg_type
        self.transformer = transformer
        self.args = args
        self.kwargs = kwargs

    def create(self):
        return self.transformer(*self.args, **self.kwargs)

    def update_topic(self, *args, **kwargs):
        self.topic = self.topic_pattern.format(*args, **kwargs)


class TopicRegistry():

    registry = {}

    def __init__(self, default:TopicRegistryItem,  topic_mapping = {}) -> None:
        self.default_item:TopicRegistryItem = default
        self.registry = topic_mapping
        self.logger = getLogger(self)


    def find(self, key:str) -> TopicRegistryItem:
        import re

        for pattern, item in self.registry.items():
            match = re.fullmatch(pattern,key)

            if match:
                new_instance = copy.copy(item)
                new_instance.update_topic(*match.groups(),**match.groupdict())

                return new_instance

        new_instance = copy.copy(self.default_item)
        new_instance.update_topic(key)
        self.logger.warn(f"Using default port for {key} resulting in topic {new_instance.topic}")
        return new_instance


    def is_valid_topic(self, topic):
        return True if topic is not None and len(topic) > 0 else False


class ExternalConnectionHandler():

    def __init__(self, settings) -> None:
        self.logger = getLogger(self)
        self.config = settings

        self.connectors = {}

        self.connectors["mqtt"] = MQTTConnector(self.config.mqtt)
        self.connectors["mavlink"] = MavlinkConnector(self.config.mavlink)
        self.connectors["default"] = self.connectors["mqtt"]


        self.registry = {}
        self.registry[r"mavlink/(?P<name>.*)"] = TopicRegistryItem("mavlink", "{name}", MAVLink_message, NoTransform)
        self.registry[r"mavlink"] = TopicRegistryItem("mavlink", "mavlink_output", MAVLink_message, NoTransform)

        self.registry[r"uav_camera_down"] = TopicRegistryItem("mqtt", "vebas/uav/camera/image", Image, JsonTransform, Image)
        self.registry[r"tracking_image"] = TopicRegistryItem("mqtt", "vebas/uav/tracking/image", Image, JsonTransform, Image)
        # self.registry['vebas/**/image'] = TopicRegistryItem(Image, JsonTransform, Image)
        self.registry[r"seedling_position/(.*)"] = TopicRegistryItem("mqtt", "vebas/tracking/{0}", dict, JsonTransform)
        self.registry['vebas_seedlingslist'] = TopicRegistryItem("mqtt", "vebas/taskplanner/seedlings", dict, JsonTransform)
        self.registry['(.*)'] = TopicRegistryItem("mqtt", "{0}", dict, JsonTransform)

        default_item = TopicRegistryItem("mqtt", "NOT_DEFINED_{0}", dict, JsonTransform)
        self.topic_registry = TopicRegistry(default_item, self.registry)

        self.runner = ComponentRunner("external_connection_runner", self.connectors.values(), cycle_rate=50)
        self.runner.start()

    def external_source(self, topic):
        self.logger.info(f"exteral_source for topic {topic}")
        reg_item = self.topic_registry.find(topic)

        if reg_item.protocol in self.connectors:
            connector = self.connectors[reg_item.protocol]
            self.logger.debug(f"using protocol {reg_item.protocol} for topic {reg_item.topic}")
        else:
            connector = self.connectors["default"]
            self.logger.warn(f"could not find procotol connector for {reg_item.protocol}, using default {connector}")

        transformer = reg_item.create()
        connector.output_port(reg_item.topic).connect(transformer)
        return transformer

    def external_sink(self, topic):
        self.logger.info(f"exteral_sink for topic {topic}")
        reg_item = self.topic_registry.find(topic)

        if reg_item.protocol in self.connectors:
            connector = self.connectors[reg_item.protocol]
            self.logger.debug(f"using protocol {reg_item.protocol} for topic {reg_item.topic}")
        else:
            connector = self.connectors["default"]
            self.logger.warn(f"could not find procotol connector for {reg_item.protocol}, using default {connector}")

        transformer = reg_item.create()
        transformer.connect(connector.input_port(reg_item.topic))
        return transformer
