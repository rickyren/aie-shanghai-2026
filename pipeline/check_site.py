"""Check local page links, fragment targets and duplicate IDs. Never requests external URLs."""
import argparse
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links, self.ids, self.duplicates = [], set(), []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            identifier = attrs["id"]
            if identifier in self.ids:
                self.duplicates.append(identifier)
            self.ids.add(identifier)
        for attribute in ("href", "src"):
            if attrs.get(attribute):
                self.links.append(attrs[attribute])


def check_site(root):
    root = Path(root).resolve()
    pages, issues = {}, []
    for path in sorted(root.rglob("*.html")):
        page = Page()
        text = path.read_text(encoding="utf-8")
        page.feed(text)
        pages[path] = page
        issues.extend(f"{path.relative_to(root)}: 重复 id {identifier}" for identifier in page.duplicates)
        if "{{LANDSCAPE}}" in text or "{{LOOP}}" in text:
            issues.append(f"{path.relative_to(root)}: 图形占位符尚未替换")
    if not pages:
        issues.append("没有生成 HTML 页面")
    for path, page in pages.items():
        for href in page.links:
            url = urlsplit(href)
            if url.scheme or url.netloc or href == "#":
                continue
            target = (path.parent / unquote(url.path)).resolve() if url.path else path
            if not target.is_relative_to(root):
                issues.append(f"{path.relative_to(root)}: 链接超出站点目录 {href}")
            elif not target.is_file():
                issues.append(f"{path.relative_to(root)}: 文件不存在 {href}")
            elif url.fragment and target in pages and unquote(url.fragment) not in pages[target].ids:
                issues.append(f"{path.relative_to(root)}: 锚点不存在 {href}")
    return issues


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("site", type=Path)
    args = parser.parse_args()
    issues = check_site(args.site)
    for issue in issues:
        print(issue)
    if issues:
        raise SystemExit(1)
    print("站内链接检查通过")


if __name__ == "__main__":
    main()
