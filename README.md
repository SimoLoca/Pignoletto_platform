![Pignoletto](images/logo.jpg)
# Pignoletto Platform

This repository contains the source code of [**Pignoletto Platform**](inserire link).

Pignoletto platform is a system designed for the collection, the visualization the
management and the analysis (through manual inspection or automatic detection) of heterogeneous
and multisource data for soil characteristics estimation. The platform is designed in such a way that
it can easily handle proximity, airborne and spaceborne data and furnishes to the final user all the
tools and proper visualizations to perform precision agriculture.

The general architecture of the tool can be seen in the next figure.

![Architecture](images/architecture.png)

As seen, it provides 3 different interface to the system:
* **Platform**, which let users interact with a web map and visualize collected data.
* **Backend**, a Flask web-app that let user manage their data.
* **API**, which allows to insert acquisitions made by drones.

Next, we can see an example of what **Platform** could look like.

![platform](images/demo.png)


Here, instead is presented the interface of **Backend**.

![backend](images/Backend.png)

### Documentation
[**Wiki**](https://github.com/SimoLoca/Pignoletto_platform_Docker/wiki)

### License
Pignoletto Platform is released under the [MIT License](./LICENSE).

### Acknowledgments
Research developed in the context of the project PIGNOLETTO - Call HUB Ricerca e Innovazione CUP (Unique Project Code) n. E41B20000050007, co-funded by POR FESR 2014-2020 (Programma Operativo Regionale, Fondo Europeo di Sviluppo Regionale – Regional Operational Programme, European Regional Development Fund).

### Cite

```bibtex
@article{s23083788,
AUTHOR = {Piccoli, Flavio and Locatelli, Simone Giuseppe and Schettini, Raimondo and Napoletano, Paolo},
TITLE = {An Open-Source Platform for GIS Data Management and Analytics},
JOURNAL = {Sensors},
VOLUME = {23},
YEAR = {2023},
NUMBER = {8},
ARTICLE-NUMBER = {3788},
URL = {https://www.mdpi.com/1424-8220/23/8/3788},
ISSN = {1424-8220}
}
```
