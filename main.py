"""Main Application"""

from actions_toolkit import core
from jinja2 import Template


template = core.get_input('template', required=True)
body = core.get_input('body', required=True)

template_content = open(template, "r").read()
template = Template(template_content)

email_info = template.render(**{
    "content": body,
})

core.info("Content body -", body)
core.info("Email body -", email_info)

core.set_output('html_data', email_info)
