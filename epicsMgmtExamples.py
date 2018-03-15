import epicsArchiver
import getpass

epicsMgmt = epicsArchiver.EpicsArchiverManagement (ipAddress = "10.0.6.57")

pvs = ["VAC:Canhao","VAC:Tripleto","VAC:Espectrometro","VAC:AEB09B","VAC:AEB10B","VAC:ADI11","VAC:AEB07B","VAC:AEB08B","VAC:AMV_09C","VAC:AEB05C","VAC:AEB06B","VAC:ACR05A","VAC:AEB04B","VAC:ACR05B","VAC:AWB07","VAC:AWB09","VAC:AMV_09C","VAC:SCR07","VAC:SKC12","VAC:XSI01","VAC:YSI03","VAC:SKC02A","VAC:SDI02","VAC:XSG02","VAC:XSG05","VAC:XSI06"]

pvs_dict_list = []

for pv in pvs:

    pvs_dict_list.append ({"name" : pv, "sampling_period" : epicsArchiver.EpicsArchiverManagement.DEFAULT_SAMPLING_PERIOD, \
                           "sampling_method" : epicsArchiver.EpicsArchiverManagement.DEFAULT_SAMPLING_METHOD, \
                           "sampling_policy" : epicsArchiver.EpicsArchiverManagement.DEFAULT_POLICY})

c = raw_input('Please enter an operation (R to remove, A to archive, D to fetch archived data or E exit): ')

if c == 'R' or c == 'A' :

    while epicsMgmt.authenticatedUser == None:

        print 'User authentication required'

        user = raw_input ('Username: ')
        passwd = getpass.getpass(prompt = 'Password: ')

        ans = epicsMgmt.login (user, passwd)

        if ans != epicsArchiver.EpicsArchiverManagement.SUCCESS:
            print 'User could not be authenticated or does not have enough rights to perform this operation'

    if c == 'A':
        epicsMgmt.archivePVs (pvs_dict_list)

    elif c == 'R':
        epicsMgmt.pausePVs (pvs_dict_list)
        epicsMgmt.deletePVs (pvs_dict_list)


