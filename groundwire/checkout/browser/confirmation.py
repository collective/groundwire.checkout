from Products.Five import BrowserView
from collective.beaker.interfaces import ISession
from getpaid.core.interfaces import IOrderManager
from zope.component import getUtility


class OrderConfirmationView(BrowserView):
    
    def __call__(self):
        session = ISession(self.request)
        order_id = session.get('groundwire.checkout.order_id', None)
        if order_id is not None:
            order_manager = getUtility(IOrderManager)
            order = order_manager.get(order_id)
            self.cart = order.shopping_cart
            if 'getpaid.processor.uid' in order.__annotations__:
                self.txn_id = order.__annotations__['getpaid.processor.uid']
            else:
                self.txn_id = None
                
            del session['groundwire.checkout.order_id']
            session.save()
        return self.index()
