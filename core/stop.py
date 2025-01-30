#! ./.venv/bin/python

from net import Net
from mininet.log import setLogLevel


def main():
    setLogLevel('info')
    n = Net("topologyzoo/Aarnet.gml")
    try:
        n.stop_net()
    except KeyboardInterrupt:
        n.stop_all()

if __name__ == '__main__':
    main()


