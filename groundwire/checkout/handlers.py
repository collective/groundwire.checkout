from zope.component import adapter
from zope.globalrequest import getRequest
from zope.site.hooks import getSite
from getpaid.core.interfaces import IOrder, workflow_states
from hurry.workflow.interfaces import IWorkflowTransitionEvent
from collective.beaker.interfaces import ISession


try:
    from pfg.donationform.interfaces import IDonationCart
except ImportError:
    IDonationCart = None


# Call each item's after_charged method after payment is captured.
@adapter(IOrder, IWorkflowTransitionEvent)
def dispatchPaymentEvents(order, event):
    if order.finance_state != event.destination:
        return
    if order.finance_state == workflow_states.order.finance.CHARGED:
        # Record order_id in session so it can be found
        # by the confirmation view
        request = getRequest()
        session = ISession(request)
        session['groundwire.checkout.order_id'] = order.order_id
        session.save()

        for item in order.shopping_cart.values():
            if hasattr(item, 'after_charged'):
                item.after_charged()

        # Make sure pfg.donationform uses our order confirmation view
        if IDonationCart and IDonationCart.providedBy(order.shopping_cart):
            if getattr(request, 'pfg.donationform_suppress_confirmation', False):
                return

            portal_url = getSite().absolute_url()
            getRequest().response.redirect(portal_url + '/order-confirmation')
