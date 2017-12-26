from datetimemgr import datetime2str, get_datetime, is_datetime
from util import sort_plans, filter_plans
import iomgr


class Planner:
    def __init__(self):
        self.plans = iomgr.load()

    def new_plan(self, chat_id, desc, place, time):
        chat_id = str(chat_id)

        if chat_id not in self.plans:
            self.plans[chat_id] = []

        self.plans[chat_id].append({"desc": desc,
                                    "loc": place,
                                    "dt": time})

        print("Added a new event!")
        iomgr.save(self.plans)

        # self.plans[chat_id] = sort_plans(self.plans[chat_id])

    def get_desc(self, chat_id, i):
        try:
            return self.plans[str(chat_id)][i]["desc"]
        except IndexError:
            return None
        except KeyError:
            return None

    def set_desc(self, chat_id, i, desc):
        try:
            self.plans[str(chat_id)][i]["desc"] = desc
            iomgr.save(self.plans)
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
            iomgr.save(self.plans)
            return "*Location is updated!* 😎"
        except IndexError:
            return False
        except KeyError:
            return False

    def get_date(self, chat_id, i):
        try:
            dt_str = self.plans[str(chat_id)][i]["dt"]

            if is_datetime(dt_str) and ":" in dt_str:
                return dt_str[:dt_str.rfind(",")]

            return dt_str
        except IndexError:
            return None
        except KeyError:
            return None

    def set_date(self, chat_id, i, date):
        try:
            chat_id = str(chat_id)
            dt_str = self.plans[chat_id][i]["dt"]
            date = datetime2str(get_datetime(date))
            time = self.get_time(chat_id, i)

            if is_datetime(dt_str) and time:
                date += ", " + time

            self.plans[chat_id][i]["dt"] = date
            iomgr.save(self.plans)
            return "*Date is updated!* 😎"
        except IndexError:
            return False
        except KeyError:
            return False

    def get_time(self, chat_id, i):
        try:
            dt_str = self.plans[str(chat_id)][i]["dt"]

            if is_datetime(dt_str):
                if ":" in dt_str:
                    return dt_str[dt_str.rfind(",") + 2:]

                return ""

            return dt_str
        except IndexError:
            return None
        except KeyError:
            return None

    def set_time(self, chat_id, i, time):
        try:
            dt_str = self.plans[str(chat_id)][i]["dt"]

            if is_datetime(dt_str):
                dt_str = self.get_date(chat_id, i) + ", " + time
                self.plans[str(chat_id)][i]["dt"] = datetime2str(get_datetime(dt_str))
            else:
                return "_Set a date first!_"

            iomgr.save(self.plans)
            return "*Time is updated!* 😎"
        except IndexError:
            return False
        except KeyError:
            return False

    def show_all(self, chat_id):
        chat_id = str(chat_id)
        filter_plans(self.plans[chat_id])

        if chat_id not in self.plans or not self.plans[chat_id]:
            return "_No events planned currently._", []

        self.plans[chat_id] = sort_plans(self.plans[chat_id])
        plans = ["{}".format(plan["desc"]) for i, plan in enumerate(self.plans[chat_id])]
        return "Choose an event from the list below:", plans

    def show(self, chat_id, i):
        try:
            event = self.plans[str(chat_id)][i]

            return "*Description*\n" \
                   "{}\n\n" \
                   "*Location\n*" \
                   "{}\n\n" \
                   "*Date/Time*\n" \
                   "{}".format(event["desc"], event["loc"], event["dt"])
        except KeyError:
            return None
        except IndexError:
            return None

    def delete(self, chat_id, i):
        try:
            del self.plans[str(chat_id)][i]
            iomgr.save(self.plans)
            return "*The event is removed!* 🙃"
        except KeyError:
            return "*The event is not found!* 😞"
        except IndexError:
            return "*This action is invalid!* 😾"
