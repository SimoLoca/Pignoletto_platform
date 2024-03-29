from qgis.core import (QgsProcessingParameterVectorLayer,
                       QgsProcessingParameterVectorDestination,
                       QgsProcessingAlgorithm,
                       QgsVectorFileWriter)


class CopyLayer(QgsProcessingAlgorithm):

    INPUT  = 'INPUT'
    OUTPUT = 'OUTPUT'

    def __init__(self):
        super().__init__()

    def name(self):
        return 'copylayer'

    def displayName(self):
        return 'Copy Layer'

    def createInstance(self, config={}):
        """ Virtual override

            see https://qgis.org/api/classQgsProcessingAlgorithm.html
        """
        return self.__class__()

    def initAlgorithm( self, config=None ):
        """ Virtual override

           see https://qgis.org/api/classQgsProcessingAlgorithm.html
        """
        self.addParameter(QgsProcessingParameterVectorLayer(self.INPUT, 'Vector Layer'))
        self.addParameter(QgsProcessingParameterVectorDestination(self.OUTPUT, 'Output Layer'))

    def processAlgorithm(self, parameters, context, feedback):
        """ Virtual override

            see https://qgis.org/api/classQgsProcessingAlgorithm.html
        """
        layer   = self.parameterAsVectorLayer(parameters, self.INPUT, context)
        outfile = self.parameterAsOutputLayer(parameters, self.OUTPUT, context)

        # Save a copy of our layer
        err = QgsVectorFileWriter.writeAsVectorFormat(layer, outfile, "utf-8")

        if err[0] != QgsVectorFileWriter.NoError:
            feedback.reportError("Error writing vector layer %s: %s" % (outfile, err))

        return {self.OUTPUT: outfile }

