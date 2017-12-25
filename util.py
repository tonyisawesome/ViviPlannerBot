import re
from datetime import datetime


def parse(text):
    command = ""
    content = text

    if re.search("^/(?=\w)", text):
        split = text.split(' ', 1)
        command, content = split[0], ""

        if "@" in command:
            command = command[:re.search("@", command).start()]

        if len(split) == 2:
            content = split[1]

    return command, content


def build_menu(buttons,
               n_cols=1,
               header_buttons=None,
               footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]

    if header_buttons is not None:
        menu.insert(0, header_buttons)
    if footer_buttons is not None:
        menu.append(footer_buttons)

    return menu


def sort_plans(plans):
    with_dt = []
    without_dt = []

    for plan in plans:
        if type(plan['dt']) is datetime:
            with_dt.append(plan)
        else:
            without_dt.append(plan)

    with_dt = sorted(with_dt,
                     key=lambda x: x['dt'])

    return with_dt + without_dt
