from Products.Five import BrowserView


class CartView(BrowserView):
    
    def format_price(self, price):
        if price < 0:
            return '-$%0.2f' % abs(price)
        else:
            return '$%0.2f' % price
