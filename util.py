import re


def parse(text):
    command = ""
    content = text

    if re.search("^/(?=\w)", text):
        split = text.split(' ', 1)
        command, content = split[0], ""

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
