from zope.component import adapter, getUtility, getAdapter
from zope.interface import implementer
from plone.app.layout.navigation.interfaces import INavigationRoot
from plone.registry.interfaces import IRegistry
from getpaid.core.interfaces import IPaymentProcessor
from getpaid.nullpayment.interfaces import INullPaymentOptions
from getpaid.authorizedotnet.interfaces import IAuthorizeNetOptions
from groundwire.checkout.settings import IGroundwireCheckoutSettings


@adapter(INavigationRoot)
@implementer(IPaymentProcessor)
def get_payment_processor(site):
    pp_name = getUtility(IRegistry).forInterface(IGroundwireCheckoutSettings, False).payment_processor
    return pp_name, getAdapter(site, IPaymentProcessor, name=pp_name)


@adapter(INavigationRoot)
@implementer(IAuthorizeNetOptions)
def get_authorizenet_settings(site):
    return getUtility(IRegistry).forInterface(IAuthorizeNetOptions)


@adapter(INavigationRoot)
@implementer(INullPaymentOptions)
def get_null_processor_settings(site):
    return getUtility(IRegistry).forInterface(INullPaymentOptions)
