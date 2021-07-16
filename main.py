"""Main Application"""

from actions_toolkit import core
from jinja2 import Environment, select_autoescape, FileSystemLoader


content_body = core.get_input('body', required=True)

env = Environment(loader=FileSystemLoader("app"), autoescape=select_autoescape())
template = env.get_template("template.html")

email_info = template.render(**{
    "content_body": content_body
})

core.info("Content body -", content_body)
core.info("Email body -", email_info)

core.set_output('html_data', email_info)
