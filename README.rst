Introduction
============

``groundwire.checkout`` provides an alternative frontend to the shopping cart
and order functionality of ``getpaid.core`` that can be used instead of
``Products.PloneGetPaid``.

In particular, this package replaces the following functionality of
Products.PloneGetPaid:

* It provides an IShoppingCartUtility to get or clear the shopping cart.
* It provides an IFormSchemas utility to look up the schemas and classes used
  to store address and payment information.
* It registers a persistent IOrderManager utility to store historic order info.
* It provides a checkout form to view the cart and place an order.
* It provides vocabularies of states and countries for use by the checkout form
  widgets.
* It provides an order confirmation view that is displayed after checkout.
* It provides settings in the configuration registry for choosing an active
  payment processor and forcing an HTTPS connection.

Noteworthy differences between this package and Products.PloneGetPaid are:

* groundwire.checkout does not provide a UI for adding items to the cart.
  This must be implemented by packages which extend groundwire.checkout.
* groundwire.checkout's payment form is implemented using z3c.form (making it
  easier to customize for people familiar with z3c.form), but does not support
  multiple wizard steps (so custom shipping and tax addons are not currently
  supported).
* groundwire.checkout uses Beaker for session storage instead of Zope sessions.
* groundwire.checkout provides a more useful order confirmation view following
  checkout, including a printable listing of the cart.
* groundwire.checkout does not currently provide a UI to browse order history.
  (Information about orders is still recorded in the database, though.)
* groundwire.checkout currently only supports the ``getpaid.authorizedotnet``
  payment processor.

Installation
============

1. Set up collective.beaker.

   groundwire.checkout uses Beaker for session storage for the user's cart.
   To use it, you must have configuration like the following in your buildout::

     [instance]
     zope-conf-additional =
         <product-config beaker>
             session.type            file
             session.data_dir        ${buildout:directory}/var/sessions/data
             session.lock_dir        ${buildout:directory}/var/sessions/lock
             session.key             beaker.session
             session.secret          secret
         </product-config>

   (Update ``secret`` to something, well, secret.)

2. Add ``groundwire.checkout`` to your buildout.

   You must add a custom find-link for hurry.workflow, because getpaid.core
   depends on a custom release that is not on PyPI. You must also pin versions
   of dependencies appropriately::
   
     [buildout]
     find-links =
         http://getpaid.googlecode.com/files/hurry.workflow-0.9.2-getpaid.zip
     versions = versions
     
     [versions]
     getpaid.authorizedotnet = 0.6.1
     getpaid.core = 0.9.2
     getpaid.nullpayment = 0.5.0
     hurry.workflow = 0.9.2-getpaid

   Then you can add ``groundwire.checkout`` as a dependency of your package in
   its setup.py::
     
     install_requires = [
          'groundwire.checkout',
          ]

   And load its ZCML in your package's configure.zcml::
   
     <include package="groundwire.checkout" />

   And activate its GenericSetup profile as a dependency in your product's
   metadata.xml::
   
     <?xml version="1.0"?>
     <metadata>
       <version>1</version>
       <dependencies>
         <dependency>profile-groundwire.checkout:default</dependency>
       </dependencies>
     </metadata>

3. Go to the configuration registry for your site and configure your payment
   processor settings appropriately.

Usage
=====

Basic checkout
--------------

Here's an example of adding an item to the cart, with a cost of $5.00, and
redirecting the user to the checkout form::

  from getpaid.core.item import PayableLineItem
  from groundwire.checkout.utils import get_cart
  from groundwire.checkout.utils import redirect_to_checkout
  
  item = PayableLineItem()
  item.item_id = 'item'
  item.name = 'My Item'
  item.cost = float(5)
  item.quantity = 1

  cart = get_cart()
  if 'item' in cart:
      del cart['item']
  cart['item'] = item
  redirect_to_checkout()


Performing an action after payment is complete
----------------------------------------------

To perform some action after a charge has been captured, use a custom
subclass of PayableLineItem and implement its ``after_charged`` method::

    from getpaid.core.item import PayableLineItem

    class MyLineItem(PayableLineItem):

        def after_charged(self):
            print 'charged!'


Setting up a donation form using pfg.donationform
-------------------------------------------------

``pfg.donationform`` can be used to set up a PloneFormGen-based donation form
that is compatible with groundwire.checkout (as well as Products.PloneGetPaid).

To add a donation form to a package that already has groundwire.checkout
installed:

1. Add ``pfg.donationform`` as a dependency of your package in setup.py::

     install_requires = [
          'pfg.donationform',
          ]

2. Depend on its ZCML from your package's configure.zcml::

     <include package="pfg.donationform" />

3. Activate its GenericSetup profile as a dependency in your package's
   metadata.xml::
   
     <?xml version="1.0"?>
     <metadata>
       <version>1</version>
       <dependencies>
         <dependency>profile-groundwire.checkout:default</dependency>
         <dependency>profile-pfg.donationform:default</dependency>
       </dependencies>
     </metadata>

4. Create a custom setuphandler for your package's GenericSetup profile which
   adds the form.  In setuphandlers.py::
   
     from pfg.donationform.utils import addDonationForm
   
     def import_various(context):
         if context.readDataFile('mypackage.txt') is None:
             return

         portal = context.getSite()
         
         if 'donate' not in portal:
             form = addDonationForm(portal,
                 title = u'Donate',
                 levels = "\n".join(['2500', '1000', '500', '250', '100', '50', '25']),
                 create_fields = True,
                 use_ssl = False,
                 )
             portal.portal_workflow.doActionFor(form, 'publish')
     
   (Adjust "mypackage.txt" to match your package's name, and make sure that file is
   present in your package's GenericSetup profile directory.)
   
   (You must enable SSL for a production deployment.)

   Also make sure you've registered the custom setup handler in your package's
   configure.zcml::
   
     <genericsetup:importStep
         name="mypackage_various"
         title="mypackage various"
         description="Various setup steps for mypackage"
         handler="mypackage.setuphandlers.import_various" />
     
   (Replace "mypackage" as appropriate.)
   
   Installing your package should now result in the creation of a functional
   donation form at /donate.

To be documented
----------------

* Customizing the templates
* Customizing the checkout form

  * Prepopulating fields
  * Customizing the contact info saved for the order
  * Adding a subform
  * Customizing the redirect URL

* Adding custom fields to a donation form
* Recording purchases to Salesforce using groundwire.sf_payment_recorder
* Test setup for products that use groundwire.checkout

