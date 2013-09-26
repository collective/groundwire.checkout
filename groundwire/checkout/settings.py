from Globals import DevelopmentMode
from zope.component import getUtility
from zope.interface import Interface
from zope import schema
from plone.registry.interfaces import IRegistry

TESTING = False


class IGroundwireCheckoutSettings(Interface):

    payment_processor = schema.Choice(
        title = u'Payment Processor',
        vocabulary = 'groundwire.checkout.PaymentMethods',
        default = u'Testing Processor',
        )

    force_ssl = schema.Bool(
        title = u'Force SSL?',
        description = u'When the Zope instance is not running in debug mode, '
                      u'the checkout form will redirect to an https:// URL.',
        default = True,
        )


def is_ssl_enabled():
    if TESTING or DevelopmentMode:
        return False
    return getUtility(IRegistry).forInterface(
                        IGroundwireCheckoutSettings, False).force_ssl
