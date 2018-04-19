init -23 python:
    class Division(renpy.store.object):
        def __init__(self, name="Freelancer", people=None, room=None, jobs=None):
            self.name = name
            self.people = set(people or []) # may be away, test room.people for non-absensent
            self.jobs = set(jobs or [name])
            self.room = getattr(world, room)
            self.serum = None
            self.uniform = None

        def give_daily_serum(self, serum_inventory, message_list):
            if self.serum:
                for person in self.room.people:
                    if serum_inventory[self.serum] == 0:
                        message_list["Stockpile ran out of %s to give to the %s division." % (self.serum.name, self.name.lower())] = 0
                        return
                    serum_inventory[self.serum] -= 1
                    person.give_serum(copy.copy(self.serum)) #use a copy rather than the main class, so we can modify and delete the effects without changing anything else.

        def remove_employee(self, the_person):
            self.people.remove(the_person)
            if the_person in self.room.people:
                self.room.people.remove(the_person)

    class Marketing(Division):
        def __init__(self):
            self.inventory = collections.defaultdict(default_to_zero)
            self.sold = 0
            super(Marketing, self).__init__("Marketing", [], "m_room")

        def work(self, corp):
            corp.funds -= self.sold
            for person in self.room.people: #Check to see if the person is in the room, otherwise don't count their progress (they are at home, dragged away by PC, weekend, etc.)
                if person.job in self.jobs:

                    serum_sale_count = __builtin__.round((3*person.charisma + person.focus + 2*person.market_skill + 10) * corp.team_effectiveness)/100 #Total number of doses of serum that can be sold by this person.

                    #For use with value boosting policies. Multipliers are multiplicative.
                    #If there is a uniform and we have the policy to increase value based on that we change the multilier.
                    serum_value_multiplier = self.uniform.slut_requirement/100.0 + 1 if self.uniform and "Male Focused Modeling" in corp.active_policies else 1.00

                    for serum, count in sorted(self.inventory["serum"].iteritems(), key=lambda serum, count: corp.production.serum_design[serum]["value"]):
                        # if there is not capacity enough to process all, process remainder and break
                        count = min(serum_sale_count, count)
                        self.sold += count * corp.production.serum_design[serum]["value"] * serum_value_multiplier
                        self.inventory["serum"][serum] -= count
                        serum_sale_count -= count
                        if serum_sale_count == 0:
                            break
                    else: # if all serums were all sold, nothing more to do for any next person.
                        break
            corp.funds += self.sold

    class Research(Division):
        def __init__(self):
            self.progress = 0 #How much research the team produced today.
            self.subject = None #
            super(Research, self).__init__("Research and Development", [], "rd_room", ["Researcher"])

        def is_drug(self):
            return self.subject and "value" in self.subject

        def work(self, corp):
            if self.subject:
                remain = self.subject["research required"] - self.subject["research done"]
                self.progress += remain
                for person in self.room.people:
                    if person.job in self.jobs:
                        remain -= __builtin__.round((3*person.int + person.focus + 2*person.research_skill + 10) * corp.team_effectiveness)/100

                        if remain <= 0: #Returns true if the research is completed by this amount'
                            if "value" in self.subject: # its a drug
                                corp.mandatory_crises_list.append(Action("Research Finished Crisis",serum_creation_crisis_requirement,"serum_creation_crisis_label",self.subject)) #Create a serum finished crisis, it will trigger at the end of the round
                            corp.message_list["Finished researching: %s" % self.subject["name"]] = 0
                            self.subject = None
                            return
                self.subject["research done"] = self.subject["research required"] - remain
                self.progress -= remain

    class Production(Division):
        def __init__(self):
            self.inventory = collections.defaultdict(default_to_zero)
            self.used = 0 #How many production points were actually used to make something.
            self.points = 0
            self.serum = None
            self.serum_design = {}
            self.auto_sell_threshold = 0
            super(Production, self).__init__("Production", [], "p_room")

        def work(self, corp):
            if self.serum != None:
                remain = corp.supply.count
                self.used += remain
                production_count = 0
                for person in self.room.people:
                    if person.job in self.jobs:
                        production_amount = min(remain, __builtin__.round((3*person.focus + person.int + 2*person.production_skill + 10) * corp.team_effectiveness)/100)

                        ##Check how many serum can be made, make them and add them to your inventory.

                        cost = self.serum_design[self.serum]["production"]
                        self.points += production_amount
                        production_count += self.points // cost
                        self.points %= cost

                        remain -= production_amount
                        if remain == 0:
                            break

                corp.supply.count = remain
                self.used -= remain

                if production_count > 0:

                    msg = "Produced %s" % self.serum
                    corp.message_list[msg] = corp.message_list.get(msg, 0) + production_count

                    for_sale_count = max(0, self.inventory["serum"][self.serum] + production_count - self.auto_sell_threshold)
                    self.inventory["serum"][self.serum] -= for_sale_count
                    corp.marketing.inventory["serum"][self.serum] += for_sale_count


        def add_serum_design(self,serum):
            while not "name" in serum:
                name = renpy.input("Please give this serum design a name.")
                if not name or name in self.serum_design:
                    renpy.say("", "That name is already registered. Please use another.")
                else:
                    serum["name"] = name
            self.serum_design[name] = serum

        def change(self,new_serum):
            self.serum = new_serum
            self.auto_sell_threshold = None
            self.points = 0

    class Supply(Division):
        def __init__(self):
            self.count = 0
            self.goal = 250
            self.purchased = 0
            super(Supply, self).__init__("Supply Procurement", [], "office", ["Supply"])

        def work(self, corp):
            corp.funds += self.count
            self.purchased -= self.count  #Used for end of world.day reporting
            for person in self.room.people:
                if person.job in self.jobs:
                    self.count += max(0, min(__builtin__.round((3*person.focus + person.charisma + 2*person.supply_skill + 10) * corp.team_effectiveness)/100, self.goal - self.count))
            corp.funds -= self.count
            self.purchased += self.count

    class HumanResources(Division):
        def __init__(self):
            super(HumanResources, self).__init__("Human Resources", [], "office")

        def work(self, corp): #Don't compute efficency cap here so that player HR effort will be applied against any efficency drop even though it's run before the rest of the end of the turn.
            for person in self.room.people:
                if person.job in self.jobs:
                    corp.team_effectiveness += 3*person.charisma + person.int + 2*person.hr_skill + 10

    class Business(renpy.store.object):
        def __init__(self, name, division):
            self.name = name
            self.division = division
            self.inventory = {"stock": collections.defaultdict(default_to_zero), "sale": collections.defaultdict(default_to_zero)}

    class Store(Business):
        def __init__(self, **kwargs):
            super(MyCorp, self).__init__(**kwargs)

    class MyCorp(Business):
        # main jobs to start with:
        # 1) buying raw supplies.
        # 2) researching new serums.
        # 2a) The player (only) designs new serums to be researched.
        # 3) working in the lab to produce serums.
        # 4) Working in marketing. Increases volumn you can sell, and max price you can sell for.
        # 5) Packaging and selling serums that have been produced.
        # 6) General secretary work. Starts at none needed, grows as your company does (requires an "HR", eventually). Maybe a general % effectivness rating.
        def __init__(self):
            # marketing etc: The phsyical locations of all of the teams, so you can move to different offices in the future.
            name = persistent.company_name

            # Increases company marketability. Raises max price serum can be sold for, and max volumn that can be sold.
            self.marketing = Marketing()

            # Physically makes the serum and sends it off to be sold.
            self.production = Production()

            # Researches new serums that the player designs, does theoretical research into future designs, or improves old serums slightly over time
            self.research = Research()

            # Buys the raw supplies used by the other departments.
            self.supply = Supply()

            # Manages everyone else and improves effectiveness. Needed as company grows.
            self.hr = HumanResources()
            super(MyCorp, self).__init__(name, [self.supply, self.production, self.marketing, self.research, self.hr])

            self.funds = 1000 #Your starting wealth.

            self.bankrupt_days = 0 #How many world.days you've been bankrupt. If it hits the max value you lose.
            self.max_bankrupt_days = 3 #How many world.days you can be negative without loosing the game. Can be increased through research.

            self.marketability = 0
            self.team_effectiveness = 100 #Ranges from 50 (Chaotic, everyone functions at 50% speed) to 200 (masterfully organized). Normal levels are 100, special traits needed to raise it higher.
            self.effectiveness_cap = 100 #Max cap, can be raised.

            self.interview_cost = 50

            self.serum_traits = default_serum_traits

            self.active_policies = set()

            self.message_list = {} # This dict stores unique and counts message. If 0 it is shown once without a count at the end of the world.day.

            self.mandatory_crises_list = [] #A list of crises to be resolved at the end of the turn, generally generated by events that have taken place.

        def run_turn(self): #Run each time the time segment changes. Most changes are done here.

            #Compute efficency drop
            for div in self.division:
                for person in div.room.people: #Only people in the office lower effectiveness, no loss on weekends, not in for the world.day, etc.
                    if person.job in div.jobs:
                        self.team_effectiveness -= 1 #TODO: Make this dependant on charisma (High charisma have a lower impact on effectiveness) and happiness.

            #Compute effiency rise from HR
            self.hr.work(self)

            self.team_effectiveness = min(max(50, self.team_effectiveness), self.effectiveness_cap)

            #Compute other deparement effects
            for div in self.division:
                if div != self.hr:
                    div.work(self)

        def payout(self): #Run at the end of the world.day.
            #Pay everyone for the world.day
            self.funds -= self.calculate_salary_cost()
            if self.funds < 0:
                self.bankrupt_days += 1
                days_remaining = self.max_bankrupt_days - self.bankrupt_days
                if days_remaining:
                    renpy.say("","Warning! Your company is losing money and unable to pay salaries or purchase necessary supplies! You have %d world.days to restore yourself to positive funds or you will be foreclosed upon!" % days_remaining)
                else:
                    renpy.say("","With no funds to pay your creditors you are forced to close your business and auction off all of your materials at a fraction of their value. Your story ends here.")
                    renpy.full_restart()
            else:
                self.bankrupt_days = 0

        def get_uniform(self, job): #Takes a division (a room) and returns the correct uniform for that division, if one exists. If it is None, returns false.
            return next((div.uniform for div in self.division if job in div.jobs), None)

        def clear_messages(self): #clear all messages for the world.day.
            self.message_list = {} # This dict stores unique and counts message. If 0 it is shown once without a count at the end of the world.day.
            self.supply.purchased = 0
            self.production.used = 0 #How many production points were actually used to make something.
            self.research.progress = 0 #How much research the team produced today.
            self.marketing.sold = 0

        def calculate_salary_cost(self):
            return sum(person.salary for person in self.get_employee_list())

        def add_employee(self, new_person, division, job=None, to_room_as_well=True):
            division.people.add(new_person)
            new_person.job = job or renpy.random.sample(division.jobs, 1)[0]
            if to_room_as_well:
                division.room.people.add(new_person)

        def remove_employee(self, the_person):
            return next((div.remove_employee(the_person) for div in self.division if the_person in div.people), None)

        def is_employee(self, person):
            return any(person in div.people for div in self.division)

        def get_employee_list(self):
            return [people for div in self.division for people in div.people]

        def get_employee_count(self):
            return sum(len(div.people) for div in self.division)

        def get_max_employee_slut(self):
            #return -1 for an empty business, all calls should require at least sluttiness 0
            return max(getattr(_, "sluttiness", -1) for _ in self.get_employee_list())

        def get_employee_title(self, the_person):
            return next((the_person.job for div in self.division if the_person in div.people), "None")

        def give_daily_serum(self):
            for div in self.division:
                div.give_daily_serum(self.inventory["stock"]["serum"], self.message_list)

        def purchase_policy(self, policy):
            self.funds -= policy.cost
            self.active_policies.add(policy)

        def get_max_outfits_to_change(self):
            return max(policies[_].get("max_outfits_to_change", 0) for _ in self.active_policies)


