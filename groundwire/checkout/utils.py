from zope.component import getUtility
from zope.site.hooks import getSite
from zope.globalrequest import getRequest
from collective.beaker.interfaces import ISession
from getpaid.core.interfaces import IShoppingCartUtility


def get_cart():
    return getUtility(IShoppingCartUtility).get(getSite())


def redirect_to_checkout():
    site = getSite()
    request = getRequest()
    session = ISession(request)
    session.save()
    request.response.redirect(site.absolute_url() + '/checkout')
