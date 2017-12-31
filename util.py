import re
from datetimemgr import is_datetime, get_datetime


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
        if is_datetime(plan['dt']):
            with_dt.append(plan)
        else:
            without_dt.append(plan)

    with_dt = sorted(with_dt,
                     key=lambda x: get_datetime(x['dt']))

    return with_dt + without_dt


def extract_date(plan):
    dt_str = plan["dt"]

    if is_datetime(dt_str) and ":" in dt_str:
        return dt_str[:dt_str.rfind(",")]

    return dt_str


def extract_time(plan):
    dt_str = plan["dt"]

    if is_datetime(dt_str):
        if ":" in dt_str:
            return dt_str[dt_str.rfind(",") + 2:]

        return ""

    return dt_str


def title(string):
    tokens = string.split()

    for i, token in enumerate(tokens):
        tokens[i] = token[0].title() + token[1:]

    return ' '.join(tokens)


# def insert_new_plan(plans, new_plan):
#     for i, plan in enumerate(plans):
#         if "date" in plan and plan["date"] == extract_date(new_plan):
#             plan["events"].append(new_plan)
#             return
#         elif "date" not in plan:
#             date = extract_date(plan)
#
#             if date == extract_date(new_plan):
#                 # Move existing date to group
#                 tmp = {"date": date, "events": [plan]}
#
#                 # Sort between existing plan and new plan
#                 if get_datetime(plan["dt"]) < get_datetime(new_plan["dt"]):
#                     tmp["events"].append(new_plan)
#                 else:
#                     tmp["events"].insert(0, new_plan)
#
#                 plans.append(tmp)
#                 del plans[i]
#                 return
#
#     plans.append(new_plan)
