from drawio.parser import Parser
from drawio.generator import Generator


def main():
    parser = Parser('canal.drawio')
    parser.parse()
    gen = Generator('canal_experiment.py', parser)
    gen.generate()


if __name__ == '__main__':
    main()
