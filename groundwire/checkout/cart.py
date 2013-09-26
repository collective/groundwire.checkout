from zope.interface import implements
from zope.globalrequest import getRequest
from getpaid.core.interfaces import IShoppingCartUtility
from getpaid.core.cart import ShoppingCart
from collective.beaker.interfaces import ISession


class ShoppingCartUtility(object):
    implements(IShoppingCartUtility)

    def get(self, portal, key=None):
        cart_id = 'groundwire.checkout.cart.%s' % '/'.join(portal.getPhysicalPath())
        session = ISession(getRequest())
        if cart_id not in session:
            session[cart_id] = ShoppingCart()
            session.save()
        return session[cart_id]

    def destroy(self, portal, key=None):
        cart_id = 'groundwire.checkout.cart.%s' % '/'.join(portal.getPhysicalPath())
        session = ISession(getRequest())
        if cart_id in session:
            del session[cart_id]
            session.save()
