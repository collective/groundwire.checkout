from cPickle import loads, dumps
from zExceptions import Redirect
from z3c.form import button, group, field, form
from collective.z3cform.datetimewidget import MonthYearFieldWidget
from zope.component import getUtility
from zope.site.hooks import getSite
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from getpaid.core import interfaces as gp_interfaces
from getpaid.core.interfaces import IOrderManager, IShoppingCartUtility
from getpaid.core.interfaces import IPaymentProcessor, workflow_states
from getpaid.core.order import Order
from zope.cachedescriptors.property import Lazy as lazy_property
from groundwire.checkout.schema import IGroundwireBillingAddress
from groundwire.checkout.schema import IGroundwireUserPaymentInformation
from groundwire.checkout.schema import ContactInfo, BillingAddressInfo, PaymentInfo
from groundwire.checkout.settings import is_ssl_enabled


class PaymentGroup(group.Group):
    label = u'Pay by credit card'
    fields = field.Fields(IGroundwireUserPaymentInformation).omit('bill_phone_number')
    fields['cc_expiration'].widgetFactory = MonthYearFieldWidget

    def getContent(self):
        return self.parentForm.getContent()

    def updateWidgets(self):
        super(PaymentGroup, self).updateWidgets()
        self.widgets['cc_cvc'].size = 3


class BillingAddressGroup(group.Group):
    label = u'Billing address'
    fields = field.Fields(IGroundwireBillingAddress).omit('bill_name', 'bill_organization')

    def getContent(self):
        return self.parentForm.getContent()

    def updateWidgets(self):
        super(BillingAddressGroup, self).updateWidgets()
        self.widgets['bill_postal_code'].size = 5


class PaymentForm(group.GroupForm, form.Form):
    label = u'Complete Payment'
    template = ViewPageTemplateFile('templates/checkout.pt')
    enable_form_tabbing = False
    ignoreContext = True

    @lazy_property
    def groups(self):
        # only show subforms if the cost is > 0
        if self.total_is_zero:
            return ()
        return PaymentGroup, BillingAddressGroup

    def __init__(self, context, request):
        if is_ssl_enabled() and not request.URL.startswith('https://'):
            raise Redirect(request.URL.replace('http://', 'https://'))

        super(PaymentForm, self).__init__(context, request)

    def update(self):
        super(PaymentForm, self).update()
        if self.total_is_zero:
            self.actions.values()[0].title = u'Finish'

    @lazy_property
    def buyer(self):
        membership = getToolByName(self.context, "portal_membership")
        if membership.isAnonymousUser():
            return None
        return membership.getAuthenticatedMember()

    @lazy_property
    def cart(self):
        cart = getUtility(IShoppingCartUtility).get(getSite())
        return cart

    @lazy_property
    def total_is_zero(self):
        return sum([item.cost for item in self.cart.values()]) <= 0

    @button.buttonAndHandler(u'Complete payment')
    def handleContinue(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        cart = self.cart
        if not len(cart):
            self.status = u"You have no items in your cart."
            return

        order = self.placeOrder(data, cart)
        if not order or order.finance_state != workflow_states.order.finance.CHARGED:
            self.status = u'Sorry, your credit card could not be processed.'
            return

        getUtility(IShoppingCartUtility).destroy(getSite())
        next_url = self.getNextUrl()
        self.request.response.redirect(next_url)

    def getNextUrl(self):
        portal_url = getToolByName(self.context, 'portal_url')()
        return portal_url + '/order-confirmation'

    def getContactInformation(self):
        contact = ContactInfo()
        contact.name = ''
        contact.email = ''
        contact.phone_number = ''
        return contact

    def getBuyerUsername(self):
        if self.buyer is not None:
            return self.buyer.getUserName()
        return ''

    def placeOrder(self, data, cart):
        # disable ZPublisher retries for this request
        self.request.retry_max_count = 0

        conn = self.context._p_jar
        order_manager = getUtility(IOrderManager)
        order = Order()
        conn.add(order)
        order.shopping_cart = loads(dumps(cart))
        # make sure the cart is not in session storage
        conn.add(order.shopping_cart)
        order.order_id = order_manager.newOrderId()

        order.contact_information = self.getContactInformation()
        conn.add(order.contact_information)
        order.billing_address = BillingAddressInfo(**data)
        conn.add(order.billing_address)
        order.user_id = self.getBuyerUsername()

        order.processor_id, processor = IPaymentProcessor(getSite())
        order.finance_workflow.fireTransition("create")
        order.bill_phone_number = ''

        if self.total_is_zero:
            order.user_payment_info_last4 = None
            order.name_on_card = None

            order_manager.store(order)
            order.finance_workflow.fireTransition("authorize")
            order.finance_workflow.fireTransition('charge-charging')
        else:
            order.user_payment_info_last4 = data['credit_card'][-4:]
            order.name_on_card = data['name_on_card']

            payment_info = PaymentInfo(**data)
            # XXX Should rewrite to do a single auth_capture if possible
            result = processor.authorize(order, payment_info)
            if result is gp_interfaces.keys.results_success:
                order_manager.store(order)
                order.finance_workflow.fireTransition("authorize")
            elif result is gp_interfaces.keys.results_async:
                # Asynchronous handling of authorization; we don't know status
                return order
            else:
                order.finance_workflow.fireTransition('reviewing-declined')
                return False

        return order
