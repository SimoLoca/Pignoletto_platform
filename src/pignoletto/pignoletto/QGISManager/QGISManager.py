# export PYTHONPATH=/usr/share/qgis/python
# export LD_LIBRARY_PATH=/usr/lib
# source venv/bin/activate export PYTHONPATH=/usr/share/qgis/python export LD_LIBRARY_PATH=/usr/lib

import sys, os, json, shutil
import qgis.core
from qgis.core import (
    QgsApplication, 
    QgsProject, 
    QgsRasterLayer, 
    QgsStyle, 
    QgsRasterBandStats, 
    QgsColorRampShader,
    QgsSingleBandPseudoColorRenderer,
    QgsVectorLayer,
    QgsDataSourceUri,
    QgsLayerTreeGroup,
    QgsLayerTreeLayer
    )
from .lizmap_API import LizmapConfig


class QGISManager:


    color_names = ('Blues', 'BrBG', 'BuGn', 'BuPu', 'Cividis', 'GnBu', 'Greens', 'Greys', 'Inferno', 'Magma', 'Mako', 'OrRd',
                    'Oranges', 'PRGn', 'PiYG', 'Plasma', 'PuBu', 'PuBuGn', 'PuOr', 'PuRd', 'Purples', 'RdBu', 'RdGy', 'RdPu', 
                    'RdYlBu', 'RdYlGn', 'Reds', 'Rocket', 'Spectral', 'Turbo', 'Viridis', 'YlGn', 'YlGnBu', 'YlOrBr', 'YlOrRd')


    def __init__(self, project_path):
        """ Reads the project path supplied and creates an instance of the project.

            Parameters
            ----------
            project_path: the path to the QGIS project
        """

        qgisPrefixPath = os.environ.get('QGIS_PREFIX_PATH','/usr/')
        os.environ['QGIS_PREFIX_PATH'] = qgisPrefixPath
        sys.path.append(os.path.join(qgisPrefixPath, "share/qgis/python/plugins/"))
        if os.environ.get('DISPLAY') is None:
            os.environ['QT_QPA_PLATFORM'] = 'offscreen'


        self.project_path = project_path    # maybe it's better os.path.abspath(project_path)
        # Create a reference to the QgsApplication
        # Setting the second argument to False disables the GUI
        self.qgis_app = QgsApplication([], False)
        self.qgis_app.setPrefixPath(qgisPrefixPath, True)
        self.qgis_app.initQgis()

        self.project = QgsProject.instance()
        self.project.setTitle("Pignoletto")
        self.WFS = False
        # if project exists, read it. Otherwise create empty one.
        if os.path.isfile(self.project_path):
            self.project.read(self.project_path)
        else:
            # Read from a base template and save in a new file
            base_path = os.path.join(os.path.join(os.getcwd(), "pignoletto/QGISManager"), "pignoletto.qgs")
            self.project.read(base_path)
            self.project.write(self.project_path)
        print("QGIS project instance created.")
    

    def add_Raster_layer(self, filename, num_classes=100, color="Viridis", group=None):
        """Adds a Raster layer to the QGIS instance and updates the QGIS project file.

        Parameters
        ----------
        filename: the path to tif file
        num_classes: the number of classes which will be use to quantize the tiff' values (default is 100)
        color: the name of the color ramp to apply (default is "Viridis")
        group: a group name (default is None), if specified insert the layer in the group
        """
        name = filename.split('/')[-1].split(".")[0]
        raster_layer = QgsRasterLayer(filename, name)

        if not self.project.mapLayersByName(raster_layer.name()):
            if not raster_layer.isValid():
                print("Error: Raster file isn't valid.")
            else:
                if group and not self.project.layerTreeRoot().findGroup(group):
                    print("Error: the specified group does not exist.")
                    return
                elif group and self.project.layerTreeRoot().findGroup(group):
                    g = self.project.layerTreeRoot().findGroup(group)
                    if raster_layer.name() in [child.name() for child in g.children()]:
                        print(f"Error: there is already a layer {raster_layer.name()} in group {group}.")
                        return
                    else:
                        self.project.layerTreeRoot().setItemVisibilityCheckedRecursive(False)
                        self.project.addMapLayer(raster_layer, False)
                        g.addLayer(raster_layer)
                else:
                    if raster_layer.name() in [child.name() for child in self.project.layerTreeRoot().children()]:
                        print("Error: The name of this layer is already used by another layer.")
                        return
                    else:
                        self.project.layerTreeRoot().setItemVisibilityCheckedRecursive(False)
                        self.project.addMapLayer(raster_layer)

                if color not in self.color_names:
                    color="Viridis"
                color_ramp = QgsStyle().defaultStyle().colorRamp(color)

                renderer = QgsSingleBandPseudoColorRenderer(raster_layer.dataProvider(), 1)
                renderer.createShader(color_ramp, colorRampType=QgsColorRampShader.Interpolated, 
                    classificationMode=QgsColorRampShader.Quantile, classes=num_classes)
                raster_layer.setRenderer(renderer)
        
                raster_layer.triggerRepaint()

                self.commit()
                print(f"Raster layer {name} added to the project.")
        else:
            print("Error: The name of this layer is already used by another layer.")


    def add_Vector_layer(self, filename, ref_sys=4326, group=None):
        """Adds a Vector layer to the QGIS instance and updates the QGIS project file.

        Parameters
        ----------
        filename: the path to vector file
        ref_sys: Coordinate Reference Systems' code (default is 4326)
        group: a group name (default is None), if specified insert the layer in the group
        """
        name = filename.split('/')[-1].split(".")[0]
        vector_layer = QgsVectorLayer(filename, name, "ogr")
        crs = vector_layer.crs()
        crs.createFromId(ref_sys)
        if not crs.isValid():
            print("Error: specified reference system isn't valid.")
            return
        vector_layer.setCrs(crs)
        if not self.project.mapLayersByName(vector_layer.name()):
            if not vector_layer.isValid():
                print("Error: Vector file isn't valid.")
            else:
                if group and not self.project.layerTreeRoot().findGroup(group):
                    print("Error: the specified group does not exist.")
                    return
                elif group and self.project.layerTreeRoot().findGroup(group):
                    g = self.project.layerTreeRoot().findGroup(group)
                    if vector_layer.name() in [child.name() for child in g.children()]:
                        print(f"Error: there is already a layer {vector_layer.name()} in group {group}.")
                        return
                    else:
                        self.project.layerTreeRoot().setItemVisibilityCheckedRecursive(False)
                        self.project.addMapLayer(vector_layer, False)
                        g.addLayer(vector_layer)
                else:
                    if vector_layer.name() in [child.name() for child in self.project.layerTreeRoot().children()]:
                        print("Error: The name of this layer is already used by another layer.")
                        return
                    else:
                        self.project.layerTreeRoot().setItemVisibilityCheckedRecursive(False)
                        self.project.addMapLayer(vector_layer)

                self.commit()
                print(f"Vector layer {name} added to the project.")
        else:
            print("Error: The name of this layer is already used by another layer.")


    def add_CSV_layer(self, filename, lat_key, lon_key, delimiter=',', variables=None, group=None):
        """Adds a Vector layer from a CSV file to the QGIS instance and updates the QGIS project file.

        Parameters
        ----------
        filename: the path to the CSV file
        lat_key: latitude key
        lon_key: longitude key
        delimiter: csv delimiter (default to ',')
        variables: a list containing all the necessary fields (default is None)
        group: a group name (default is None), if specified insert the layer in the group
        """
        layer_name = filename.split('/')[-1].split(".")[0]
        uri = f"file://{filename}?delimiter={delimiter}&xField={lon_key}&yField={lat_key}"
        # or
        # uri = "file:///some/path/file.csv?delimiter={}&crs=epsg:4723&wktField={}".format(";", "shape")
        vector_layer = QgsVectorLayer(uri, layer_name, "delimitedtext")
        vector_layer.setCrs(self.project.crs())

        if not self.project.mapLayersByName(vector_layer.name()):
            if not vector_layer.isValid():
                print("Error: csv file isn't valid.")
            else:
                if group and not self.project.layerTreeRoot().findGroup(group):
                    print("Error: the specified group does not exist.")
                    return
                elif group and self.project.layerTreeRoot().findGroup(group):
                    g = self.project.layerTreeRoot().findGroup(group)
                    if vector_layer.name() in [child.name() for child in g.children()]:
                        print(f"Error: there is already a layer {vector_layer.name()} in group {group}.")
                        return
                    else:
                        self.project.layerTreeRoot().setItemVisibilityCheckedRecursive(False)
                        self.project.addMapLayer(vector_layer, False)
                        g.addLayer(vector_layer)
                else:
                    if vector_layer.name() in [child.name() for child in self.project.layerTreeRoot().children()]:
                        print("Error: The name of this layer is already used by another layer.")
                        return
                    else:
                        self.project.layerTreeRoot().setItemVisibilityCheckedRecursive(False)
                        self.project.addMapLayer(vector_layer)

                self.commit()
                print(f"Vector layer {layer_name} added to the project.")
        else:
            print("Error: The name of this layer is already used by another layer.")


    def add_PostGIS_vector_layer(self, host_name, port, db_name, username, password, schema,
            table_name, geomColumn="coords", layer_name=None, pk=None, filter=None, group=None):
        """Adds a PostGIS vector layer to the QGIS instance and updates the QGIS project file.

        Parameters
        ----------
        host_name: the host name of the PostGre database
        port: the port where the db is exposed
        db_name: the name of the database
        username: the username
        password: password for the given username
        schema: the database schema
        table_name: the table name
        geomColumn: (default to 'coords') the geometry column type
        layer_name: (optional) the name of the layer
        pk: (optional) primary key field
        filter: (optional) a subset filter string to be applied to the source, and should take the form of a SQL “where” clause (e.g. “VALUE > 5”, “CAT IN (1,2,3)”)
        group: (optional) a group name, if specified insert the layer in the group
        """
        if layer_name is None:
            layer_name = table_name
        uri = QgsDataSourceUri()
        print(f"Connection to server {host_name}...")
        uri.setConnection(host_name, port, db_name, username, password)
        print("Connected!")
        uri.setDataSource(schema, table_name, geomColumn, filter, pk)
        print("Data retrieved!")
        layer = QgsVectorLayer(uri.uri(False), layer_name, "postgres")
        crs = layer.crs()
        if not crs.isValid():
            layer.setCrs(self.project.crs())
        if not self.project.mapLayersByName(layer.name()):
            if not layer.isValid():
                print("Error: PostGIS vector file isn't valid.")
            else:
                if group and not self.project.layerTreeRoot().findGroup(group):
                    print("Error: the specified group does not exist.")
                    return
                elif group and self.project.layerTreeRoot().findGroup(group):
                    g = self.project.layerTreeRoot().findGroup(group)
                    if layer.name() in [child.name() for child in g.children()]:
                        print(f"Error: there is already a layer {layer.name()} in group {group}.")
                        return
                    else:
                        self.project.layerTreeRoot().setItemVisibilityCheckedRecursive(False)
                        self.project.addMapLayer(layer, False)
                        g.addLayer(layer)
                else:
                    if layer.name() in [child.name() for child in self.project.layerTreeRoot().children()]:
                        print("Error: The name of this layer is already used by another layer.")
                        return
                    else:
                        self.project.layerTreeRoot().setItemVisibilityCheckedRecursive(False)
                        self.project.addMapLayer(layer)

                self.commit()
                print(f"Vector layer {layer_name} added to the project.")
        else:
            print("Error: The name of this layer is already used by another layer.")


    def add_PostGIS_raster_layer(self, host_name, port, db_name, username, password, schema,
                table_name, num_classes=100, color="Viridis",
                layer_name=None, pk=None, filter=None, group=None):
        """Adds a PostGIS raster layer to the QGIS instance and updates the QGIS project file.

        Parameters
        ----------
        host_name: the host name of the PostGre database
        port: the port where the db is exposed
        db_name: the name of the database
        username: the username
        password: password for the given username
        schema: the database schema
        table_name: the table name
        num_classes: the number of classes which will be use to quantize the tiff' values (default is 100)
        color: the name of the color ramp to apply (default is "Viridis")
        layer_name: (optional) the name of the layer
        pk: (optional) primary key field
        filter: (optional) a subset filter string to be applied to the source, and should take the form of a SQL “where” clause (e.g. “VALUE > 5”, “CAT IN (1,2,3)”)
        group: (optional) a group name, if specified insert the layer in the group
        """
        if layer_name is None:
            layer_name = table_name
        uri = QgsDataSourceUri()
        print(f"Connection to server {host_name}...")
        uri.setConnection(host_name, port, db_name, username, password)
        print("Connected!")
        uri.setDataSource(schema, table_name, "rast", filter, pk)
        print("Data retrieved!")
        
        layer = QgsRasterLayer(uri.uri(False), layer_name, "postgresraster")
        
        if not self.project.mapLayersByName(layer.name()):
            if not layer.isValid():
                print("Error: Raster file isn't valid.")
            else:
                if group and not self.project.layerTreeRoot().findGroup(group):
                    print("Error: the specified group does not exist.")
                    return
                elif group and self.project.layerTreeRoot().findGroup(group):
                    g = self.project.layerTreeRoot().findGroup(group)
                    if layer.name() in [child.name() for child in g.children()]:
                        print(f"Error: there is already a layer {layer.name()} in group {group}.")
                        return
                    else:
                        self.project.layerTreeRoot().setItemVisibilityCheckedRecursive(False)
                        self.project.addMapLayer(layer, False)
                        g.addLayer(layer)
                else:
                    if layer.name() in [child.name() for child in self.project.layerTreeRoot().children()]:
                        print("Error: The name of this layer is already used by another layer.")
                        return
                    else:
                        self.project.layerTreeRoot().setItemVisibilityCheckedRecursive(False)
                        self.project.addMapLayer(layer)

                if color not in self.color_names:
                    color="Viridis"
                color_ramp = QgsStyle().defaultStyle().colorRamp(color)
                renderer = QgsSingleBandPseudoColorRenderer(layer.dataProvider(), 1)
                renderer.createShader(color_ramp, colorRampType=QgsColorRampShader.Interpolated, 
                    classificationMode=QgsColorRampShader.Quantile, classes=num_classes)
                layer.setRenderer(renderer)
                layer.triggerRepaint()
                self.commit()
                print(f"Raster layer {layer_name} added to the project.")
        else:
            print("Error: The name of this layer is already used by another layer.")


    def move_layer_in_group(self, group_name, layer_name):
        """Move a layer in the specified existing group.

        Parameters
        ----------
        group_name: The name of the new group.
        layer_name: The layer to move.
        """
        if not self.project.mapLayersByName(layer_name):
            print(f"Error: layer {layer_name} not found.")
        else:
            if self.project.layerTreeRoot().findGroup(group_name):
                root = self.project.layerTreeRoot()
                parent = root.findGroup(group_name)
                layer = self.project.mapLayersByName(layer_name)[0]
                if layer.name() in [c.name() for c in parent.children()]:
                    print(f"There is already a layer {layer_name} in group {parent.name()}.")
                else:
                    thelayer = next((l for l in root.children() if l.name()==layer.name()), root.findLayer(layer.id()))
                    if thelayer is None:
                        print(f"Error: cannot find layer {layer.name()}")
                    else:
                        myClone = thelayer.clone()
                        parent.addChildNode(myClone)
                        parent = root if thelayer.parent() == None else thelayer.parent()
                        parent.removeChildNode(thelayer)
                        self.commit()
                        print(f"Layer {layer_name} inserted in group {group_name}.")
            else:
                print(f"Error: group {group_name} not found.")


    def create_group(self, group_name):
        """Creates a group.

        Parameters
        ----------
        group_name: The name of the new group.
        """
        if not self.project.layerTreeRoot().findGroup(group_name):
            self.project.layerTreeRoot().insertGroup(0, group_name)
            self.commit()
            print(f"Group {group_name} added.")
        else:
            print(f"Error: group {group_name} already exist.")


    def remove_group(self, group_name):
        """Remove the specified group if exists and all its content.

        Parameters
        ----------
        group_name: The name of the group.
        """
        if self.project.layerTreeRoot().findGroup(group_name):
            root = self.project.layerTreeRoot()
            group = root.findGroup(group_name)
            parent = root if group.parent() == None else group.parent()
            parent.removeChildNode(group)
            self.commit()
            print(f"Group {group_name} removed.")
        else:
            print(f"Error: group {group_name} does not exist.")


    def remove_empty_groups(self):
        """Remove all groups without layers.
        """
        self.project.layerTreeRoot().removeChildrenGroupWithoutLayers()
        self.commit()
        print("Removed all groups without layers.")


    def add_subgroup(self, parent_group, subgroup):
        """Create a group for the specified layers.

        Parameters
        ----------
        parent_group: The name of the parent group.
        subgroup: The name of the subgroup.
        """
        if self.project.layerTreeRoot().findGroup(subgroup):
            print(f"Error: group {subgroup} already exist.")
            return
        if self.project.layerTreeRoot().findGroup(parent_group):
            root = self.project.layerTreeRoot()
            parent = root.findGroup(parent_group)
            if parent.findGroup(subgroup):
                print(f"Error: subgroup {subgroup} is already in {parent_group}.")
            else:
                parent.addGroup(subgroup)
                self.commit()
                print(f"Subgroup {subgroup} added to parent group {parent_group}.")
        else:
            print(f"Error: Cannot find group {parent_group}.")


    def remove_layer(self, layer_name, group_name=None):
        """ Remove the specified layer if it exists.

            Parameters
            ----------
            layer_name: the name of the layer to be removed
            group_name: if specified, the remove the layer inside this group
        """
        if self.project.mapLayersByName(layer_name):
            layer = self.project.mapLayersByName(layer_name)[0]
            root = self.project.layerTreeRoot()
            if group_name is None:
                thelayer = next((l for l in root.children() if l.name()==layer.name()), None)
                root.removeChildNode(thelayer)
                self.commit()
                print(f"Layer {layer_name} removed.")
            else:
                if self.project.layerTreeRoot().findGroup(group_name):
                    group = root.findGroup(group_name)
                    if not layer.name() in [g.name() for g in group.children()]:
                        print(f"Error: there isn't a layer {layer_name} in group {group_name}.")
                    else:
                        thelayer = next((l for l in group.children() if l.name()==layer.name()), None)
                        group.removeChildNode(thelayer)
                        self.commit()
                        print(f"Layer {layer_name} in group {group_name} removed.")
                else:
                    print(f"Error: group {group_name} does not exist.")
        else:
            print("Error: The specified name doesn't belong to any layer.")


    def set_WFSCapabilities(self, published=True, precision=8, update=False, insert=False, delete=False):
        """Set the WFS Capabilities for the QGIS project in order to let the user use Lizmap tools (Edition, Tooltip, ...).
        """
        print("Setting WFS Capabilities...")
        vectorLayers = {layer.id(): layer.name() for layer in self.project.mapLayers().values() if isinstance(layer, QgsVectorLayer)}
        wfsLayersConfig = []
        for layer in self.project.mapLayers().values():
            if isinstance(layer, QgsVectorLayer):
                wfsLayersConfig.append({
                    "name": layer.name(),
                    "published": published,
                    "precision": precision,
                    "Update": update,
                    "Insert": insert,
                    "Delete": delete
                })
            
        if len(wfsLayersConfig) > 0 and wfsLayersConfig is not None:
            # To join by name as a key instead of identifier
            vectorLayersKeyValReversed = {v: k for k, v in vectorLayers.items()}
            # To set if published
            self.project.writeEntry( "WFSLayers" , "/", [vectorLayersKeyValReversed[l['name']] for l in wfsLayersConfig if l["published"]])
            # Set precision (need to loop as the xml tag is the layer identifier)
            [self.project.writeEntry("WFSLayersPrecision", "/" + vectorLayersKeyValReversed[l['name']], l["precision"]) for l in wfsLayersConfig]
            # Set Update
            self.project.writeEntry( "WFSTLayers" , "Update", [vectorLayersKeyValReversed[l['name']] for l in wfsLayersConfig if l["Update"]])
            # Set Insert
            self.project.writeEntry( "WFSTLayers" , "Insert", [vectorLayersKeyValReversed[l['name']] for l in wfsLayersConfig if l["Insert"]])
            # Set Delete
            self.project.writeEntry( "WFSTLayers" , "Delete", [vectorLayersKeyValReversed[l['name']] for l in wfsLayersConfig if l["Delete"]])
            print("WFS Capabilities set!")
            self.commit()
            self.WFS = True


    def create_Lizmap_configuration(self, tooltip=False, formfilter=False, attributeTable=False):
        """Creates the Lizmap configuration file.
        """

        layer = self.project.mapLayersByName("OSM_Standard")[0]
        self.project.layerTreeRoot().findLayer(layer.id()).setItemVisibilityChecked(True)
        self.commit()

        lv = LizmapConfig(self.project)
        if lv:
            my_global_options = {
                "mapScales": [1000,10000,25000,50000,100000,1000000,10000000,25000000,50000000],
                "minScale": 1000,
                "maxScale": 50000000,
                "popupLocation": "dock",
                "pointTolerance": 25,
                "lineTolerance": 10,
                "polygonTolerance": 5,
                "tmTimeFrameSize": 10,
                "tmTimeFrameType": "seconds",
                "tmAnimationFrameLength": 1000,
                "datavizLocation": "dock",
                "theme": "light"
            }

            osm_options = {
                "OSM_Standard": {"toggled": "True"}
            }

            _tooltip = True if tooltip and self.WFS else False
            _formfilter = True if formfilter and self.WFS else False
            _attributeTable = True if attributeTable and self.WFS else False

            json_content =  lv.to_json(
                p_global_options=my_global_options,
                p_layer_options=osm_options,
                tooltip=_tooltip,    # Set the Tooltip lizmap tool to each vector layer
                formfilter = _formfilter,    # Set the FormFilter lizmap tool to each vector layer
                attributeTable = _attributeTable    # Set the Attribute Table lizmap tool to each vector layer
            )

            if os.path.isfile(self.project_path + ".cfg"):
                json_content = json.loads(json_content)
                with open(self.project_path + ".cfg", mode='r+') as f:
                    jfile = json.load(f)
                    # update data
                    jfile["metadata"] = json_content["metadata"]
                    jfile["options"] = json_content["options"]
                    jfile["layers"] = json_content["layers"]
                    jfile["tooltipLayers"] = json_content["tooltipLayers"]
                    jfile["formFilterLayers"] = json_content["formFilterLayers"]
                    jfile["attributeLayers"] = json_content["attributeLayers"]
                    f.seek(0)
                    f.writelines(json.dumps(jfile, indent=4))
                    f.truncate()
            else:
                with open(self.project_path + ".cfg", 'x') as f:
                    f.writelines(json_content)
            
            shutil.copytree("./pignoletto/QGISManager/media", os.path.dirname(self.project_path)+'/media', dirs_exist_ok=True)


    def hide_project(self, flag:bool):
        """ Hide the project to all users if flag is True.

            Parameters
            ----------
            flag: if True hide the project, if False it makes it visible.
        """
        if type(flag) == bool:
            if os.path.isfile(self.project_path + ".cfg"):
                with open(self.project_path + ".cfg", mode='r+') as f:
                    jfile = json.load(f)
                    # update data
                    jfile["options"]["hideProject"] = flag
                    f.seek(0)
                    f.writelines(json.dumps(jfile, indent=4))
                    f.truncate()
                print(f"Project successfully {'hidden' if flag else 'visible'}")
            else:
                print("Error: lizmap configuration file not found.")
        else:
            print("Error: input parameter type isn't bool.")


    def restrict_layer_access(self, layer_name:str, groups:list):
        """ Restrict the access to the layer to specified groups of users.

            Parameters
            ----------
            layer_name : the name of the layer.
            groups: a list of str containing the groups of users.
        """
        if type(groups) == list and type(layer_name) == str:
            if all([type(g) == str for g in groups]) and layer_name and len(set(groups)) == len(groups):
                if os.path.isfile(self.project_path + ".cfg"):
                    with open(self.project_path + ".cfg", mode='r+') as f:
                        jfile = json.load(f)
                        # update data
                        if layer_name in jfile["layers"]:
                            jfile["layers"][layer_name]["group_visibility"] = groups
                            f.seek(0)
                            f.writelines(json.dumps(jfile, indent=4))
                            f.truncate()
                            print(f"Layer {layer_name} restricted to groups: {groups}")
                        else:
                            print("Error: specified layer not found.")
                else:
                    print("Error: lizmap configuration file not found.")
            else:
                print("Error: not all inserted groups are in a correct format.")
        else:
            print("Error: input parameters type not valid.")

    
    def restrict_proj_access(self, groups:list):
        """ Restrict the access to the project to specified groups of users.

            Parameters
            ----------
            groups: a list of str containing the groups of users.
        """
        if type(groups) == list:
            if all([type(g) == str for g in groups]) and len(set(groups)) == len(groups):
                if os.path.isfile(self.project_path + ".cfg"):
                    with open(self.project_path + ".cfg", mode='r+') as f:
                        jfile = json.load(f)
                        # update data
                        jfile["options"]["acl"] = groups
                        f.seek(0)
                        f.writelines(json.dumps(jfile, indent=4))
                        f.truncate()
                    print(f"Project restricted to groups: {groups}")
                else:
                    print("Error: lizmap configuration file not found.")
            else:
                print("Error: not all inserted groups are in a correct format.")
        else:
            print("Error: input parameter type isn't a list.")


    def get_all_layers_groups(self):
        """Get all the layers and groups in the project.

        Returns
        ----------
        dict: A dictionary of all layers and groups loaded
        """
        def get_group_layers(group):
            for child in group.children():
                if isinstance(child, QgsLayerTreeGroup):
                    res["group"].append(child.name())
                    get_group_layers(child)
                elif isinstance(child, QgsLayerTreeLayer):
                    res["layer"].append(child.name())
        
        res = {
            "group": [],
            "layer": []
        }
        for layer in self.project.layerTreeRoot().children():
                if isinstance(layer, QgsLayerTreeLayer):
                    res["layer"].append(layer.name())
                elif isinstance(layer, QgsLayerTreeGroup):
                    res["group"].append(layer.name())
                    get_group_layers(layer)

        return res


    def get_colors():
        """Get all the color for a color ramp.

        Returns
        ----------
        List: A list of strings containing all possible color names
        """
        return QgsStyle().defaultStyle().colorRampNames()


    def get_MinMax(self, raster_layer):
        """Get the min and max values in a raster layer.

        Parameters
        ----------
        raster_layer: the QgsRasterLayer object

        Returns
        ----------
        tuple: The min and max values

        """
        provider = raster_layer.dataProvider()
        extent = raster_layer.extent()
        stats = provider.bandStatistics(1, QgsRasterBandStats.All, extent, 0)
        return (stats.minimumValue, stats.maximumValue)


    def commit(self):
        self.project.write()
        print("Project commited.")


    def shutDown(self):
        """Remove the provider and layer registries from memory.
        """
        self.qgis_app.exit()
        del self.qgis_app
        del self.project
