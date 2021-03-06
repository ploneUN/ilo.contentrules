from Acquisition import aq_inner
from OFS.SimpleItem import SimpleItem
from zope.component import adapts
from zope.component.interfaces import ComponentLookupError
from zope.interface import Interface, implements
from zope.formlib import form
from zope import schema

from plone.app.contentrules.browser.formhelper import AddForm, EditForm
from plone.contentrules.rule.interfaces import IRuleElementData, IExecutable

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.utils import safe_unicode

from logging import getLogger

logger = getLogger('ilo.contentrules.mailfromcreator')

class IMailFromCreator(Interface):
    subject = schema.TextLine(title=_(u"Subject"),
                              description=_(u"Subject of the message"),
                              required=True)

    recipients = schema.TextLine(title=_(u"Email recipients"),
                                description=_("The email where you want to \
send this message. To send it to different email addresses, just separate them\
 with ,"),
                                required=True)

    message = schema.Text(title=_(u"Message"),
                          description=_(u"Type in here the message that you \
want to mail. Some defined content can be replaced: ${title} will be replaced \
by the title of the item. ${url} will be replaced by the URL of the item."),
                          required=True)


class MailFromCreator(SimpleItem):
    """
    The implementation of the action defined before
    """
    implements(IMailFromCreator, IRuleElementData)

    subject = u''
    source = u''
    recipients = u''
    message = u''

    element = 'ilo.contentrules.mailfromcreator'

    @property
    def summary(self):
        return _(u"Email report to ${recipients} from object creator",
                 mapping=dict(recipients=self.recipients))

class MailFromCreatorExecutor(object):

    implements(IExecutable)
    adapts(Interface, IMailFromCreator, Interface)

    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event

    def __call__(self):
        recipients = [str(mail.strip()) for mail in \
                      self.element.recipients.split(',')]
        mailhost = getToolByName(aq_inner(self.context), "MailHost")
        if not mailhost:
            raise ComponentLookupError, 'You must have a Mailhost utility to \
execute this action'

        context = aq_inner(self.context)
        urltool = getToolByName(context, "portal_url")
        portal = urltool.getPortalObject()
        email_charset = portal.getProperty('email_charset')

        membertool = getToolByName(context, 'portal_membership')
        creator = self.event.object.Creator()
        memberobj = membertool.getMemberById(creator)

        if memberobj:
            email = memberobj.getProperty('email')
            fullname = memberobj.getProperty('fullname')
            source = '%s <%s>' % (fullname, email)
        else:
            logger.info('Unable to get member info for %s, sending as site from_address' % creator)
            from_address = portal.getProperty('email_from_address')
            if not from_address:
                raise ValueError, 'You must provide a source address for this \
action or enter an email in the portal properties'
            from_name = portal.getProperty('email_from_name')
            source = "%s <%s>" % (from_name, from_address)
        
        obj = self.event.object
        event_title = safe_unicode(obj.Title())
        event_url = obj.absolute_url()
        event_description = safe_unicode(obj.Description())
        message = self.element.message.replace("${url}", event_url)
        message = message.replace("${title}", event_title)
        message = message.replace("${description}", event_description)

        subject = self.element.subject.replace("${url}", event_url)
        subject = subject.replace("${title}", event_title)

        for email_recipient in recipients:
            mailhost.secureSend(message, email_recipient, source,
                                subject=subject, subtype='plain',
                                charset=email_charset, debug=False)
        return True


class MailAddForm(AddForm):
    """
    An add form for the mail action
    """
    form_fields = form.FormFields(IMailFromCreator)
    label = _(u"Add Mail From Creator Action")
    description = _(u"A mail action can mail different recipient")
    form_name = _(u"Configure element")

    def create(self, data):
        a = MailFromCreator()
        form.applyChanges(a, self.form_fields, data)
        return a

class MailEditForm(EditForm):
    """
    An edit form for the mail action
    """
    form_fields = form.FormFields(IMailFromCreator)
    label = _(u"Edit Mail From Creator Action Action")
    description = _(u"A mail action can mail different recipient.")
    form_name = _(u"Configure element")

