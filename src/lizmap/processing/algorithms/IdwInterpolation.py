import math
from collections import OrderedDict

from qgis.core import (QgsProcessing,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterDefinition,
                       QgsProcessingParameterRasterDestination,
                       QgsProcessingParameterString,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsRectangle,
                       QgsProcessingParameterField)
from qgis.analysis import (QgsInterpolator,
                           QgsIDWInterpolator,
                           QgsGridFileWriter)
from qgis.PyQt.QtCore import QCoreApplication

class ParameterPixelSize(QgsProcessingParameterNumber):

    def __init__(self, name='', description='', layersData=None, extent=None, minValue=None, default=None, optional=False):
        QgsProcessingParameterNumber.__init__(self, name, description, QgsProcessingParameterNumber.Double, default, optional, minValue)
        self.setMetadata({
            'widget_wrapper': 'srv.processing.algorithms.ui.InterpolationWidgets.PixelSizeWidgetWrapper'
        })

        self.layersData = layersData
        self.extent = extent
        self.layers = []

    def clone(self):
        copy = ParameterPixelSize(self.name(), self.description(), self.layersData, self.extent, self.minimum(), self.defaultValue(), self.flags() & QgsProcessingParameterDefinition.FlagOptional)
        return copy

class IdwInterpolation(QgsProcessingAlgorithm):
    INTERPOLATION_DATA = 'INTERPOLATION_DATA'
    INTERPOLATION_ATTRIBUTE = "INTERPOLATION_ATTRIBUTE"
    SOURCE_TYPE = 'SOURCE_TYPE'
    DISTANCE_COEFFICIENT = 'DISTANCE_COEFFICIENT'
    PIXEL_SIZE = 'PIXEL_SIZE'
    COLUMNS = 'COLUMNS'
    ROWS = 'ROWS'
    EXTENT = 'xMin,yMin,xMax,yMax'
    OUTPUT = 'OUTPUT'

    def tr(self, string, context=''):
        if context == '':
            context = self.__class__.__name__
        return QCoreApplication.translate(context, string)

    def __init__(self):
        super().__init__()

    def createInstance(self, config={}):
        return self.__class__()

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFeatureSource(self.INTERPOLATION_DATA,
                                                              'Input layer',
                                                              [QgsProcessing.SourceType.TypeVectorPoint]))
        field_param = QgsProcessingParameterField(self.INTERPOLATION_ATTRIBUTE,
                                                    'Interpolation attribute field',
                                                    None,
                                                    self.INTERPOLATION_DATA,
                                                    QgsProcessingParameterField.DataType.String,
                                                    optional=False
                                                    )
        field_param.setFlags(field_param.flags() | QgsProcessingParameterDefinition.Flag.FlagAdvanced)
        self.addParameter(field_param)     

        self.addParameter(QgsProcessingParameterString(self.EXTENT,
                                                       self.tr('Extent'),
                                                       defaultValue=self.EXTENT,
                                                       optional=True))                                  

        self.SOURCE_TYPES = OrderedDict([('Points', QgsInterpolator.SourceType.SourcePoints),
                                    ('Structure lines', QgsInterpolator.SourceType.SourceStructureLines),
                                    ('Break lines', QgsInterpolator.SourceType.SourceBreakLines)])
        keys = list(self.SOURCE_TYPES.keys())
        kernel_shape_param = QgsProcessingParameterEnum(self.SOURCE_TYPE,
                                                        'Source types',
                                                        keys,
                                                        allowMultiple=False,
                                                        defaultValue=0)
        kernel_shape_param.setFlags(kernel_shape_param.flags() | QgsProcessingParameterDefinition.Flag.FlagAdvanced)
        self.addParameter(kernel_shape_param)

        self.addParameter(QgsProcessingParameterNumber(self.DISTANCE_COEFFICIENT,
                                                       self.tr('Distance coefficient P'), 
                                                       type=QgsProcessingParameterNumber.Type.Double,
                                                       minValue=0.0, maxValue=99.99, defaultValue=2.0))

        pixel_size_param = ParameterPixelSize(self.PIXEL_SIZE,
                                              self.tr('Pixel size'),
                                              layersData=self.INTERPOLATION_DATA,
                                              extent=self.EXTENT,
                                              minValue=0.0,
                                              default=0.1)
        self.addParameter(pixel_size_param)

        cols_param = QgsProcessingParameterNumber(self.COLUMNS,
                                                  self.tr('Number of grid columns'),
                                                  optional=True,
                                                  minValue=0, maxValue=10000000)
        cols_param.setFlags(cols_param.flags() | QgsProcessingParameterDefinition.Flag.FlagAdvanced)
        self.addParameter(cols_param)

        rows_param = QgsProcessingParameterNumber(self.ROWS,
                                                  self.tr('Number of grid rows'),
                                                  optional=True,
                                                  minValue=0, maxValue=10000000)
        rows_param.setFlags(rows_param.flags() | QgsProcessingParameterDefinition.Flag.FlagAdvanced)
        self.addParameter(rows_param)

        self.addParameter(QgsProcessingParameterRasterDestination(self.OUTPUT,
                                                                  self.tr('Interpolated')))

    def name(self):
        return 'idwinterpolation'

    def displayName(self):
        return self.tr('IDW interpolation')

    def processAlgorithm(self, parameters, context, feedback):
        source = self.parameterAsSource(parameters, self.INTERPOLATION_DATA, context)
        if source is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INTERPOLATION_DATA))
        interpolation_attribute = self.parameterAsString(parameters, self.INTERPOLATION_ATTRIBUTE, context)
        source_type = self.parameterAsEnum(parameters, self.SOURCE_TYPE, context)
        coefficient = self.parameterAsDouble(parameters, self.DISTANCE_COEFFICIENT, context)
        pixel_size = self.parameterAsDouble(parameters, self.PIXEL_SIZE, context)
        output = self.parameterAsOutputLayer(parameters, self.OUTPUT, context)

        extent = self.parameterAsString(parameters, self.EXTENT, context)
        height, width = 0.0, 0.0
        if extent != self.EXTENT:
            exts = [float(x) for x in extent.split(',')]
            if len(exts) != 4: raise ValueError("Incorrect format!")
            rectangle = QgsRectangle(*exts) # 8.60,44.64,12,45.5
            height, width = rectangle.height(), rectangle.width()
        else:
            rectangle = source.sourceExtent()
            height, width = rectangle.height(), rectangle.width()

        columns = self.parameterAsInt(parameters, self.COLUMNS, context)
        rows = self.parameterAsInt(parameters, self.ROWS, context)
        if columns == 0:
            columns = max(math.ceil(height / pixel_size), 1)
        if rows == 0:
            rows = max(math.ceil(width / pixel_size), 1)

        layer_data = QgsInterpolator.LayerData()
        layer_data.source = source
        layer_data.sourceType = source_type
        layer_data.transformContext = context.transformContext()
        layer_data.interpolationAttribute = source.fields().lookupField(interpolation_attribute)
        #layer_data.valueSource = 0 # QgsInterpolator.ValueSource.ValueAttribute

        interpolator = QgsIDWInterpolator([layer_data])
        interpolator.setDistanceCoefficient(coefficient)
        writer = QgsGridFileWriter(interpolator,
                                   output,
                                   rectangle,
                                   columns,
                                   rows)
        writer.writeFile(feedback)
        return {self.OUTPUT: output}