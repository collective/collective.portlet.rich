from zope.component import getUtility, getMultiAdapter

from plone.portlets.interfaces import IPortletType
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletRenderer

from Products.CMFPlone.tests import dummy

from plone.app.portlets.storage import PortletAssignmentMapping

from collective.portlet.rich import richportlet
from collective.portlet.rich.tests import base

from collective.formlib.link.field import InternalLink, ExternalLink

class TestPortlet(base.TestCase):

    def afterSetUp(self):
        self.setRoles(('Manager',))

    def testPortletTypeRegistered(self):
        portlet = getUtility(IPortletType, name='collective.portlet.rich.RichPortlet')
        self.assertEquals(portlet.addview, 'collective.portlet.rich.RichPortlet')

    def testInterfaces(self):
        portlet = richportlet.Assignment(title=u"title", text="text")
        self.failUnless(IPortletAssignment.providedBy(portlet))
        self.failUnless(IPortletDataProvider.providedBy(portlet.data))

    def testInvokeAddview(self):
        portlet = getUtility(IPortletType, name='collective.portlet.rich.RichPortlet')
        mapping = self.portal.restrictedTraverse('++contextportlets++plone.leftcolumn')
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)
        
        #TODO: clean the dummy.Image() up
        data = {
            'target_title_image' : dummy.Image(), 
            'title' : u"test title", 
            'text' : u"test text", 
            'links' : [u'http://www.plone.org:Link title 1:Link description 1', u'http://www.python.org:Link title 2:Link description 2'],
        }
        addview.createAndAdd(data=data)
        
        self.assertEquals(len(mapping), 1)
        self.failUnless(isinstance(mapping.values()[0], richportlet.Assignment))

    def testInvokeEditView(self):
        mapping = PortletAssignmentMapping()
        request = self.folder.REQUEST

        mapping['foo'] = richportlet.Assignment(title=u"rich portlet title", text="rich portlet text")
        editview = getMultiAdapter((mapping['foo'], request), name='edit')
        self.failUnless(isinstance(editview, richportlet.EditForm))

    def testRenderer(self):
        context = self.folder
        request = self.folder.REQUEST
        view = self.folder.restrictedTraverse('@@plone')
        manager = getUtility(IPortletManager, name='plone.rightcolumn', context=self.portal)
        assignment = richportlet.Assignment(title=u"rich portlet title", text="rich portlet text")

        renderer = getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)
        self.failUnless(isinstance(renderer, richportlet.Renderer))

class TestRenderer(base.TestCase):
    
    def afterSetUp(self):
        self.setRoles(('Manager',))

    def renderer(self, context=None, request=None, view=None, manager=None, assignment=None):
        context = context or self.folder
        request = request or self.folder.REQUEST
        view = view or self.folder.restrictedTraverse('@@plone')
        manager = manager or getUtility(IPortletManager, name='plone.rightcolumn', context=self.portal)
        assignment = assignment or richportlet.Assignment(title=u"rich portlet title", text="rich portlet text")

        return getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)

    def test_render(self):
        r = self.renderer(context=self.portal, assignment=richportlet.Assignment(title=u"rich portlet title", text="<b>rich portlet text</b>"))
        r = r.__of__(self.folder)
        r.update()
        output = r.render()
        # print output
        self.failUnless('rich portlet title' in output)
        self.failUnless('<b>rich portlet text</b>' in output)
        
        
    def test_render_has_title_link(self):
        r = self.renderer(context=self.portal, assignment=richportlet.Assignment(title=u"rich portlet title", title_more_url="http://www.plone.org", text="<b>rich portlet text</b>"))
        r = r.__of__(self.folder)
        r.update()
        output = r.render()
        # print output
        self.failUnless('<a href="http://www.plone.org">rich portlet title</a>' in output)
        self.failUnless('<b>rich portlet text</b>' in output)
        
    def test_render_has_footer_link(self):
        r = self.renderer(context=self.portal, assignment=richportlet.Assignment(title=u"rich portlet title", text="<b>rich portlet text</b>", footer=u"rich portlet footer", footer_more_url="http://www.plone.org"))
        r = r.__of__(self.folder)
        r.update()
        output = r.render()
        # print output
        self.failUnless('rich portlet title' in output)
        self.failIf('<a href="http://www.plone.org">rich portlet title</a>' in output)
        self.failUnless('<b>rich portlet text</b>' in output)
        self.failUnless('<a href="http://www.plone.org">rich portlet footer</a>' in output)
    
    def test_render_get_title_image_tag(self):
        self.folder.invokeFactory('Image', id='image')
        target_title_image = '/Members/test_user_1_/image'
        r = self.renderer(context=self.portal, assignment=richportlet.Assignment(target_title_image=target_title_image, title=u"rich portlet title", text="<b>rich portlet text</b>",))
        r = r.__of__(self.folder)
        r.update()
        output = r.render()
        # print output
        image_tag = '<img src="http://nohost/plone/Members/test_user_1_/image/image_mini" alt="" title="" height="0" width="0" />'
        self.failUnless(image_tag in output)


    def test_render_list_links(self):
        links = (
            ExternalLink(u'http://www.plone.org', u'Link title 1', u'Link description 1'),
            ExternalLink(u'http://www.python.org', u'Link title 2', u'Link description 2'))

        r = self.renderer(context=self.portal, assignment=richportlet.Assignment(title=u"rich portlet title", text="<b>rich portlet text</b>", links = links,))
        r = r.__of__(self.folder)
        r.update()
        output = r.render()
        # print output
        self.failUnless('href="http://www.plone.org"' in output)
        self.failUnless('title="Link description 1">Link title 1' in output)

    def test_render_list_links_internal(self):
        links = (
            InternalLink(self.portal['front-page'].UID(),
                         u'Internal link title 1',
                         u'Internal link description 1'),
            InternalLink(self.portal['news'].UID(),
                         u'Internal link title 2',
                         u'Internal link description 2'))

        r = self.renderer(context=self.portal, assignment=richportlet.Assignment(title=u"rich portlet title", text="<b>rich portlet text</b>", links = links,))
        r = r.__of__(self.folder)
        r.update()
        output = r.render()
        # print output
        self.failUnless('href="http://nohost/plone/front-page' in output)
        self.failUnless('title="Internal link description 1">Internal link title 1' in output)

    def test_render_list_links_css_style(self):
        links = (
            ExternalLink(u'http://www.plone.org', u'Link title 1', u'Link description 1'),
            ExternalLink(u'http://www.python.org', u'Link title 2', u'Link description 2'))

        links_css = 'links_list_description'
        r = self.renderer(context=self.portal, assignment=richportlet.Assignment(title=u"rich portlet title", text="<b>rich portlet text</b>", links = links, links_css=links_css,))
        r = r.__of__(self.folder)
        r.update()
        output = r.render()
        # print output
        self.failUnless('href="http://www.plone.org"' in output)
        self.failUnless('title="Link description 1">Link title 1' in output)

    def test_render_has_text_only_html_tags(self):
        
        html_tags_no_text = "  \n\n         <p><br %><b></b></p>    \n  \n    <br />          "
        r = self.renderer(context=self.portal, assignment=richportlet.Assignment(title=u"rich portlet title", title_more_url="http://www.plone.org", text=html_tags_no_text))
        r = r.__of__(self.folder)
        r.update()
        output = r.render()
        # print output
        self.failIf(html_tags_no_text in output)


    def test_css_class(self):
        r = self.renderer(context=self.portal, 
                          assignment=richportlet.Assignment(title=u"Rich portlet title", text="<b>rich portlet text</b>"))
        self.assertEquals('portlet-richportlet-rich-portlet-title', r.css_class())
    
    def test_render_get_title_image_tag_scale(self):
        self.folder.invokeFactory('Image', id='image')
        target_title_image = '/Members/test_user_1_/image'
        r = self.renderer(context=self.portal, assignment=richportlet.Assignment(target_title_image=target_title_image, title=u"rich portlet title", text="<b>rich portlet text</b>", scale='thumb'))
        r = r.__of__(self.folder)
        r.update()
        output = r.render()
        # print output
        image_tag = '<img src="http://nohost/plone/Members/test_user_1_/image/image_thumb" alt="" title="" height="0" width="0" />'
        self.failUnless(image_tag in output)

        
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPortlet))
    suite.addTest(makeSuite(TestRenderer))
    return suite
