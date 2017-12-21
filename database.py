class Planner:
    def __init__(self):
        self.plans = dict()

    def new_plan(self, chat_id, desc, place, time):
        if chat_id not in self.plans:
            self.plans[chat_id] = []

        self.plans[chat_id].append({"desc": desc,
                                    "place": place,
                                    "time": time})

    def view_plan(self):
        for i, plan in enumerate(self.plans):
            print("{}. {}".format(str(i + 1), plan["desc"]))
