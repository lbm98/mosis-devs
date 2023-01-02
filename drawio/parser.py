import xml.etree.ElementTree as ET
from dataclasses import dataclass
import inflection


@dataclass
class FQPort:
    """A fully qualified port"""
    port_name: str
    model_name: str


@dataclass
class Model:
    name: str
    class_name: str
    parameters: str


@dataclass
class Connection:
    source: FQPort
    target: FQPort


@dataclass
class Import:
    class_name: str
    filename: str


class Parser:
    def __init__(self, filename):
        self.filename = filename

        self.models: list[Model] = []
        self.connections: list[Connection] = []
        self.imports: list[Import] = []

        self.params_to_ignore = ['id', 'label', 'name', 'class_name']

    def parse(self):
        tree = ET.parse(self.filename)
        root = tree.getroot()

        # Store all ports (fully qualified)
        lookup = {}

        # Parse models (they all have parent='1')
        models = root.findall(".//object/mxCell[@parent='1']/..")
        for model in models:

            # Get parameters
            parameters = ""
            for param, value in model.attrib.items():
                if param not in self.params_to_ignore:
                    parameters += f", {param}={value}"

            self.models.append(Model(
                name=model.attrib['name'],
                class_name=model.attrib['class_name'],
                parameters=parameters
            ))

            # Parse ports (of a model)
            ports = root.findall(f".//object/mxCell[@parent='{model.attrib['id']}']/..")
            for port in ports:
                lookup[port.attrib['id']] = FQPort(
                    port_name=port.attrib['name'],
                    model_name=model.attrib['name']
                )

        # Get imports
        unique_class_names = set(m.class_name for m in self.models)
        for class_name in unique_class_names:
            self.imports.append(Import(
                class_name=class_name,
                # Convert class names in CamelCase to filenames in snake_case
                filename=inflection.underscore(class_name)
            ))

        # Parse connections (they all have edge='1')
        connections = root.findall(".//mxCell[@edge='1']")
        for conn in connections:
            self.connections.append(Connection(
                source=lookup[conn.attrib['source']],
                target=lookup[conn.attrib['target']]
            ))
