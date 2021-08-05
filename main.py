"""Main Application"""

from markdown2 import Markdown
import jinja2
import re
from actions_toolkit import core


md = Markdown()

template = core.get_input('template', required=True)
body = core.get_input('body', required=True)
message_commit = core.get_input('message_commit', required=True)

template_content = open(template, "r").read()


# Convert markdown to html
env = jinja2.Environment()
env.filters['markdown'] = lambda text: str(md.convert(text))
env.trim_blocks = True
env.lstrip_blocks = True

email_info = env.from_string(template_content).render(**{
    "content": body,
})

# Generate Mode of staging
REGEX = r"{(\b\w+\b)}"
result = re.search(REGEX, message_commit)
LEVELS = ["major", "minor", "patch"]
level = None
if result:
    level = result.groups()[0]
    if level not in LEVELS:
        level = None


core.info(f"Content body - { body }")
core.info(f"Email body - {email_info}")

core.set_output('html_data', email_info)
core.set_output('level', level)
