from datetimemgr import datetime2str, get_datetime, is_datetime, update_year
from datetime import datetime
from util import sort_plans
from constants import *
import iomgr
import util


class Planner:
    def __init__(self):
        self.plans = iomgr.load(PLANS_JSON)
        self.history = iomgr.load("history.json")

    def new_plan(self, chat_id, desc, place, time):
        chat_id = str(chat_id)

        if chat_id not in self.plans:
            self.plans[chat_id] = []

        # util.insert_new_plan(self.plans[chat_id], {"desc": util.title(desc),
        #                                            "loc": place,
        #                                            "dt": time})

        self.plans[chat_id].append({"desc": util.title(desc),
                                    "loc": place,
                                    "dt": time})

        self.plans[chat_id] = sort_plans(self.plans[chat_id])

        print("Added a new event!")
        iomgr.save(PLANS_JSON, self.plans)

    def get_desc(self, chat_id, i):
        try:
            return self.plans[str(chat_id)][i]["desc"]
        except IndexError:
            return None
        except KeyError:
            return None

    def set_desc(self, chat_id, i, desc):
        try:
            self.plans[str(chat_id)][i]["desc"] = util.title(desc)
            iomgr.save(PLANS_JSON, self.plans)
            return "*Description is updated!* 😎"
        except IndexError:
            return False
        except KeyError:
            return False

    def get_loc(self, chat_id, i):
        try:
            return self.plans[str(chat_id)][i]["loc"]
        except IndexError:
            return None
        except KeyError:
            return None

    def set_loc(self, chat_id, i, loc):
        try:
            self.plans[str(chat_id)][i]["loc"] = loc
            iomgr.save(PLANS_JSON, self.plans)
            return "*Location is updated!* 😎"
        except IndexError:
            return False
        except KeyError:
            return False

    def get_date(self, chat_id, i):
        try:
            return util.extract_date(self.plans[str(chat_id)][i])
        except IndexError:
            return None
        except KeyError:
            return None

    def set_date(self, chat_id, i, date):
        try:
            chat_id = str(chat_id)
            plan = self.plans[chat_id][i]
            date = datetime2str(update_year(get_datetime(date)))
            time = util.extract_time(plan)

            if ":" not in date and is_datetime(plan["dt"]) and time:
                date += ", " + time

            plan["dt"] = date
            self.plans[chat_id] = sort_plans(self.plans[chat_id])
            iomgr.save(PLANS_JSON, self.plans)
            return "*Date is updated!* 😎"
        except IndexError:
            return False
        except KeyError:
            return False

    def get_time(self, chat_id, i):
        try:
            return util.extract_time(self.plans[chat_id][i])
        except IndexError:
            return None
        except KeyError:
            return None

    def set_time(self, chat_id, i, time):
        try:
            plan = self.plans[str(chat_id)][i]
            dt_str = plan["dt"]

            if is_datetime(dt_str):
                dt_str = util.extract_date(plan) + ", " + time
                plan["dt"] = datetime2str(get_datetime(dt_str))
            else:
                return "_Set a date first!_"

            self.plans[chat_id] = sort_plans(self.plans[chat_id])
            iomgr.save(PLANS_JSON, self.plans)
            return "*Time is updated!* 😎"
        except IndexError:
            return False
        except KeyError:
            return False

    def show_all(self, chat_id):
        chat_id = str(chat_id)
        plans = self.plans[chat_id]
        text = "Choose an event from the list below:"
        self.filter_plans(chat_id)

        if chat_id not in self.plans or not self.plans[chat_id]:
            return "_No events planned currently._", []

        headers = []

        # self.plans[chat_id] = sort_plans(self.plans[chat_id])
        for i, plan in enumerate(plans):
            header = plan["desc"] if "desc" in plan else plan["date"] + " »"
            headers.append(header)

        return text, headers

    def show(self, chat_id, i, group=None, history=False):
        try:
            chat_id = str(chat_id)

            if group is None:
                event = self.plans[chat_id][i] if not history else self.history[chat_id][i]
            else:
                event = self.plans[chat_id][group]["events"][i] if not history else self.history[chat_id][group]["events"][i]

            return "*Description* 📝\n" \
                   "{}\n\n" \
                   "*Location 🏖\n*" \
                   "{}\n\n" \
                   "*Date/Time* 📆🕜🕡\n " \
                   "{}".format(event["desc"], event["loc"], event["dt"])
        except KeyError:
            return None
        except IndexError:
            return None

    def delete(self, chat_id, i):
        try:
            del self.plans[str(chat_id)][i]
            iomgr.save(PLANS_JSON, self.plans)
            return "*The event is removed!* 🙃"
        except KeyError:
            return "*The event is not found!* 😞"
        except IndexError:
            return "*This action is invalid!* 😾"

    # Note: Assumed that list is sorted from earliest to latest datetime
    def filter_plans(self, chat_id):
        for i, plan in enumerate(self.plans[chat_id]):
            if not is_datetime(plan['dt']) or get_datetime(plan['dt']) >= datetime.now():
                return

            self.move_to_history(chat_id, i, plan)

    def move_to_history(self, chat_id, i, plan):
        print(plan['desc'] + " is outdated!")
        self.save_history(chat_id, plan)
        self.delete(chat_id, i)

    def save_history(self, chat_id, plan):
        print(plan["desc"] + " saved to history!")

        if self.history is None:
            self.history = dict()

        if chat_id not in self.history:
            self.history[chat_id] = []

        self.history[chat_id].append(plan)
        iomgr.save(HISTORY_JSON, self.history)

    def show_history(self, chat_id):
        chat_id = str(chat_id)
        self.filter_plans(chat_id)

        if self.history is None or chat_id not in self.history or not self.history[chat_id]:
            return "_No events planned._", []

        # self.history[chat_id] = sort_plans(self.history[chat_id])
        plans = ["{}".format(plan["desc"]) for i, plan in enumerate(self.history[chat_id])]
        return "_Every_ *moment* _we share together_\n" \
               "_is even better than the_ *moment* _before._\n" \
               "_If everyday was as good as_ *today* _was_\n" \
               "_then I can't wait till_ *tomorrow* _comes_...", plans


