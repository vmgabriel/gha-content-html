"""Main Application"""

import markdown
import jinja2
from actions_toolkit import core


md = markdown.Markdown(extensions=['meta'])

template = core.get_input('template', required=True)
body = core.get_input('body', required=True)

template_content = open(template, "r").read()

env = jinja2.Environment()
env.filters['markdown'] = lambda text: jinja2.Markup(md.convert(text))
env.trim_blocks = True
env.lstrip_blocks = True

email_info = env.from_string(template_content).render(**{
    "content": body,
})

core.info(f"Content body - { body }")
core.info(f"Email body - {email_info}")

core.set_output('html_data', email_info)
