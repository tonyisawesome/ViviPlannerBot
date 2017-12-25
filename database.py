from datetimemgr import datetime2str, str2datetime
import datetime
from util import sort_plans
import iomgr


class Planner:
    def __init__(self):
        self.plans = dict()

    def new_plan(self, chat_id, desc, place, time):
        if chat_id not in self.plans:
            self.plans[chat_id] = []

        self.plans[chat_id].append({"desc": desc,
                                    "loc": place,
                                    "dt": time})

        # self.plans[chat_id] = sort_plans(self.plans[chat_id])

    def get_desc(self, chat_id, i):
        try:
            return self.plans[chat_id][i]["desc"]
        except IndexError:
            return None
        except KeyError:
            return None

    def set_desc(self, chat_id, i, desc):
        try:
            self.plans[chat_id][i]["desc"] = desc
            return "*Description is updated!* 😎"
        except IndexError:
            return False
        except KeyError:
            return False

    def get_loc(self, chat_id, i):
        try:
            return self.plans[chat_id][i]["loc"]
        except IndexError:
            return None
        except KeyError:
            return None

    def set_loc(self, chat_id, i, loc):
        try:
            self.plans[chat_id][i]["loc"] = loc
            return "*Location is updated!* 😎"
        except IndexError:
            return False
        except KeyError:
            return False

    def get_date(self, chat_id, i):
        try:
            dt = self.plans[chat_id][i]["dt"]

            if type(dt) is datetime.datetime:
                string = datetime2str(dt)

                if ":" not in string:
                    return string

                return string[:string.rfind(",")]

            return dt
        except IndexError:
            return None
        except KeyError:
            return None

    def set_date(self, chat_id, i, date):
        try:
            dt = self.plans[chat_id][i]["dt"]

            if type(dt) is datetime.datetime:
                date += " " + self.get_time(chat_id, i)

            self.plans[chat_id][i]["dt"] = str2datetime(date)
            return "*Date is updated!* 😎"
        except IndexError:
            return False
        except KeyError:
            return False

    def get_time(self, chat_id, i):
        try:
            dt = self.plans[chat_id][i]["dt"]

            if type(dt) is datetime.datetime:
                string = datetime2str(dt)

                if ":" in string:
                    return string[string.rfind(",") + 2:]

                return ""

            return dt
        except IndexError:
            return None
        except KeyError:
            return None

    def set_time(self, chat_id, i, time):
        try:
            dt = self.plans[chat_id][i]["dt"]

            if type(dt) is datetime.datetime:
                time += " " + self.get_date(chat_id, i)
                self.plans[chat_id][i]["dt"] = str2datetime(time)
            else:
                return "_Set a date first!_ "

            return "*Time is updated!* 😎"
        except IndexError:
            return False
        except KeyError:
            return False

    def show_all(self, chat_id):
        if chat_id not in self.plans or not self.plans[chat_id]:
            return "_No events planned currently._", []

        self.plans[chat_id] = sort_plans(self.plans[chat_id])
        plans = ["{}".format(plan["desc"]) for i, plan in enumerate(self.plans[chat_id])]
        return "Choose an event from the list below:", plans

    def show(self, chat_id, i):
        try:
            event = self.plans[chat_id][i]

            return "*Description*\n" \
                   "{}\n\n" \
                   "*Location\n*" \
                   "{}\n\n" \
                   "*Date/Time*\n" \
                   "{}".format(event["desc"], event["loc"], datetime2str(event["dt"]))
        except KeyError:
            return None
        except IndexError:
            return None

    def delete(self, chat_id, i):
        try:
            del self.plans[chat_id][i]
            return "*The event is removed!* 🙃"
        except KeyError:
            return "*The event is not found!* 😞"
        except IndexError:
            return "*This action is invalid!* 😾"

    def save(self):
        data = dict()

        for chat_id, plans in self.plans.items():
            if chat_id not in data:
                data[chat_id] = []

            for plan in self.plans:
                plan
