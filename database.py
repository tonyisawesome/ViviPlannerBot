from datetimemgr import datetime2str


class Planner:
    def __init__(self):
        self.plans = dict()

    def new_plan(self, chat_id, desc, place, time):
        if chat_id not in self.plans:
            self.plans[chat_id] = []

        self.plans[chat_id].append({"desc": desc,
                                    "loc": place,
                                    "time": time})

    def show_all(self, chat_id):
        if chat_id not in self.plans:
            return "*No events found!* 😞"

        if not self.plans[chat_id]:
            return "No events planned currently.\n\n😪 *B O R I N G* 😪"

        plans = ["{}. {}".format(str(i + 1), plan["desc"]) for i, plan in enumerate(self.plans[chat_id])]
        return "*Events*\n\n" + '\n'.join(plans)

    def show(self, chat_id, i):
        try:
            event = self.plans[chat_id][i]

            return "*Event*\n" \
                   "{}\n\n" \
                   "*Location\n*" \
                   "{}\n\n" \
                   "*Date/Time*\n" \
                   "{}".format(event["desc"], event["loc"], datetime2str(event["time"]))
        except IndexError:
            return "The number you have entered is invalid."

    def delete(self, chat_id, i):
        try:
            del self.plans[chat_id][i]
            return "*The event is removed!* 🙃"
        except KeyError:
            return "The number you have entered is invalid."
