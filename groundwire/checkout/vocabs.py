from operator import attrgetter
import pycountry
from getpaid.core.interfaces import IPaymentProcessor
from zope.component import getAdapters
from zope.component.interfaces import ComponentLookupError
from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.site.hooks import getSite


def PaymentMethods(context):
    adapters = getAdapters([getSite()], IPaymentProcessor)
    try:
        payment_names = [unicode(n) for n, a in adapters if n]
    except ComponentLookupError:
        payment_names = [u'Testing Processor', ]
    payment_names = set(payment_names)
    return SimpleVocabulary.fromValues(payment_names)


class CountryVocabulary(object):
    """ Vocab for selecting a country from the pycountry ISO-3166 database.
    """
    implements(IVocabularyFactory)

    def __call__(self, context):
        # Make sure US and Canada sort at the top
        terms = [
            SimpleTerm(u'United States', title=u'United States', token='US'),
            SimpleTerm(u'Canada', title=u'Canada', token='CA'),
            ]
        for country in pycountry.countries:
            if country.alpha2 in ('US', 'CA'):
                continue
            uname = unicode(country.name)
            terms.append(SimpleTerm(uname, title=uname, token=country.alpha2))
        return SimpleVocabulary(terms)


class StateVocabulary(object):
    """ Vocab for selecting a state."""
    implements(IVocabularyFactory)

    def __call__(self, context):
        terms = [SimpleTerm('', title=u'-- None/International --', token='n/a')]
        us_states = sorted(pycountry.subdivisions.get(country_code='US'), key=attrgetter('name'))
        ca_states = sorted(pycountry.subdivisions.get(country_code='CA'), key=attrgetter('name'))
        states = us_states + ca_states
        for state in states:
            code = state.code[3:]
            terms.append(SimpleTerm(code, title=state.name, token=code))
        return SimpleVocabulary(terms)
