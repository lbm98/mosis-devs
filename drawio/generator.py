from jinja2 import Template

from drawio.parser import Parser


class Generator:
    def __init__(self, filename: str, parser: Parser):
        self.filename = filename
        self.parser = parser

    def generate(self):
        with open('./templates/experiment.py.jinja') as jj:
            template = Template(jj.read(), trim_blocks=True, lstrip_blocks=True)
            code = template.render(
                models=self.parser.models,
                connections=self.parser.connections,
                imports=self.parser.imports
            )
            with open('output/' + self.filename, 'w') as out:
                out.write(code)


