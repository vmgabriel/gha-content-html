
"""Main Application"""

import jinja2
import json
from typing import List
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

email_info = env.from_string(template_content).render(**{
    "content": body,
})


def convert_to_list(content_str: str) -> List[dict]:
    prs = content_str.split("(^)")[:-1]
    content_prs = []
    for pr in prs:
        content_pr = {}
        pr_datas = pr.split("(~)")
        for pr_data in pr_datas:
            min_data = pr_data.split("(|)")
            content_pr[min_data[0]] = min_data[1]
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
