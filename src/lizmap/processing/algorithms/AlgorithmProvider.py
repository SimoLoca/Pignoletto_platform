import traceback

from qgis.core import (QgsApplication,
                       QgsProcessingProvider,
                       QgsProcessingAlgorithm)

import os, importlib, glob

class AlgorithmProvider(QgsProcessingProvider):

    def __init__(self):
        super().__init__()

    def getAlgs(self):
        algs = []
        classes = []
        for file in glob.glob("/srv/processing/algorithms/*.py"):
            name = os.path.splitext(os.path.basename(file))[0]
            if name != "__init__" and name != "AlgorithmProvider":
                try:
                    spec = importlib.util.spec_from_file_location(name, "/srv/processing/algorithms/"+name+".py")
                    c = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(c)
                    miaclasse = getattr(c, name)
                    if issubclass(miaclasse, QgsProcessingAlgorithm):
                        classes.append(name)
                except Exception as e:
                    print("Error: ", e)
                    continue  

        for cl in classes:
            exec(f"from .{cl} import {cl};algs.append({cl}())")
        return algs

    def id(self):
        return 'pyqgiswps'

    def name(self):
        return "PyQgisWPS"

    def loadAlgorithms(self):
        self.algs = self.getAlgs()
        for a in self.algs:
            self.addAlgorithm(a)

