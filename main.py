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
    return f"""#### [Title: {change['title']} - PR: {change['number']}]({change['url']}, "url")
    Merged At: {change['mergedat']}
    Author: {change['author']}
    Body:
    {change['body']}\n
    """

def to_markdown(content: dict) -> str:
    changelog = ""
    if content["changelog"]:
        if content["changelog"]["Features"]:
            changelog += "### Features\n"
            changelog += "".join(
                [change_to_md(change) for change in content["changelog"]["Features"]]
            )

        if content["changelog"]["Fixes"]:
            changelog += "### Fixes\n"
            changelog += "".join(
                [change_to_md(change) for change in content["changelog"]["Fixes"]]
            )

        if content["changelog"]["Tests"]:
            changelog += "### Tests\n"
            changelog += "".join(
                [change_to_md(change) for change in content["changelog"]["Tests"]]
            )

    uncategorized = ""
    if content["uncategorized"]:
        uncategorized += "### Uncategorized\n"
        uncategorized += "".join(
            [change_to_md(change) for change in content["uncategorized"]]
        )

    ignored = ""
    if content["ignored"]:
        ignored += "### Ignored\n"
        ignored += "".join(
            [change_to_md(change) for change in content["ignored"]]
        )

    return f"""
    # Fithub {content['repo']}
    ## Update:
       {content['fromtag']} -> {content['totag']}
    -----
    Count Categorized: {content['categorizedcount']}

    {changelog}
    -----
    Count Uncategorized: {content['uncategorizedcount']}

    {uncategorized}
    -----
    Count Ignored: {content['ignored_count']}

    {ignored}
    """


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
