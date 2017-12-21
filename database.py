class Planner:
    def __init__(self):
        self.plans = []

    def new_plan(self, desc, place, time):
        self.plans.append({"desc": desc, "place": place, "time": time})

    def view_plan(self):
        for i, plan in enumerate(self.plans):
            print("{}. {}".format(str(i + 1), plan["desc"]))
