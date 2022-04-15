import collections
import json
import os
from qgis.core import QgsMapLayer, QgsProject, QgsLayerTreeLayer, QgsLayerTreeGroup, QgsVectorLayer


class LizmapConfigError(Exception):
    pass


class LizmapConfig:

    # Static data
    
    mapQgisGeometryType = {
        0: 'point',
        1: 'line',
        2: 'polygon',
        3: 'unknown',
        4: 'none'
    }

    #lizmap_version = version()
    #target_lwc_version = format_version_integer('{}.0'.format(DEFAULT_LWC_VERSION.value))
    lizmap_version = "3.6.3"
    target_lwc_version = 30500

    metadata = {
        'qgis_desktop_version': {'default': 32204},
        'lizmap_plugin_version': {
            'wType': 'spinbox', 'type': 'integer', 'default': lizmap_version
        },
        'lizmap_web_client_target_version': {
            'wType': 'spinbox', 'type': 'integer', 'default': target_lwc_version
        },
        'project_valid': {'default': True}
    }

    globalOptionDefinitions = {
        'mapScales': {
            'wType': 'text', 'type': 'intlist', 'default': [1, 100, 1000, 10000, 25000, 50000, 100000, 250000, 500000, 1000000, 10000000]
        },
        'minScale': {
            'wType': 'text', 'type': 'integer', 'default': 1
        },
        'maxScale': {
            'wType': 'text', 'type': 'integer', 'default': 1000000000
        },
        'acl': {
            'wType': 'text', 'type': 'list', 'default': []
        },
        'initialExtent': {
            'wType': 'text', 'type': 'floatlist', 'default': []
        },
        'googleKey': {
            'wType': 'text', 'type': 'string', 'default': ''
        },
        'googleHybrid': {
            'wType': 'checkbox', 'type': 'boolean', 'default': False
        },
        'googleSatellite': {
            'wType': 'checkbox', 'type': 'boolean', 'default': False
        },
        'googleTerrain': {
            'wType': 'checkbox', 'type': 'boolean', 'default': False
        },
        'googleStreets': {
            'wType': 'checkbox', 'type': 'boolean', 'default': False
        },
        'osmMapnik': {
            'wType': 'checkbox', 'type': 'boolean', 'default': False
        },
        'osmStamenToner': {
            'wType': 'checkbox', 'type': 'boolean', 'default': False
        },
        'bingKey': {
            'wType': 'text', 'type': 'string', 'default': ''
        },
        'bingStreets': {
            'wType': 'checkbox', 'type': 'boolean', 'default': False
        },
        'bingSatellite': {
            'wType': 'checkbox', 'type': 'boolean', 'default': False
        },
        'bingHybrid': {
            'wType': 'checkbox', 'type': 'boolean', 'default': False
        },
        'ignKey': {
            'wType': 'text', 'type': 'string', 'default': ''
        },
        'ignStreets': {
            'wType': 'checkbox', 'type': 'boolean', 'default': False
        },
        'ignSatellite': {
            'wType': 'checkbox', 'type': 'boolean', 'default': False
        },
        'ignTerrain': {
            'wType': 'checkbox', 'type': 'boolean', 'default': False
        },
        'ignCadastral': {
            'wType': 'checkbox', 'type': 'boolean', 'default': False
        },

        'hideGroupCheckbox': {
            'wType': 'checkbox', 'type': 'boolean', 'default': False
        },
        'activateFirstMapTheme': {
            'wType': 'checkbox', 'type': 'boolean', 'default': False
        },
        'popupLocation': {
            'wType': 'list', 'type': 'string', 'default': 'dock', 'list': ['dock', 'minidock', 'map', 'bottomdock', 'right-dock']
        },
        'draw': {
            'wType': 'checkbox', 'type': 'boolean', 'default': False
        },
        'print': {
            'wType': 'checkbox', 'type': 'boolean', 'default': False
        },
        'measure': {
            'wType': 'checkbox', 'type': 'boolean', 'default': False
        },
        'externalSearch': {
            'wType': 'list', 'type': 'string', 'default': '', 'list': ['', 'nominatim', 'google', 'ban', 'ign']
        },
        'zoomHistory': {
            'wType': 'checkbox', 'type': 'boolean', 'default': False
        },
        'geolocation': {
            'wType': 'checkbox', 'type': 'boolean', 'default': False
        },
        'pointTolerance': {
            'wType': 'spinbox', 'type': 'integer', 'default': 25
        },
        'lineTolerance': {
            'wType': 'spinbox', 'type': 'integer', 'default': 10
        },
        'polygonTolerance': {
            'wType': 'spinbox', 'type': 'integer', 'default': 5
        },
        'hideHeader': {
            'wType': 'checkbox', 'type': 'boolean', 'default': False
        },
        'hideMenu': {
            'wType': 'checkbox', 'type': 'boolean', 'default': False
        },
        'hideLegend': {
            'wType': 'checkbox', 'type': 'boolean', 'default': False
        },
        'hideOverview': {
            'wType': 'checkbox', 'type': 'boolean', 'default': False
        },
        'hideNavbar': {
            'wType': 'checkbox', 'type': 'boolean', 'default': False
        },
        'hideProject': {
            'wType': 'checkbox', 'type': 'boolean', 'default': False
        },
        'tmTimeFrameSize': {
            'wType': 'spinbox', 'type': 'integer', 'default': 10
        },
        'tmTimeFrameType': {
            'wType': 'list', 'type': 'string', 'default': 'seconds',
            'list': ['seconds', 'minutes', 'hours', 'days', 'weeks', 'months', 'years']
        },
        'tmAnimationFrameLength': {
            'wType': 'spinbox', 'type': 'integer', 'default': 1000
        },
        'emptyBaselayer': {
            'wType': 'checkbox', 'type': 'boolean', 'default': False
        },
        'startupBaselayer': {
            'wType': 'list', 'type': 'string', 'default': '', 'list': ['']
        },
        'limitDataToBbox': {
            'wType': 'checkbox', 'type': 'boolean', 'default': False
        },
        'datavizLocation': {
            'wType': 'list', 'type': 'string', 'default': 'dock', 'list': ['dock', 'bottomdock', 'right-dock']
        },
        'datavizTemplate': {
            'wType': 'html', 'type': 'string', 'default': ''
        },
        'theme': {
            'wType': 'list', 'type': 'string', 'default': 'light', 'list': ['dark', 'light']
        },
        'atlasShowAtStartup': {
            'wType': 'checkbox', 'type': 'boolean', 'default': False
        },
        'atlasAutoPlay': {
            'wType': 'checkbox', 'type': 'boolean', 'default': False
        },
        'atlas': {
            'wType': 'dict', 'type': 'string', 'default': {'layers': []}
        },
        'locateByLayer': {
            'wType': 'checkbox', 'type': 'boolean', 'default': {}
        },
        'attributeLayers': {
            'wType': 'checkbox', 'type': 'boolean', 'default': {}
        },
        'tooltipLayers': {
            'wType': 'checkbox', 'type': 'boolean', 'default': {}
        },
        'editionLayers': {
            'wType': 'checkbox', 'type': 'boolean', 'default': {}
        },
        'loginFilteredLayers': {
            'wType': 'checkbox', 'type': 'boolean', 'default': {}
        },
        'timemanagerLayers': {
            'wType': 'checkbox', 'type': 'boolean', 'default': {}
        },
        'datavizLayers': {
            'wType': 'checkbox', 'type': 'boolean', 'default': {}
        },
        'filter_by_polygon': {
            'wType': 'checkbox', 'type': 'boolean', 'default': False
        },
        'formFilterLayers': {
            'wType': 'checkbox', 'type': 'boolean', 'default': {}
        },
        
    }

    layerOptionDefinitions = {
        'title': {
            'wType': 'text', 'type': 'string', 'default': '', 'isMetadata': True
        },
        'abstract': {
            'wType': 'textarea', 'type': 'string', 'default': '', 'isMetadata': True
        },
        'link': {
            'wType': 'text', 'type': 'string', 'default': '', 'isMetadata': False
        },
        'minScale': {
            'wType': 'text', 'type': 'integer', 'default': 1
        },
        'maxScale': {
            'wType': 'text', 'type': 'integer', 'default': 1000000000000
        },
        'toggled': {
            'wType': 'checkbox', 'type': 'boolean', 'default': "False"
        },
        'popup': {
            'wType': 'checkbox', 'type': 'boolean', 'default': "True", 'children': 'popupFrame'
        },
        'popupFrame': {
            'wType': 'frame', 'type': None, 'default': None, 'parent': 'popup'
        },
        'popupSource': {
            'wType': 'list', 'type': 'string', 'default': 'auto',
            'list': ["auto", "lizmap", "qgis", "form", ]
        },
        'popupTemplate': {
            'wType': 'text', 'type': 'string', 'default': ''
        },
        'popupMaxFeatures': {
            'wType': 'spinbox', 'type': 'integer', 'default': 10
        },
        'popupDisplayChildren': {
            'wType': 'checkbox', 'type': 'boolean', 'default': "False"
        },
        'noLegendImage': {
            'wType': 'checkbox', 'type': 'boolean', 'default': "False"
        },
        'groupAsLayer': {
            'wType': 'checkbox', 'type': 'boolean', 'default': "False"
        },
        'baseLayer': {
            'wType': 'checkbox', 'type': 'boolean', 'default': "False"
        },
        'displayInLegend': {
            'wType': 'checkbox', 'type': 'boolean', 'default': "True"
        },
        'group_visibility': {
            'wType': 'text', 'type': 'list', 'default': []
        },
        'singleTile': {
            'wType': 'checkbox', 'type': 'boolean', 'default': "True", 'children': 'cached', 'exclusive': "True"
        },
        'imageFormat': {
            'wType': 'list', 'type': 'string', 'default': 'image/png',
            'list': ["image/png", "image/png; mode=16bit", "image/png; mode=8bit", "image/jpeg"]
        },
        'cached': {
            'wType': 'checkbox', 'type': 'boolean', 'default': "False", 'children': 'serverFrame', 'parent': 'singleTile'
        },
        'serverFrame': {
            'wType': 'frame', 'type': None, 'default': None, 'parent': 'cached'
        },
        #'cacheExpiration': {
        #    'wType': 'spinbox', 'type': 'integer', 'default': 0
        #},
        #'metatileSize': {
        #    'wType': 'text', 'type': 'string', 'default': ''
        #},
        'clientCacheExpiration': {
            'wType': 'spinbox', 'type': 'integer', 'default': 300
        },
        #'externalWmsToggle': {
        #    'wType': 'checkbox', 'type': 'boolean', 'default': False
        #},
        #'sourceRepository': {
        #        'wType': 'text', 'type': 'string', 'default': '', '_api': False
        #},
        #'sourceProject': {
        #        'wType': 'text', 'type': 'string', 'default': '', '_api': False
        #}
    }

    groupOptionDefinitions = {
        'abstract': {
            'wType': 'textarea', 'type': 'string', 'default': '', 'isMetadata': True
        },
        'link': {
            'wType': 'text', 'type': 'string', 'default': '', 'isMetadata': False
        },
        'minScale': {
            'wType': 'text', 'type': 'integer', 'default': 1
        },
        'maxScale': {
            'wType': 'text', 'type': 'integer', 'default': 1000000000000
        },
        'toggled': {
            'wType': 'checkbox', 'type': 'boolean', 'default': "True"
        },
        'popup': {
            'wType': 'checkbox', 'type': 'boolean', 'default': "False", 'children': 'popupFrame'
        },
        'popupFrame': {
            'wType': 'frame', 'type': None, 'default': None, 'parent': 'popup'
        },
        'popupSource': {
            'wType': 'list', 'type': 'string', 'default': 'auto',
            'list': ["auto", "lizmap", "qgis", "form", ]
        },
        'popupTemplate': {
            'wType': 'text', 'type': 'string', 'default': ''
        },
        'popupMaxFeatures': {
            'wType': 'spinbox', 'type': 'integer', 'default': 10
        },
        'popupDisplayChildren': {
            'wType': 'checkbox', 'type': 'boolean', 'default': "False"
        },
        'noLegendImage': {
            'wType': 'checkbox', 'type': 'boolean', 'default': "False"
        },
        'groupAsLayer': {
            'wType': 'checkbox', 'type': 'boolean', 'default': "False"
        },
        'baseLayer': {
            'wType': 'checkbox', 'type': 'boolean', 'default': "False"
        },
        'displayInLegend': {
            'wType': 'checkbox', 'type': 'boolean', 'default': "True"
        },
        'group_visibility': {
            'wType': 'text', 'type': 'list', 'default': []
        },
        'singleTile': {
            'wType': 'checkbox', 'type': 'boolean', 'default': "True", 'children': 'cached', 'exclusive': "True"
        },
        'imageFormat': {
            'wType': 'list', 'type': 'string', 'default': 'image/png',
            'list': ["image/png", "image/png; mode=16bit", "image/png; mode=8bit", "image/jpeg"]
        },
        'cached': {
            'wType': 'checkbox', 'type': 'boolean', 'default': "False", 'children': 'serverFrame', 'parent': 'singleTile'
        },
        'serverFrame': {
            'wType': 'frame', 'type': None, 'default': None, 'parent': 'cached'
        },
        'clientCacheExpiration': {
            'wType': 'spinbox', 'type': 'integer', 'default': 300
        },
    }

    timemanagerOptionDefinitions = {
        'attributeResolution': {
            'wType': 'list', 'type': 'string', 'default': 'years',
            'list': ['seconds', 'minutes', 'hours', 'days', 'weeks', 'months', 'year']
        }
    }

    datavizOptionDefinitions = {
        'plotType': {
            'wType': 'list', 'type': 'string', 'default': 'scatter',
            'list': ['scatter', 'box', 'bar', 'histogram', 'pie', 'histogram2d', 'polar', 'sunburst']
        },
        'plotAggregation': {
            'wType': 'list', 'type': 'string', 'default': '',
            'list': ['', 'avg', 'sum', 'count', 'median', 'stddev', 'min', 'max', 'first', 'last']
        }
    }

    formFilterOptionDefinitions = {
        'type': {
            'wType': 'list', 'type': 'string', 'default': 'text',
            'list': ['text', 'uniquevalues', 'numeric', 'date']
        },
        'uniqueValuesFormat': {
            'wType': 'list', 'type': 'string', 'default': 'checkboxes',
            'list': ['checkboxes', 'select']
        }
    }

    def __init__(self, project, fix_json=False):
        """ Configuration setup

            :param fix_json: fix the json parsing,
                see https://github.com/3liz/lizmap-web-client/issues/925
        """
        if not isinstance(project, QgsProject):
            self.project = self._load_project(project)
        else:
            self.project = project

        self._WFSLayers = self.project.readListEntry('WFSLayers', '')[0]
        self._metadata = {}
        self._global_options = {}
        self._layer_options = {}
        self._tooltipLayers = {}
        self._formFilterLayers = {}
        self._attributeLayers = {}
        self._fix_json = fix_json


    @staticmethod
    def _load_project(path):
        """ Read a qgis project from path
        """
        if not os.path.exists(path):
            raise FileNotFoundError(path)
        project = QgsProject.instance()
        if not project.read(path):
            raise LizmapConfigError("Error reading qgis project")
        return project


    def get_layer_by_name(self, name):
        """ Return a unique layer by its name
        """
        matches = self.project.mapLayersByName(name)
        if len(matches) > 0:
            return matches[0]


    def get_group_by_name(self, name):
        """ Return a unique group by its name
        """
        root = self.project.layerTreeRoot()
        group = root.findGroup(name)
        if len(group) > 0:
            return group[0]


    def to_json(self, p_global_options=None, p_layer_options=None,
                sort_keys=False, indent=4, tooltip=False, formfilter=False,
                attributeTable=False, **kwargs):
        """ Returns the lizmap JSON configuration
        """
        # Set the options from the default only if overridden or not defined
        if p_global_options is not None or len(self._global_options) == 0:
            self.set_global_options(p_global_options)

        if p_layer_options is not None or len(self._layer_options) == 0:
            self.set_layer_options(p_layer_options)

        if tooltip:
            self.set_tooltips_layer()
        
        if formfilter:
            self.set_formfilter()

        if attributeTable:
            self.set_attributeTable()

        config = {
            'metadata': self._metadata,
            'options': self._global_options,
            'layers': self._layer_options,
            'tooltipLayers': self._tooltipLayers,
            'formFilterLayers': self._formFilterLayers,
            'attributeLayers': self._attributeLayers
        }

        if self._fix_json:
            # Fix https://github.com/3liz/lizmap-web-client/issues/925
            # copy config
            def map_dict(ob):
                if isinstance(ob, collections.Mapping):
                    return {k: map_dict(v) for k, v in ob.items()}
                elif isinstance(ob, bool):
                    return str(ob)
                else:
                    return ob

            config = map_dict(config)

        # Write json to the cfg file
        json_file_content = json.dumps(config, sort_keys=sort_keys, indent=indent, **kwargs)
        return json_file_content
    

    def set_tooltips_layer(self):
        self._tooltipLayers = {}

        vectorLayers = [(layer.id(), layer.name()) for layer in self.project.mapLayers().values() if isinstance(layer, QgsVectorLayer)]
        i = 0
        for id, name in vectorLayers:
            self._tooltipLayers[name] = {}  
            self._tooltipLayers[name]["layerId"] = id
            self._tooltipLayers[name]["fields"] = "id,value"
            self._tooltipLayers[name]["displayGeom"] = "True"
            self._tooltipLayers[name]["colorGeom"] = "#0000ff"
            self._tooltipLayers[name]["order"] = i
            i += 1
    

    def set_formfilter(self):
        self._formFilterLayers = {}

        vectorLayers = [(layer.id(), layer.name(), layer.providerType()) for layer in self.project.mapLayers().values() if isinstance(layer, QgsVectorLayer)]
        i = 0
        for id, name, provider in vectorLayers:
            self._formFilterLayers[i] = {}  
            self._formFilterLayers[i]["layerId"] = id
            self._formFilterLayers[i]["title"] = "Select a range of values for "+name+" layer"
            self._formFilterLayers[i]["type"] = "numeric"
            self._formFilterLayers[i]["field"] = "value"
            self._formFilterLayers[i]["order"] = i
            self._formFilterLayers[i]["provider"] = provider
            i += 1
    

    def set_attributeTable(self):
        self._attributeLayers = {}

        vectorLayers = [(layer.id(), layer.name()) for layer in self.project.mapLayers().values() if isinstance(layer, QgsVectorLayer)]
        i = 0
        for id, name in vectorLayers:
            self._attributeLayers[name] = {}  
            self._attributeLayers[name]["layerId"] = id
            self._attributeLayers[name]["primaryKey"] = "id"
            self._attributeLayers[name]["pivot"] = False
            self._attributeLayers[name]["hideAsChild"] = False
            self._attributeLayers[name]["hideLayer"] = False
            self._attributeLayers[name]["custom_config"] = False
            self._attributeLayers[name]["order"] = i
            i += 1


    def set_global_options(self, options):
        """ Set the global lizmap configuration options
        """
        # set defaults metadata
        self._metadata = {}
        self._metadata.update((k, v['default']) for k, v in self.metadata.items())

        # set defaults or Set custom options
        self._global_options = {}
        if options is not None:
            self._global_options.update((k, v) for k, v in options.items() if k in self.globalOptionDefinitions)
        else:
            self._global_options.update((k, v['default']) for k, v in self.globalOptionDefinitions.items() if v.get('_api', True))

        # projection
        # project projection
        project_crs = self.project.crs()
        self._global_options["projection"] = {"proj4": str(project_crs.toProj4()), "ref": str(project_crs.authid())}
        # wms extent
        project_wms_extent = self.project.readListEntry('WMSExtent', '')[0]
        if len(project_wms_extent) > 1:
            bbox = [project_wms_extent[0], project_wms_extent[1], project_wms_extent[2], project_wms_extent[3]]
        else:
            # init from a default position
            bbox = ["-3151562.0963662313", "1925755.0913321762", "7096917.541947947", "8926255.028888322"]
        self._global_options["bbox"] = bbox

        #if not self._global_options["initialExtent"]:
        self._global_options["initialExtent"] = list(map(float, bbox.copy()))


    def add_group(self, group, **options):
        """ Add a group to the configuration

            Pass options as keyword arguments
        """
        
        lo = {}
        lo["id"] = group.name()
        lo['name'] = group.name()
        lo['type'] = 'group'
        lo['title'] = group.name()

        lo.update((k, v['default']) for k, v in self.groupOptionDefinitions.items() if v.get('_api', True))

        # Override with passed options parameter
        if options:
            lo.update((k, v) for k, v in options if k in self.groupOptionDefinitions)

        # set config
        lid = str(group.name())
        self._layer_options[lid] = lo
        return lo


    def add_layer(self, layer, **options):
        """ Add a layer to the configuration

            Pass options as keyword arguments
        """
        lo = {}

        # The following should not be overridden
        lo['id'] = layer.id()
        lo['name'] = layer.name()
        lo['type'] = 'layer'

        geometry_type = -1
        if layer.type() == 0:  # if it is a vector layer
            geometry_type = self.mapQgisGeometryType[layer.geometryType()]
        if geometry_type != -1:
            lo["geometryType"] = geometry_type

        l_extent = layer.extent()
        lo["extent"] = [l_extent.xMinimum(),
                        l_extent.yMinimum(),
                        l_extent.xMaximum(),
                        l_extent.yMaximum()]

        lo['crs'] = layer.crs().authid()

        # lizmap default options for layer
        lo.update((k, v['default']) for k, v in self.layerOptionDefinitions.items() if v.get('_api', True))

        lo['title'] = layer.title() or layer.name()
        lo['abstract'] = layer.abstract()

        # styles
        if layer and hasattr(layer, 'styleManager'):
            ls = layer.styleManager().styles()
            if len(ls) > 1:
                lo['styles'] = ls

        # Override with passed p_layer_options parameter
        if len(options) > 0 and options:
            lo.update((k, v) for k, v in options.items() if k in self.layerOptionDefinitions)

        # Add metadata
        if layer.hasScaleBasedVisibility():
            if layer.maximumScale() < 0:
                lo['minScale'] = 0
            else:
                lo['minScale'] = layer.maximumScale()
            if layer.minimumScale() < 0:
                lo['maxScale'] = 0
            else:
                lo['maxScale'] = layer.minimumScale()

        # set config
        lid = str(layer.name())
        self._layer_options[lid] = lo
        return lo


    def set_layer_options(self, p_layer_options=None):
        """ Set the configuration options for the the project layers

            :param p_layer_options: dict of options for each layers
                    if p_layer options is None, add all layers otherwise add layer for
                    all layer names specified in p_layer_options
        """
        def get_group_layers(group):
            for child in group.children():
                if isinstance(child, QgsLayerTreeGroup):
                    self.add_group(child)
                    get_group_layers(child)
                elif isinstance(child, QgsLayerTreeLayer):
                    self.add_layer(child.layer())
    
        for layer in self.project.layerTreeRoot().children():
            if isinstance(layer, QgsLayerTreeLayer):
                self.add_layer(layer.layer())
            elif isinstance(layer, QgsLayerTreeGroup):
                self.add_group(layer)
                get_group_layers(layer)
        if p_layer_options:
            for lname, options in p_layer_options.items():
                if not self.get_layer_by_name(lname) is None:
                    layer = self.get_layer_by_name(lname)
                    self.add_layer(layer, **options)
                elif not self.get_group_by_name(lname) is None:
                    layer = self.get_group_by_name(lname)
                    self.add_group(layer, **options)

        return self._layer_options


    def hasWFSCapabilities(self, layer):
        """ Test if layer has WFS capabilities
        """
        return layer.id() in self._WFSLayers


    def set_title(self, title):
        """ Set WMS title
        """
        self.project.writeEntry("WMSServiceTitle", "/", title)


    def set_description(self, description):
        """ Set WMS description
        """
        self.project.writeEntry("WMSServiceDescription", "/", description)
        self.project.setDirty()


    def set_wmsextent(self, xmin, ymin, xmax, ymax):
        """ Set WMS extent
        """
        self.project.writeEntry("WMSExtent", "/", [str(xmin), str(ymin), str(xmax), str(ymax)])


    # noinspection PyPep8Naming
    def configure_server_options(self, WMSTitle=None, WMSDescription=None, WFSLayersPrecision=6, WMSExtent=None):
        """ Configure server options for layers in the qgis project

            The method will set WMS/WMS publication options for the layers in the project
        """
        if WMSTitle is not None:
            self.set_title(WMSTitle)
        if WMSDescription is not None:
            self.set_description(WMSDescription)
        if WMSExtent is not None:
            self.set_wmsextent(*WMSExtent)

        prj = self.project

        prj.writeEntry("WFSLayers", "/", [lid for lid, lyr in prj.mapLayers().items() if lyr.type() == QgsMapLayer.VectorLayer])
        for lid, lyr in prj.mapLayers().items():
            if lyr.type() == QgsMapLayer.VectorLayer:
                prj.writeEntry("WFSLayersPrecision", "/"+lid, WFSLayersPrecision)
        prj.writeEntry("WCSLayers", "/", [lid for lid, lyr in prj.mapLayers().items() if lyr.type() == QgsMapLayer.RasterLayer])
        prj.setDirty()

        # Update WFS layer list
        self._WFSLayers = prj.readListEntry('WFSLayers', '')[0]


    def from_template(self, template, context=None, **kwargs):
        """ Read a configuration from a jinja2 template
        """
        if not context:
            context = dict()
        # set context
        ctx = dict(context)
        layers = self.project.mapLayers().values()
        ctx['project'] = self.project
        ctx['layers'] = layers
        ctx['vectorlayers'] = [l for l in layers if l.type() == QgsMapLayer.VectorLayer]
        ctx['rasterlayers'] = [l for l in layers if l.type() == QgsMapLayer.RasterLayer]
        rendered = template.render(ctx)
        with open("/srv/projects/test_lizmap_api/api_output.json", "w") as fp:
            fp.write(rendered)
        options = json.loads(template.render(ctx))

        return self.to_json(options.get('options'), options.get('layers'), options.get('attributeLayers'), **kwargs)