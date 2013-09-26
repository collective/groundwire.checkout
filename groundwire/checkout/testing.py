from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting
from collective.beaker.testing import BeakerConfigLayer
from groundwire.checkout import settings


class Layer(PloneSandboxLayer):
    
    defaultBases = (PLONE_FIXTURE,)
    
    def setUpZope(self, app, configurationContext):
        settings.TESTING = True
        BeakerConfigLayer.setUp()
        
        import groundwire.checkout
        self.loadZCML(package=groundwire.checkout)

    def setUpPloneSite(self, portal):
        self.applyProfile(portal, 'groundwire.checkout:default')
    
    def tearDownZope(self, app):
        settings.TESTING = False


FIXTURE = Layer()
INTEGRATION_TESTING = IntegrationTesting(bases=(FIXTURE,), name='groundwire.checkout:Integration')
FUNCTIONAL_TESTING = FunctionalTesting(bases=(FIXTURE,), name='groundwire.checkout:Functional')
