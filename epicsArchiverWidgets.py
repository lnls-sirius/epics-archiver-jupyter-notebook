# Widgets creation was moved to this module in order to let the notebook cleaner.
# Gustavo Ciotto Pinton

from ipywidgets import widgets

import epicsArchiver
import datetime
import matplotlib
import time
import numpy

UTC_OFFSET_TIMEDELTA = time.timezone // 3600
DELTA = (datetime.datetime (1970, 1, 1, 0, 0, 0) - datetime.datetime (1, 1, 1, 0, 0, 0)).total_seconds();

COLOR_STACK = [ (1.0, 0, 0, 1.0), (0, 1.0, 0, 1.0), (0, 0, 1.0, 1.0), (0, 0, 0, 1.0),(0.9, 0.75, 1.0, 1.0), (0.5, 0, 0, 1.0), (0.67, 0.43, 0.16, 1.0), (0.94, 0.196, 0.90, 1.0) ]

### Event handlers

def removePVHandler (b):
    PVWidgetList.remove(b.parent)
    appendPVVBox.children = PVWidgetList + [appendPVWidget]

def appendPVHandler (b):
    appendPVWidgets ()

def updateBinsText (event):
    event ["owner"].parent.children [2].disabled = not event ["owner"].parent.children [1].value
    
def appendPVWidgets (pv = ""):
    PVNameWidget = widgets.Text (description = "PV Name:", value = pv)

    PVBinsWidget = widgets.Checkbox(value = False, description = 'Optimized?')
    PVBinsIntWidget = widgets.IntText (value = "500", description = "# bins:", disabled = not PVBinsWidget.value)
    PVRemoveWidget = widgets.Button (description = "Remove")

    PVBinsWidget.observe (updateBinsText)
    PVRemoveWidget.on_click(removePVHandler) 

    newRow = widgets.HBox ([PVNameWidget, PVBinsWidget, PVBinsIntWidget, PVRemoveWidget])

    PVRemoveWidget.parent = newRow
    PVBinsWidget.parent = newRow

    PVWidgetList.append (newRow)

    appendPVVBox.children = PVWidgetList + [appendPVWidget]

# Encryption 
def update (sender):
    isSelfSignedWidget.value = isSSLWidget.value
    isSelfSignedWidget.disabled = not isSSLWidget.value

### Widgets initialization

# Host IP text widget
hostIPWidget = widgets.Text (value = "10.0.6.57:8080", description = "IP address:" )

# Encryption preferences widgets - SSL and self-signed certificate
isSSLWidget = widgets.Checkbox(value = True, description = 'Use HTTPS?')
isSSLWidget.observe (update)

isSelfSignedWidget = widgets.Checkbox(value = True, description = 'Self-signed SSL?', disabled = not isSSLWidget.value)

encryptionWidgets = widgets.HBox([isSSLWidget, isSelfSignedWidget])

# Datetime widgets
dateLayout = widgets.Layout(width='25%')

startDateWidget = widgets.DatePicker (description = 'Start: ', layout = dateLayout)
startHour = widgets.BoundedIntText (min = 0, max = 23, step = 1,description = 'Hour:', layout = dateLayout)
startMinute = widgets.BoundedIntText (min = 0, max = 59, step = 1, description = 'Minute:', layout = dateLayout)
startSecond = widgets.BoundedIntText(min = 0, max = 59, step = 1, description = 'Seconds:', layout = dateLayout)

endDateWidget = widgets.DatePicker(description = 'End: ', layout = dateLayout)
endHour = widgets.BoundedIntText(min = 0, max = 23, step = 1,description = 'Hour:', layout = dateLayout)
endMinute = widgets.BoundedIntText(min = 0, max = 59, step = 1, description = 'Minute:', layout = dateLayout)
endSecond = widgets.BoundedIntText(min = 0, max = 59, step = 1, description = 'Seconds:', layout = dateLayout)

dateTimeWidgets = widgets.VBox([widgets.HBox([startDateWidget, startHour, startMinute, startSecond]), \
                                widgets.HBox([endDateWidget, endHour, endMinute, endSecond])])

# Set default initialization values for the datetime widgets
now = datetime.datetime.now()

startDateWidget.value = now - datetime.timedelta (minutes = 10)
startHour.value = startDateWidget.value.hour
startMinute.value = startDateWidget.value.minute
startSecond.value = startDateWidget.value.second

endDateWidget.value = now
endHour.value = now.hour
endMinute.value = now.minute
endSecond.value = now.second

# PV field widgets
appendPVWidget = widgets.Button(description = 'Append')
appendPVWidget.on_click (appendPVHandler)

PVWidgetList = []

appendPVVBox = widgets.VBox ()
appendPVWidgets("Cont:LNLS191:NTP:Offset")
appendPVWidgets("CONT:EVK-M8F:NTP:Offset")
appendPVWidgets("LNLS:ANEL:corrente")
appendPVWidgets("PRO:MBTemp:Ch5")

### User helper functions

def drawAddressWidgets ():
    display (hostIPWidget)

def drawConnectionWidgets ():
    display (encryptionWidgets)

def drawDatetimeWidgets ():
    display (dateTimeWidgets)

def drawVariableWidgets ():
    display (appendPVVBox)

def drawPlot (variables = [], groups = []):

    if  variables == None or groups == None:
        return

    # A single variable has been passed as parameter
    if type (variables) == dict:
        variables = [variables]

    total = len (variables)

    for group in groups:
        total += len (group)

    # No PVs were passed
    if total == 0:
        return

    if len (variables) > 0:
        groups.append (variables)

    r = epicsArchiver.EpicsArchiverRetrieval (ipAddress = getIP (), port = getPort (), \
                                              isSSLSecure = isSSL (), \
                                              isSelfSignedCertificate = isSelfSignedCert ())

    fig, axes = matplotlib.pyplot.subplots(len (groups), sharex = True, figsize = (12,8))

    for g, group in enumerate (groups):

        answer = r.retrieveData (start = startTime (), end = endTime (), pvs = group)

        if len (groups) == 1:
            ax = axes
        else:
            ax = axes [g]

        init_ax = ax

        units = {}
        lines = []
        labels = []

        padding = 0

        for i, pv in enumerate(group):

            x_axis = []
            y_axis = []

            for sample in answer[pv ["name"]][0]["data"]:
                # https://matplotlib.org/devdocs/api/_as_gen/matplotlib.pyplot.plot_date.html
                # matplotlib.pyplot.plot_date(x, y)
                # x and/or y can be a sequence of dates represented as float days since 0001-01-01 UTC.
                x_axis.append((DELTA + sample["secs"] - UTC_OFFSET_TIMEDELTA * 3600 + sample["nanos"] * 1e-9) / (24.0 * 60.0 * 60.0 ))
                y_axis.append(sample["val"])

            if "EGU" in answer[pv ["name"]][0]["meta"].keys():
                unit = answer[pv ["name"]][0]["meta"]["EGU"]
            else:
                unit = pv ["name"]

            if unit in units.keys ():
                ax = units [unit]

            else :
                if i == 0:
                    units [unit] = ax
                else:
                    units [unit] = init_ax.twinx ()
                    ax = units [unit]
                    ax.spines['right'].set_position(('axes', 1 + padding))

                    padding += 0.125

                ax.set_ylabel (unit)

            lines += ax.plot_date (x_axis, y_axis, linestyle = "solid", drawstyle = "steps-post", marker = "", label = pv ["name"], color = COLOR_STACK [i])
            labels.append (pv ["name"])

        for i, ax in enumerate (units.values ()):

            ax.grid ()

            ax.set_yticks(numpy.linspace(ax.get_ybound()[0], ax.get_ybound()[1], 7))

            ax.xaxis_date ()
            ax.xaxis.set_major_locator(matplotlib.dates.MinuteLocator())
            ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%H:%M:%S"))

        ax.legend (lines, labels)

    matplotlib.pyplot.show (block = False)

def getIP ():
    return hostIPWidget.value.split (":") [0]

def getPort ():
    return int(hostIPWidget.value.split (":") [1])

def isSSL ():
    return isSSLWidget.value

def isSelfSignedCert ():
    return isSelfSignedWidget.value

def startTime ():
    start = startDateWidget.value
    return start.replace (hour = int(startHour.value + UTC_OFFSET_TIMEDELTA), minute = int(startMinute.value), second = int(startSecond.value))

def endTime ():
    end = endDateWidget.value
    return end.replace (hour = int(endHour.value + UTC_OFFSET_TIMEDELTA), minute = int(endMinute.value), second = int(endSecond.value))

def getVariables ():
    pvs = []

    for pvW in PVWidgetList:
        if pvW.children [0].value != "":
            pvs.append ({"name" : pvW.children [0].value, "optimized" : pvW.children [1].value, "bins" : pvW.children [2].value})

    return pvs

def getIthVariable (i = 0):

    if i < len (PVWidgetList) and PVWidgetList[i].children [0].value != "":
        return {"name" : PVWidgetList[i].children [0].value, "optimized" : PVWidgetList[i].children [1].value, "bins" : PVWidgetList[i].children [2].value}

    return None

def getRangeVariables (r = range (0,2)):

    pvs = []

    for i in r:
        pv = getIthVariable(i)
        if pv != None:
            pvs.append (pv)

    return pvs

