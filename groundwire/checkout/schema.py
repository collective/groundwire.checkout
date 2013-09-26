from datetime import date
from zope import schema
from getpaid.core.interfaces import IBillingAddress, IShippingAddress, IUserPaymentInformation
from getpaid.core.interfaces import IUserContactInformation
from getpaid.core.options import PropertyBag, PersistentBag, FormSchemas
from getpaid.core.fields import CreditCardNumber


# Override to use our own country/state vocabs
class IGroundwireBillingAddress(IBillingAddress):
    bill_state = schema.Choice(
        title=u'State/Province',
        vocabulary='groundwire.checkout.States',
        )
    bill_postal_code = schema.TextLine(title = u'Zip/Postal Code', required=False)
    bill_country = schema.Choice(
        title=u'Country',
        vocabulary='groundwire.checkout.Countries',
        default=u'United States',
        )


class IGroundwireUserPaymentInformation(IUserPaymentInformation):
    name_on_card = schema.TextLine( title = u"Name",
                                description = u"Enter the full name, as it appears on the card. ")

    # DON'T STORE PERSISTENTLY
    credit_card_type = schema.Choice( title = u"Credit Card Type",
                                      source = "getpaid.core.accepted_credit_card_types",)

    credit_card = CreditCardNumber( title = u"Credit Card Number",
                                    description = u"Enter card number without spaces or hyphens.")

    cc_expiration = schema.Date( title = u"Credit Card Expiration Date", min=date(2011, 1, 1))

    cc_cvc = schema.TextLine(title = u"Security Code",
                             description = u"For American Express cards, this is the 4-digit code on the front of the card. "
                                           u"For all other cards, this is the 3-digit number on the back of the card.",
                             min_length = 3,
                             max_length = 4)


class ContactInfo(PersistentBag):
    pass
ContactInfo.initclass(IUserContactInformation)

class BillingAddressInfo(PersistentBag):
    pass
BillingAddressInfo.initclass(IBillingAddress)

class ShippingAddressInfo(PersistentBag):
    pass
ShippingAddressInfo.initclass(IShippingAddress)

class PaymentInfo(PropertyBag):
    def __init__(self, context=None, **kw):
        PropertyBag.__init__(self, **kw)
PaymentInfo = PaymentInfo.makeclass(IGroundwireUserPaymentInformation)


class GroundwireFormSchemas(FormSchemas):
    interfaces = {
        'billing_address': IGroundwireBillingAddress,
        'shipping_address': IShippingAddress,
        'contact_information': IUserContactInformation,
        'payment': IGroundwireUserPaymentInformation,
        }

    bags = {
        'billing_address': BillingAddressInfo,
        'shipping_address': ShippingAddressInfo,
        'contact_information': ContactInfo,
        'payment': PaymentInfo,
        }
