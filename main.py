
"""Main Application"""

from markdown2 import Markdown
import jinja2
from actions_toolkit import core


md = Markdown()

template = core.get_input('template', required=True)
body = core.get_input('body', required=True)
# body = "changelog->;uncategorized->title|fix: control module status~number|1.0~url|https://github.com/vmgabriel/test-semantic-version-ga/pull/50~mergedat|2021-07-26T15:40:52.000Z~author|vmgabriel~body|content data °title|fix: control module status~number|1.0~url|https://github.com/vmgabriel/test-semantic-version-ga/pull/50~mergedat|2021-07-26T15:40:52.000Z~author|vmgabriel~body|content data ;ignored->;repo->test-semantic-version-ga;fromtag->2.0.5;totag->2.1.0;categorizedcount->0;uncategorizedcount->1;ignoredcount->0"
template_content = open(template, "r").read()
# template_content = "<html><body>{{ content|safe }}</body></html>"

# Convert markdown to html
env = jinja2.Environment()
env.filters['markdown'] = lambda text: str(md.convert(text))
env.trim_blocks = True
env.lstrip_blocks = True

email_info = env.from_string(template_content).render(**{
    "content": body,
})

dict_content = {}
main_content = body.split(";")
INTERN_CONTENTS = ["changelog", "uncategorized", "ignored"]
for content in main_content:
    data_content = content.split("->")[1]
    if len(data_content.split("~")) > 1:
        intern_data_content = data_content.split("~")
        for s_data_content in intern_data_content:
            n_data_content = {}
            s_s_data_content = s_data_content.split("|")
            n_data_content[s_s_data_content[0]] = s_s_data_content[1]
        data_content = n_data_content
    dict_content[content.split("->")[0]] = data_content

    if content.split("->")[0] in INTERN_CONTENTS and data_content == "":
        dict_content[content.split("->")[0]] = {}
main_content = dict_content

email_info = env.from_string(template_content).render(**{
    "content": body,
    "json_content": main_content,
})

core.info(f"Content body - { body }")
core.info(f"Email body - {email_info}")

core.set_output('html_data', email_info)
# print("Email info - ", main_content)
