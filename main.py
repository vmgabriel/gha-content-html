"""Main Application"""

from typing import List
import jinja2
from markdown2 import Markdown
from actions_toolkit import core


md = Markdown()

template = core.get_input('template', required=True)
body = core.get_input('body', required=True)

template_content = open(template, "r").read()

# Convert markdown to html
env = jinja2.Environment()
env.filters['markdown'] = lambda text: str(md.convert(text))
env.trim_blocks = True
env.lstrip_blocks = True

def change_to_md(change: dict) -> str:
    return f"""#### [Title: {change.get('title')} - PR: {change.get('number')}]({change.get('url')}, "url")\nMerged At: {change.get('mergedat')}\nAuthor: {change.get('author')}\nBody:\n{change.get('body')}\n"""

def to_markdown(content: dict) -> str:
    changelog = ""
    if content.get("changelog"):
        if content.get("changelog").get("Features"):
            changelog += "### Features\n"
            changelog += "".join(
                [change_to_md(change) for change in content.get("changelog").get("Features")]
            )

        if content.get("changelog").get("Fixes"):
            changelog += "### Fixes\n"
            changelog += "".join(
                [change_to_md(change) for change in content.get("changelog").get("Fixes")]
            )

        if content.get("changelog").get("Tests"):
            changelog += "### Tests\n"
            changelog += "".join(
                [change_to_md(change) for change in content.get("changelog").get("Tests")]
            )

    uncategorized = ""
    if content.get("uncategorized"):
        uncategorized += "### Uncategorized\n"
        uncategorized += "".join(
            [change_to_md(change) for change in content.get("uncategorized")]
        )

    ignored = ""
    if content.get("ignored"):
        ignored += "### Ignored\n"
        ignored += "".join(
            [change_to_md(change) for change in content.get("ignored")]
        )

    return f"""#Fithub {content.get('repo')}\n## Update:\n  {content.get('fromtag')} -> {content.get('totag')}\n-----\n## Count Categorized: {content.get('categorizedcount')}\n\n{changelog}\n-----\n## Count Uncategorized: {content.get('uncategorizedcount')}\n\n{uncategorized}\n-----\n## Count Ignored: {content.get('ignored_count')}\n\n{ignored}"""


def get_content_relese(content: str) -> dict:
    """Generate Content of release note description"""
    content_to_split = "## Release Note Description:"
    content_data = content.split(content_to_split)
    if len(content_data) > 1:
        return content_data[-1]
    return ""


def convert_to_list(content_str: str) -> List[dict]:
    """Convert to List"""
    prs = content_str.split("(^)")[:-1]
    content_prs = []
    for pr in prs:
        content_pr = {}
        pr_datas = pr.split("(~)")
        for pr_data in pr_datas:
            min_data = pr_data.split("(|)")
            min_data_content = min_data[1]
            if min_data[0] == "body":
                min_data_content = get_content_relese(min_data_content)
                if min_data_content != "":
                    min_data_content = md.convert(min_data_content)
            content_pr[min_data[0]] = min_data_content
        content_prs.append(content_pr)
    return content_prs


dict_content = {}
main_content = body.split("(;)")
INTERN_CONTENTS = ["changelog", "uncategorized", "ignored"]
for content in main_content:
    data_content = content.split("(->)")[1]

    changes_content = data_content.split("(°)\n\n")
    if len(changes_content) > 1:
        data_content = changes_content[:-1]

        state_content = {}
        for cont_pos in range(len(data_content) // 2):
            state_content[data_content[2 * cont_pos]] = convert_to_list(
                data_content[(2 * cont_pos) + 1]
            )
        data_content = state_content

    if content.split("(->)")[0] == INTERN_CONTENTS[0] and data_content == "":
        data_content = []

    if content.split("(->)")[0] in INTERN_CONTENTS[1:]:
        data_content = convert_to_list(data_content)

    dict_content[content.split("(->)")[0]] = data_content
main_content = dict_content

email_info = env.from_string(template_content).render(**{
    "content": body,
    "json_content": main_content,
})

core.info(f"Content body - { body }")
core.info(f"Email body - {email_info}")

core.set_output('html_data', email_info)
core.set_output('markdown_data', to_markdown(main_content))

