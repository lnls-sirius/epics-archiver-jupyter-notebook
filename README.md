# EPICS Archiver Retrieval Appliance Jupyter Notebook

A simple Jupyter notebook to fetch data from the archiver.

## Python modules

The `epicsArchiver.py` module provides two classes that can be used to pull data from the archiver. The first one, `EpicsArchiverRetrieval`, fetches data from the `retrieval` appliance, meanwhile the second one, `EpicsArchiverManagement`, can be used to add or remove variables.

Some remarkable methods belonging to the `EpicsArchiverRetrieval` class:

* `retrieveData(pvs = [])`: `pvs` is a list of dictionaries containing the keys `name`, `optimized` and `bins`. The latter one is optional and must be set only if `pvs[i]["optimized"]` is `True`. It returns another dict, in which the keys are the variable names and their values are the pulled data from the archiver.

Some remarkable methods belonging to the `EpicsArchiverManagement` class:

* If the archiver requires that the user must be authenticated, `login ()` must be executed before any other call of this class. `logout ()` invalidates the user session that is created after `login ()`.

* `pausePVs`, `archivePVs` and `pausePVs` control the set of archvied variables and their status. They all receive a PV list containing their names. Additionally, `archivePVs` requires information about the `samplingperiod`, `samplingmethod` and `sampling_policy` of each variable. They must be provided as dict values associated with the mentioned keys.

## Jupyter Notebook

An [interactive notebook](https://github.com/lnls-sirius/epics-archiver-jupyter-notebook/blob/master/epics-retrieval-notebook.ipynb) is also provided in this repo. It provides two different ways of plotting the pulled data: using one or multiple plots according to the number of groups passed as parameter. The function responsible for drawing the plots is `drawPlot`, defined in the `epicsArchiverWidgets` module. This module also provides helper functions to get the data from the UI components belonging to the notebook. The most important ones are `getVariables ()`, `getIthVariable ()` and `getRangeVariables ()` which translate the specified variable information into the format that `drawPlot ()` expects.
