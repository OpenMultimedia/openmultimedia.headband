Testing the viewlet
===================

Basic Setup
-----------

	>>> from plone.app.testing import SITE_OWNER_NAME, SITE_OWNER_PASSWORD
	>>> import transaction
	
	>>> portal = layer.get('app').plone
	>>> browser = z2.Browser(layer['app'])
	>>> import os
	>>> input_dir = os.path.join(test_home, 'input')
	>>> browser.open(portal.absolute_url() + '/login_form')
	>>> browser.getControl(name='__ac_name').value = SITE_OWNER_NAME
	>>> browser.getControl(name='__ac_password').value = SITE_OWNER_PASSWORD
	>>> browser.getControl(name='submit').click()

	>>> browser.open(portal.absolute_url())
	>>> 'id="portal-logo"' in browser.contents
	True

Still the original plone logo

	>>> '@@openmultimedia.headband/image' in browser.contents
	False

Replace logo

	>>> from zope.component import getUtility
	>>> from plone.registry.interfaces import IRegistry
	>>> from openmultimedia.headband.interfaces import ISettings
	>>> from openmultimedia.headband.testing import generate_jpeg

	>>> registry = getUtility(IRegistry)
	>>> settings = registry.forInterface(ISettings)
	>>> settings.image = generate_jpeg(200, 100)
	>>> transaction.commit()
	
Custom logo

	>>> browser.open(portal.absolute_url())
	>>> '@@openmultimedia.headband/image' in browser.contents
	True

	>>> browser.open(portal.absolute_url() + '/@@openmultimedia.headband/image')
	>>> browser.contents == settings.image
	True

	>>> browser.open(portal.absolute_url() + '/@@openmultimedia.headband/image1')
	Traceback (most recent call last):
	...
	HTTPError: HTTP Error 500: Internal Server Error
