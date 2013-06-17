try:
    from zope.app.schema.vocabulary import IVocabularyFactorya
except ImportError:
    from zope.schema.interfaces import IVocabularyFactory
from zope.interface import implements
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

from Products.CMFCore.utils import getToolByName

from collective.portlet.rich import RichPortletMessageFactory as _

from plone.app.imaging.utils import getAllowedSizes

# Each vocabulary term should e understood like this:
# value | token (only used in the form) | title (unicode)
LINKS_CSS_STYLES = (
    (u"links_list", _(u"Links list")),
    (u"links_list_description", _(u"Links list with description")),
    (u"links_list_row", _(u"Links in a row")),
)
# this one might not be wanted since we already have - the footer feature
# #(u"links_read_more", 4, u"Read more links"),

class LinksCSSVocabulary(object):
    implements(IVocabularyFactory)

    def __call__(self, context):
        items = [SimpleTerm(value, value, title) for value, title in LINKS_CSS_STYLES]
        return SimpleVocabulary(items)

LinksCSSVocabulary = LinksCSSVocabulary()

class ImageScalesVocabulary(object):
    implements(IVocabularyFactory)

    def __call__(self, context):
        results = []
        sizes = getAllowedSizes()

        for (size, dimentions) in sizes.items():
            results.append(
                SimpleTerm(size, size)
            )

        return SimpleVocabulary(results)

ImageScalesVocabulary = ImageScalesVocabulary()
