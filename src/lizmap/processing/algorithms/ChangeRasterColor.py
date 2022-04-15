from qgis.core import (QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterRasterDestination,
                       QgsProcessingAlgorithm,
                       QgsRasterFileWriter,
                       QgsRasterPipe,
                       QgsStyle,
                       QgsSingleBandPseudoColorRenderer,
                       QgsColorRampShader,
                       QgsProcessingParameterEnum,
                    )


class ChangeRasterColor(QgsProcessingAlgorithm):

    INPUT  = 'INPUT'
    OUTPUT = 'OUTPUT'
    COLORS = 'OPTIONS'

    color_names = ['Blues', 'BrBG', 'BuGn', 'BuPu', 'Cividis', 'GnBu', 'Greens', 'Greys', 'Inferno', 'Magma', 'Mako', 'OrRd',
                    'Oranges', 'PRGn', 'PiYG', 'Plasma', 'PuBu', 'PuBuGn', 'PuOr', 'PuRd', 'Purples', 'RdBu', 'RdGy', 'RdPu', 
                    'RdYlBu', 'RdYlGn', 'Reds', 'Rocket', 'Spectral', 'Turbo', 'Viridis', 'YlGn', 'YlGnBu', 'YlOrBr', 'YlOrRd']

    def __init__(self):
        super().__init__()


    def name(self):
        return 'Change Raster Color'


    def displayName(self):
        return 'Change Raster Color'

    
    def shortDescription(self):
        return 'Creates a copy of the selected layer with a different color map.'


    def createInstance(self, config={}):
        """ Virtual override

            see https://qgis.org/api/classQgsProcessingAlgorithm.html
        """
        return self.__class__()


    def initAlgorithm( self, config=None ):
        """ Virtual override

           see https://qgis.org/api/classQgsProcessingAlgorithm.html
        """
        self.addParameter(QgsProcessingParameterRasterLayer(self.INPUT, 'Raster Layer'))
        self.addParameter(QgsProcessingParameterEnum(
                            self.COLORS,
                            "Select color map",
                            options=self.color_names,
                            allowMultiple=False)
                        )
        self.addParameter(QgsProcessingParameterRasterDestination(self.OUTPUT, 'Output Layer'))


    def processAlgorithm(self, parameters, context, feedback):
        """ Virtual override

            see https://qgis.org/api/classQgsProcessingAlgorithm.html
        """
        layer = self.parameterAsRasterLayer(parameters, self.INPUT, context)
        color = self.parameterAsString(parameters, self.COLORS, context)
        outfile = self.parameterAsOutputLayer(parameters, self.OUTPUT, context)

        color_ramp = QgsStyle().defaultStyle().colorRamp(self.color_names[int(color)])

        renderer = QgsSingleBandPseudoColorRenderer(layer.dataProvider(), 1)
        renderer.createShader(color_ramp, colorRampType=QgsColorRampShader.Interpolated, 
            classificationMode=QgsColorRampShader.Quantile, classes=100)
        layer.setRenderer(renderer)

        layer.triggerRepaint()

        provider = layer.dataProvider()
        renderer = layer.renderer()

        pipe = QgsRasterPipe()
        pipe.set(provider.clone())        
        pipe.set(renderer.clone())

        # Save a copy of our layer
        file_writer = QgsRasterFileWriter(outfile)
        file_writer.writeRaster(pipe, provider.xSize(), provider.ySize(), provider.extent(), provider.crs())

        return {self.OUTPUT: outfile }