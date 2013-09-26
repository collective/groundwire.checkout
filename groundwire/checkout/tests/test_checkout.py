import unittest2 as unittest
from plone.testing.z2 import Browser
from groundwire.checkout.testing import FUNCTIONAL_TESTING


CHARGED = False

from getpaid.core.item import PayableLineItem
class DummyLineItem(PayableLineItem):
    
    def after_charged(self):
        global CHARGED
        CHARGED = True


class TestGroundwireCheckout(unittest.TestCase):
    
    layer = FUNCTIONAL_TESTING
    
    def setUp(self):
        self.portal = self.layer['portal']

    def test_checkout(self):
        
        # Create a browser view to add our custom line item to the cart.
        # After payment is complete, the CHARGED global will be updated.
        from Products.Five import BrowserView
        from groundwire.checkout.utils import get_cart
        from groundwire.checkout.utils import redirect_to_checkout
        class PurchaseDummyView(BrowserView):
            __name__ = u'purchase'
            
            def __call__(self):
                item = DummyLineItem()
                item.item_id = 'item'
                item.name = 'My Item'
                item.cost = float(5)
                item.quantity = 1

                cart = get_cart()
                cart['item'] = item
                redirect_to_checkout()
        from zope.component import provideAdapter
        from zope.interface import Interface
        from zope.publisher.interfaces import IRequest
        provideAdapter(PurchaseDummyView, (Interface, IRequest), provides=Interface, name=u'purchase')
        
        # Hit the browser view to add an item to the cart
        browser = Browser(self.layer['app'])
        browser.handleErrors = False
        browser.open('http://nohost/plone/purchase')
        
        # Fill out the checkout form
        browser.getControl('Name', index=0).value = 'Harvey Frank'
        browser.getControl('Visa').selected = True
        browser.getControl('Credit Card Number').value = '4007000000027'
        browser.getControl(name='form.widgets.cc_expiration-year').value = '2020'
        browser.getControl('Security Code').value = '111'
        browser.getControl('Address 1').value = '1402 3rd Ave'
        browser.getControl('City', index=0).value = 'Seattle'
        browser.getControl('Postal Code').value = '98101'
        browser.handleErrors = False
        browser.getControl('Complete payment').click()

        # We should be on the confirmation page.
        self.assertEqual('http://nohost/plone/order-confirmation', browser.url)
        # Make sure everything was processed.
        self.assertTrue(CHARGED)
