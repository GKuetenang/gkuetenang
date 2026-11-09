from django.test import SimpleTestCase

from projects.admin import ProjectAdminForm


class ProjectAdminFormTests(SimpleTestCase):
    def test_tagline_uses_two_row_textarea(self):
        field = ProjectAdminForm.base_fields["tagline"]

        self.assertEqual(field.widget.attrs["rows"], 2)
        self.assertEqual(field.widget.template_name, "unfold/widgets/textarea.html")
