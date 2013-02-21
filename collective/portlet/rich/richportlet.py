import re

from plone.app.form.widgets.wysiwygwidget import WYSIWYGWidget
from plone.app.form.widgets.uberselectionwidget import UberSelectionWidget
from plone.app.portlets.portlets import base
from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.portlets.interfaces import IPortletDataProvider

from zope import schema
from zope.component import getUtility, getMultiAdapter
from zope.formlib import form
from zope.interface import implements

from Products.ATContentTypes.interface import IATImage
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
try:
    from Products.Five.formlib import formbase
except ImportError:
    from five.formlib import formbase

from collective.portlet.rich import RichPortletMessageFactory as _
from collective.formlib.link.field import Link
from collective.formlib.link.interfaces import ILink
try:
    from plone.namedfile.interfaces import IImageScaleTraversable
    provides = [IATImage.__identifier__, IImageScaleTraversable.__identifier__]
except ImportError:
    IImageScaleTraversable = None
    provides = IATImage.__identifier__


class IRichPortlet(IPortletDataProvider):
    """A portlet which renders predefined static HTML.

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    target_title_image = schema.Choice(
        title=_(u"Portlet title image"),
        description=_(u"Find the image"),
        required=False,
        source=SearchableTextSourceBinder({'object_provides' : provides}))
    
    scale = schema.TextLine(
        title=_(u"Image scale"),
        description=_(u"Scale of the selected image. "
                       "Make sure entered image scale exists."),
        required=False,
        default=u"mini")
    
    title = schema.TextLine(
        title=_(u"Portlet title"),
        description=_(u"Title of the rendered portlet"),
        required=True)

    title_more_url = schema.ASCIILine(
        title=_(u"Portlet title details link"),
        description=_(u"If given, the title "
                      "will link to this URL."),
        required=False)

    text = schema.Text(
        title=_(u"Text"),
        description=_(u"The portlet body text."),
        required=False)

    links = schema.List(
        title=_(u"Links"),
        description=_(u"Write links on the form \"<title>\":<path or uri>:\"<description\"."+
                      u"Title and description are both optional (but required for WCAG "+
                      u"accessibility compliance)."),
        required=False,
        value_type = Link(),
    )
    
    links_css = schema.Choice(
        title=_(u"Links styles"),
        description=_(u"Choose a css style for the links list."),
        required=True,
        vocabulary='collective.portlet.rich.vocabularies.LinksCSSVocabulary',
        )
    
    omit_border = schema.Bool(
        title=_(u"Omit portlet border"),
        description=_(u"Tick this box if you want to render the text above without the "
                      "standard header, border or footer."),
        required=True,
        default=False)
    
    footer = schema.TextLine(
        title=_(u"Portlet footer"),
        description=_(u"Text to be shown in the footer"),
        required=False)

    footer_more_url = schema.ASCIILine(
        title=_(u"Portlet footer details link"),
        description=_(u"If given, the footer will link to this URL."),
        required=False)

class Assignment(base.Assignment):
    """Portlet assignment.
    
    This is what is actually managed through the portlets UI and associated
    with columns.
    """
    
    implements(IRichPortlet)

    # backwards compatibility
    target_title_image = None
    title_more_url = None
    title = u"Rich portlet"
    scale = u"mini"
    
    def __init__(self, target_title_image=None, title=u"",
                 title_more_url='', text=u"", links = (),
                 links_css = 'links_list', omit_border=False,
                 footer=u"", footer_more_url='',
                 header=None, target_header_image=None, header_more_url=None,
                 scale=u"mini"):
        """Initialize all variables."""
        
        self.target_title_image = target_title_image
        self.title = title or Assignment.title
        self.title_more_url = title_more_url
        self.text = text
        self.links = links
        self.links_css = links_css
        self.omit_border = omit_border
        self.footer = footer
        self.footer_more_url = footer_more_url
        self.scale = scale

        # backwards compatibility
        if header is not None:
            self.title = header

        if target_header_image is not None:
            self.target_title_image = target_header_image

        if header_more_url is not None:
            self.title_more_url = header_more_url

class Renderer(base.Renderer):
    """Portlet renderer.
    
    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('richportlet.pt')
    
    # also taken from collection portlet 
    def __init__(self, *args):
        base.Renderer.__init__(self, *args)
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        self.portal_url = portal_state.portal_url()
        self.portal = portal_state.portal()        
        
    def css_class(self):
        """Generate a CSS class from the portlet title
        """
        title = self.data.title
        normalizer = getUtility(IIDNormalizer)
        return "portlet-richportlet-%s" % normalizer.normalize(title)
    
    def has_title_link(self):
        return bool(self.data.title_more_url)

    def has_text(self):
        """Is the text field really empty ? kupu do some times leave som
            markup behind the scene - so lets get the text 
           striped for markup and white spaces before and after the text
           this approach requires a regular expression. 
           
           TODO: clear out -- is this a sane approach ? is a reg expression expensive due to performance ?
        """
        text = self.data.text
        return text and len(re.sub('<(?!(?:a\s|/a|!))[^>]*>','',text).replace("\n", "").strip())
    
    def has_footer_link(self):
        return bool(self.data.footer_more_url)

    def has_footer(self):
        return bool(self.data.footer)

    def get_links(self):
        """Return a list of links as dictionaries."""

        # filter for backwards compatibility
        links = filter(ILink.providedBy, self.data.links)

        return [dict(
            title=link.title,
            description=link.description,
            url=link.absolute_url()) for link in links]

    def get_title_image_tag(self):
        """Generate image tag.
        
        Note: ``target_title_image`` uses the uberselection-widget
        and does not return an object (unlike Archetypes reference
        fields).
        """
        
        image_path = self.data.target_title_image
        
        
        # it feels insane that i need to do manual strippping of the first slash in this string.
        # I must be doing something wrong
        # please make this bit more sane
        
        if image_path is None or len(image_path)==0:
            return None
        # The portal root is never a image
        
        if image_path[0]=='/':
            image_path = image_path[1:]
        image = self.portal.restrictedTraverse(image_path, default=None)
        
        # we should also check that the returned object implements the interfaces for image
        # So that we don't accidentally return folders and stuff that will make things break
        scale = self.data.scale or u"mini"
        scale = scale.encode('ascii', 'replace')
        if IImageScaleTraversable and IImageScaleTraversable.providedBy(image):
            try:
                view = image.restrictedTraverse('@@images')
                view = view.__of__(image)
                return view.tag('image', scale=scale)
            except:
                return None
        elif IATImage.providedBy(image) and image.getImage() is not None:
            return image.tag(scale=scale)
        else:
            return None

class AddForm(base.AddForm):
    """Portlet add form.
    
    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IRichPortlet)
    form_fields['text'].custom_widget = WYSIWYGWidget
    form_fields['target_title_image'].custom_widget = UberSelectionWidget
    
    label = _(u"Add Rich Portlet")
    description = _(u"This portlet ...")

    def create(self, data):
        return Assignment(**data)

class EditForm(base.EditForm):
    """Portlet edit form.
    
    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IRichPortlet)
    form_fields['text'].custom_widget = WYSIWYGWidget
    form_fields['target_title_image'].custom_widget = UberSelectionWidget
    
    label = _(u"Edit Rich Portlet")
    description = _(u"This portlet ...")
    
