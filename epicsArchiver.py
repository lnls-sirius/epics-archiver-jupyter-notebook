import requests
import urllib3

class EpicsArchiverRetrieval:    

    def __init__ (self, ipAddress, port = 8080, isSelfSignedCertificate = True, isSSLSecure = True):

        self.ipAddress = ipAddress
        self.port = port
        self.isSelfSignedCertificate = isSelfSignedCertificate
        self.isSSLSecure = self.isSelfSignedCertificate or isSSLSecure

        if isSelfSignedCertificate:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def getRetrievalData (self) :

        protocol = "http://"

        if self.isSSLSecure:
            protocol = "https://"

        bpl = self.ipAddress

        if self.port != 8080 and self.port != 80:
            bpl = self.ipAddress + ":" + str (self.port)

        return protocol + bpl + "/retrieval/data"

    def retrieveData (self, start, end, pvs = []) :

        retrieval = self.getRetrievalData()

        ans = {}

        for pv in pvs:

            requestedPV = pv ["name"]

            if pv ["optimized"] :
                requestedPV = "optimized_" + str (pv ["bins"]) + "(" + pv ["name"] + ")"

            ans [pv ["name"]] = requests.get(retrieval + "/getData.json", \
                                    params = {"pv"   : requestedPV, \
                                              "from" : start.strftime("%Y-%m-%dT%H:%M:%S") + ".000Z", \
                                              "to"   : end.strftime ("%Y-%m-%dT%H:%M:%S") + ".000Z"}, \
                                    verify = not self.isSelfSignedCertificate ).json ()

        return ans

    def retrieveMetadata (self, pvs = []):

        retrieval = self.getRetrievalData()

        ans = {}

        for pv in pvs:

            ans [pv ["name"]] = requests.get(retrieval + "/getMetadata.json", \
                                    params = {"pv"   : requestedPV }, \
                                    verify = not self.isSelfSignedCertificate ).json ()

        return ans

class EpicsArchiverManagement:

    SUCCESS = 0
    LOGIN_FAILED = 1
    UNAUTHENTICATED_USER = 2

    DEFAULT_SAMPLING_PERIOD = 1.0
    DEFAULT_SAMPLING_METHOD = "MONITOR"
    DEFAULT_POLICY = "2HzPVs"

    def __init__ (self, ipAddress, port = 8080, requireUserAuthentication = True, isSelfSignedCertificate = True):

        self.ipAddress = ipAddress
        self.port = port
        self.requireUserAuthentication = requireUserAuthentication
        self.isSelfSignedCertificate = isSelfSignedCertificate
        self.authenticatedUser = None

        if requireUserAuthentication:
            self.session = requests.Session ()

        if isSelfSignedCertificate:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def getMgmtBpl (self) :

        bpl = self.ipAddress

        if self.port != 8080 and self.port != 80:
            bpl = self.ipAddress + ":" + str (self.port)

        return "https://" + bpl + "/mgmt/bpl"

    def login (self, user, passwd):

        if not self.requireUserAuthentication:
            return EpicsArchiverManagement.SUCCESS # We don't need to authenticate it

        mgmt = self.getMgmtBpl()

        self.session.post(mgmt + "/login", data = {"username" : user, "password" : passwd}, verify = not self.isSelfSignedCertificate)

        answer = self.session.get (mgmt + "/getLoginUsername",  verify = not self.isSelfSignedCertificate).json()

        if 'username' not in answer or answer['username'] != user:
            return EpicsArchiverManagement.LOGIN_FAILED

        self.authenticatedUser = user

        return EpicsArchiverManagement.SUCCESS

    def logout (self) :

        if not self.requireUserAuthentication:
            return EpicsArchiverManagement.SUCCESS  # We don't need to authenticate it

        mgmt = self.getMgmtBpl()

        self.session.post(mgmt + "/logout", verify = not self.isSelfSignedCertificate)

        self.authenticatedUser = None

    def archivePVs (self, pvs = []) :

        if self.requireUserAuthentication and self.authenticatedUser == None:
            return EpicsArchiverManagement.UNAUTHENTICATED_USER

        mgmt = self.getMgmtBpl()

        for pv in pvs:
            print "Attempting to archive PV = " + pv ["name"] + " : "
            print self.session.get(mgmt + "/archivePV", \
                                   params = {"pv" : pv ["name"], "samplingperiod" : pv ["sampling_period"], \
                                             "samplingmethod" : pv ["sampling_method"], \
                                             "policy" : pv ["sampling_policy"]}, \
                                   verify = not self.isSelfSignedCertificate).json()

    def deletePVs (self, pvs = []) :

        if self.requireUserAuthentication and self.authenticatedUser == None:
            return EpicsArchiverManagement.UNAUTHENTICATED_USER

        mgmt = self.getMgmtBpl()

        for pv in pvs:
            a = self.session.get(mgmt + "/deletePV", params = {"pv" : pv ["name"]}, verify = not self.isSelfSignedCertificate)
            print "PV " + pv ["name"] + " : status_code = " + str(a.status_code)

    def pausePVs (self, pvs = []) :

        if self.requireUserAuthentication and self.authenticatedUser == None:
            return EpicsArchiverManagement.UNAUTHENTICATED_USER

        mgmt = self.getMgmtBpl()

        for pv in pvs:

            a = self.session.get(mgmt + "/pauseArchivingPV", params = {"pv" : pv ["name"]}, verify = not self.isSelfSignedCertificate).json()

            if 'validation' in a:
                print "PV " + pv ["name"] + " : " + a['validation']
            elif 'engine_desc' in a:
                print "PV " + pv ["name"] + " : " + a['engine_desc']
