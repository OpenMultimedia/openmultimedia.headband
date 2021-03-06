from zope.interface import implements
from zope.component import getUtility
from zope.component import getMultiAdapter
from zope.publisher.interfaces import IPublishTraverse
from zope.i18nmessageid import MessageFactory
from z3c.form import button
from z3c.form.interfaces import NOT_CHANGED

from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage

from plone.z3cform import layout
from plone.app.layout.viewlets.common import LogoViewlet as BaseLogoViewlet
from plone.registry.interfaces import IRegistry
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.cachepurging.interfaces import IPurger

from openmultimedia.headband.interfaces import ISettings
from zope.component.interfaces import ComponentLookupError


_ = MessageFactory('plone')


class HeadBandViewlet(BaseLogoViewlet):

    def update(self):
        super(HeadBandViewlet, self).update()
        registry = getUtility(IRegistry)
        setting = registry.forInterface(ISettings)
        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state')
        if setting.image:
            self.image_tag = '<img id="headband" src="%s%s" />' % \
                             (portal_state.portal_url(),
                             '/@@openmultimedia.headband/image')


class HeadBandImage(BrowserView):
    implements(IPublishTraverse)

    def __init__(self, context, request):
        """ Initialize context and request as view multiadaption parameters.

        Note that the BrowserView constructor does this for you.
        This step here is just to show how view receives its context and
        request parameter. You do not need to write __init__() for your
        views.
        """
        self.context = context
        self.request = request
        self.fieldname = None
        self.position = None
        self.subfieldname = None

    def publishTraverse(self, request, name):
        if self.fieldname is None:  # ../@@openmultimedia.headband/fieldname
            self.fieldname = name

        return self

    def __call__(self):
        registry = getUtility(IRegistry)
        setting = registry.forInterface(ISettings)
        self.request.RESPONSE.setHeader('Content-Type', 'image/jpeg')

        return getattr(setting, self.fieldname)


class SettingsEditForm(RegistryEditForm):
    """
    Define form logic
    """
    schema = ISettings
    label = u"Headband Settings"

    @button.buttonAndHandler(_(u"Save"), name='save')
    def handleSave(self, action):
        data, _errors = self.extractData()
        if not data['image']:
            data['image'] = NOT_CHANGED
        self.applyChanges(data)
        IStatusMessage(self.request).addStatusMessage(_(u"Changes saved."), "info")
        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state')
        try:
            purger = getUtility(IPurger)
            purger.purgeSync(portal_state.portal_url() + '/@@openmultimedia.headband/image')
        except ComponentLookupError:
            pass
        self.request.response.redirect("%s/%s" % (self.context.absolute_url(), self.control_panel_view))

    @button.buttonAndHandler(_(u"Cancel"), name='cancel')
    def handleCancel(self, action):
        IStatusMessage(self.request).addStatusMessage(_(u"Edit cancelled."), "info")
        self.request.response.redirect("%s/%s" % (self.context.absolute_url(), self.control_panel_view))


SettingsEditFormView = layout.wrap_form(SettingsEditForm, ControlPanelFormWrapper)
