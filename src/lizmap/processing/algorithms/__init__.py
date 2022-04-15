
from .AlgorithmProvider import  AlgorithmProvider

class Test:
    def __init__(self):
        pass


def WPSClassFactory( iface: 'WPSServerInterface' ) -> Test:

    iface.registerProvider( AlgorithmProvider() )
    return Test()


