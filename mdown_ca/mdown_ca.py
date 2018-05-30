import logging
import misaka
import textwrap

from xblock.core import XBlock
from xblock.fields import Scope, String, List
from xblock.fragment import Fragment
from xblockutils.resources import ResourceLoader
from xblockutils.studio_editable import StudioEditableXBlockMixin

log = logging.getLogger(__name__)
loader = ResourceLoader(__name__)


class MarkdownCAXBlock(StudioEditableXBlockMixin, XBlock):
    """
    Displays markdown content as HTML

    """
    display_name = String(
        help="This name appears in the horizontal navigation at the top of the page.",
        default="Markdown CA",
        scope=Scope.settings)
    filename = String(
        help="Relative path to a markdown file uploaded to the static store.  For example, \"markdown_file.md\".",
        default="",
        scope=Scope.content)
    content = String(
        help="Markdown content to display for this module.",
        default=u"",
        multiline_editor=True,
        scope=Scope.content)
    extras = List(
        help="Misaka module extras to turn on for the instance.",
        list_style="set",
        list_values_provider=lambda _: [
            # Taken from http://misaka.61924.nl/#extensions
            {"display_name": "Tables", "value": "tables"},
            {"display_name": "Fenced Code Blocks", "value": "fenced-code"},
            {"display_name": "Footnotes", "value": "footnotes"},
            {"display_name": "Autolinks", "value": "autolink"},
            {"display_name": "Strikethrough", "value": "strikethrough"},
            {"display_name": "Underline", "value": "underline"},
            {"display_name": "Highlight", "value": "highlight"},
            {"display_name": "Quotes", "value": "quote"},
            {"display_name": "Superscript", "value": "superscript"},
            {"display_name": "Math", "value": "math"},
            {"display_name": "No Intra Emphasis", "value": "no-intra-emphasis"},
            {"display_name": "Space Headers", "value": "space-headers"},
            {"display_name": "Math Explicit", "value": "math-explicit"},
            {"display_name": "Disable Indented Code",
                "value": "disable-indented-code"}
        ],
        default=[
            "tables"
            "fenced-code",
            "footnotes",
            "autolink",
            "strikethrough",
            "math"
        ],
        scope=Scope.content)

    editable_fields = (
        'display_name',
        'filename',
        'content',
        'extras')

    @classmethod
    def parse_xml(cls, node, runtime, keys, id_generator):
        """
        Parses the source XML in a way that preserves indenting, needed for markdown.

        """
        block = runtime.construct_xblock_from_class(cls, keys)

        # Load the data
        for name, value in node.items():
            if name in block.fields:
                value = (block.fields[name]).from_string(value)
                setattr(block, name, value)

        # Load content
        text = node.text
        if text:
            # Fix up whitespace.
            if text[0] == "\n":
                text = text[1:]
            text.rstrip()
            text = textwrap.dedent(text)
            if text:
                block.content = text

        return block

    def student_view(self, context=None):
        """
        The student view of the MarkdownCAXBlock.

        """
        if self.filename:
            # These can only be imported when the XBlock is running on the LMS
            # or CMS.  Do it at runtime so that the workbench is usable for
            # regular XML content.
            from xmodule.contentstore.content import StaticContent
            from xmodule.contentstore.django import contentstore
            from xmodule.exceptions import NotFoundError
            from opaque_keys import InvalidKeyError
            try:
                course_id = self.xmodule_runtime.course_id
                loc = StaticContent.compute_location(course_id, self.filename)
                asset = contentstore().find(loc)
                content = asset.data
            except (NotFoundError, InvalidKeyError):
                pass
        else:
            content = self.content

        html_content = ""
        if content:
            html_content = misaka.html(content, extensions=self.extras)

        # Render the HTML template
        context = {'content': html_content}
        html = loader.render_template('templates/main.html', context)
        frag = Fragment(html)

        if "fenced-code" in self.extras:
            frag.add_css_url(self.runtime.local_resource_url(
                self, 'public/css/pygments.css'))

        return frag

    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ("MarkdownCAXBlock",
             """<vertical_demo>
                <mdown_ca>
                    # This is an h1

                    ## This is an h2

                    This is a regular paragraph.

                        This is a code block.

                    ```
                    #!/bin/bash

                    echo "This is a fenced code block.
                    ```

                    ```python
                    from xblock.core import XBlock

                    class MarkdownCAXBlock(XBlock):
                        "This is a colored fence block."
                    ```

                    > This is a blockquote.

                    * This is
                    * an unordered
                    * list

                    1. This is
                    1. an ordered
                    1. list

                    [Link to cat](http://i.imgur.com/3xVUnyA.jpg)

                    ![Cat](http://i.imgur.com/3xVUnyA.jpg)
                </mdown_ca>
                </vertical_demo>
             """),
        ]
