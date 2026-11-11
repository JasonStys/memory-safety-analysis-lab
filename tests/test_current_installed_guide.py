"""Jason Stys: current named Word XML visibility and unknown binary refusal; navigation in docs/CODE_INDEX.md."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: test_current_installed_guide_keeps_xml_and_relationships_visible — line 18
# parameter: tmp_path — line 18
# variable: current — line 20
# variable: package — line 22
# variable: observed — line 31
# variable: unknown — line 34
# END CODE MAP

from zipfile import ZipFile

import pytest

from scripts.publication_text import public_text


def test_current_installed_guide_keeps_xml_and_relationships_visible(tmp_path):
    """Real named ZIP content is inspected; renaming unrelated binary files remains forbidden."""
    current = tmp_path / "docs/reports/windows-application-guide-1.1.0.docx"
    current.parent.mkdir(parents=True)
    with ZipFile(current, "x") as package:
        package.writestr("[Content_Types].xml", "<Types/>")
        package.writestr(
            "word/document.xml", "<document>reviewed-current-marker</document>"
        )
        package.writestr(
            "word/_rels/document.xml.rels",
            '<Relationships><Relationship Target="https://github.com/JasonStys"/></Relationships>',
        )
    observed = public_text(current, tmp_path)
    assert "reviewed-current-marker" in observed
    assert "github.com/JasonStys" in observed
    unknown = current.with_name("unknown-current.docx")
    unknown.write_bytes(b"\xffinert-unknown-binary")
    with pytest.raises(UnicodeDecodeError):
        public_text(unknown, tmp_path)
