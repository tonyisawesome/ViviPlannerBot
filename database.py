class Planner:
    def __init__(self):
        self.plans = dict()

    def new_plan(self, chat_id, desc, place, time):
        if chat_id not in self.plans:
            self.plans[chat_id] = []

        self.plans[chat_id].append({"desc": desc,
                                    "loc": place,
                                    "time": time})

    def view_plan(self, chat_id):
        if chat_id not in self.plans:
            return "*No events found!*"

        plans = ["{}. {}".format(str(i + 1), plan["desc"]) for i, plan in enumerate(self.plans[chat_id])]
        return "*Events*\n\n" + '\n'.join(plans)
