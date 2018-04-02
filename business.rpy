init -18 python:

    class Business(renpy.store.object):
        # main jobs to start with:
        # 1) buying raw supplies.
        # 2) researching new serums.
        # 2a) The player (only) designs new serums to be researched.
        # 3) working in the lab to produce serums.
        # 4) Working in marketing. Increases volumn you can sell, and max price you can sell for.
        # 5) Packaging and selling serums that have been produced.
        # 6) General secretary work. Starts at none needed, grows as your company does (requires an "HR", eventually). Maybe a general % effectivness rating.
        def __init__(self, name, m_room, p_room, rd_room, s_room, h_room):
            self.name = name
            self.funds = 1000 #Your starting wealth.

            self.bankrupt_days = 0 #How many days you've been bankrupt. If it hits the max value you lose.
            self.max_bankrupt_days = 3 #How many days you can be negative without loosing the game. Can be increased through research.

            # m_div etc: The phsyical locations of all of the teams, so you can move to different offices in the future.

            # Increases company marketability. Raises max price serum can be sold for, and max volumn that can be sold.
            self.m_div = Division("Marketing", [], m_room)

            # Physically makes the serum and sends it off to be sold.
            self.p_div = Division("Production", [], p_room)

            # Researches new serums that the player designs, does theoretical research into future designs, or improves old serums slightly over time
            self.r_div = Division("Research and Development", [], rd_room, "Researcher")

            # Buys the raw supplies used by the other departments.
            self.s_div = Division("Supply Procurement", [], s_room, "Supply")

            # Manages everyone else and improves effectiveness. Needed as company grows.
            self.h_div = Division("Human Resources", [], h_room)

            self.division = [self.m_div, self.p_div, self.r_div, self.s_div, self.h_div]

            self.supply_count = 0
            self.supply_goal = 250
            self.auto_sell_threshold = None
            self.marketability = 0
            self.production_points = 0
            self.team_effectiveness = 100 #Ranges from 50 (Chaotic, everyone functions at 50% speed) to 200 (masterfully organized). Normal levels are 100, special traits needed to raise it higher.
            self.effectiveness_cap = 100 #Max cap, can be raised.

            self.serum_designs = []
            self.active_research_design = None #

            self.serum_production_target = None
            self.inventory = SerumInventory([])
            self.sale_inventory = SerumInventory([])

            self.available_policies = set() # available: it can be bought
            self.active_policies = set()

            self.message_list = [] #This list of strings is shown at the end of each day on the business update screen. Cleared each day.
            self.counted_message_list = {} #This is a dict holding the count of each message stored in it. Used when you want to have a message that is counted and the total shown at the end of the day.
            self.production_potential = 0 #How many production points the team was capable of
            self.supplies_purchased = 0
            self.production_used = 0 #How many production points were actually used to make something.
            self.research_produced = 0 #How much research the team produced today.
            self.sales_made = 0

            self.mandatory_crises_list = [] #A list of crises to be resolved at the end of the turn, generally generated by events that have taken place.

        def run_turn(self): #Run each time the time segment changes. Most changes are done here.

            #Compute efficency drop
            for div in self.division:
                for person in div.people: #Only people in the office lower effectiveness, no loss on weekends, not in for the day, etc.
                    if person in div.room.people:
                        self.team_effectiveness += -1 #TODO: Make this dependant on charisma (High charisma have a lower impact on effectiveness) and happiness.

            #Compute effiency rise from HR
            for person in self.m_div.people:
                if person in div.room.people:
                    self.hr_progress(person.charisma,person.int,person.hr_skill)

            if self.team_effectiveness < 50:
                self.team_effectiveness = 50

            if self.team_effectiveness > self.effectiveness_cap:
                self.team_effectiveness = self.effectiveness_cap

            #Compute other deparement effects
            for person in self.s_div.people: #Check to see if the person is in the room, otherwise don't count their progress (they are at home, dragged away by PC, weekend, etc.)
                if person in div.room.people:
                    self.supply_purchase(person.focus,person.charisma,person.supply_skill)

            for person in self.r_div.people:
                if person in div.room.people:
                    self.research_progress(person.int,person.focus,person.research_skill)

            for person in self.p_div.people:
                if person in div.room.people:
                    self.production_progress(person.focus,person.int,person.production_skill)

            for person in self.m_div.people:
                if person in div.room.people:
                    self.sale_progress(person.charisma,person.focus,person.market_skill)

        def run_day(self): #Run at the end of the day.
            #Pay everyone for the day
            cost = self.calculate_salary_cost()
            self.funds += -cost

            return

        def is_open_for_business(self): #Checks to see if employees are currently working
            if time_of_day == 1 or time_of_day == 2 or time_of_day == 3: #TODO: give people the weekends off.
                return True
            else:
                return False

        def get_uniform(self,title): #Takes a division (a room) and returns the correct uniform for that division, if one exists. If it is None, returns false.
            for div in self.division:
                if title == div.employment_title:
                    return div.uniform

        def clear_messages(self): #clear all messages for the day.
            self.message_list = []
            self.counted_message_list = {}
            self.production_potential = 0
            self.supplies_purchased = 0
            self.production_used = 0
            self.research_produced = 0
            self.sales_made = 0

        def add_counted_message(self,message,new_count):
            if message in self.counted_message_list:
                self.counted_message_list[message] += new_count
            else:
                self.counted_message_list[message] = new_count

        def calculate_salary_cost(self):
            daily_cost = 0
            for person in self.get_employee_list():
                daily_cost += person.salary
            return daily_cost

        def add_serum_design(self,the_serum):
            self.serum_designs.append(the_serum)

        def set_serum_research(self,new_research):
            self.active_research_design = new_research

        def research_progress(self,int,focus,skill):
            research_amount = __builtin__.round(((3*int) + (focus) + (2*skill) + 10) * (self.team_effectiveness))/100
            self.research_produced += research_amount
            if self.active_research_design != None:
                if self.active_research_design.add_research(research_amount): #Returns true if the research is completed by this amount'
                    if type(self.active_research_design) is SerumDesign:
                        self.mandatory_crises_list.append(Action("Research Finished Crisis",serum_creation_crisis_requirement,"serum_creation_crisis_label",self.active_research_design)) #Create a serum finished crisis, it will trigger at the end of the round
                    self.message_list.append("Finished researching: " + self.active_research_design.name)
                    self.active_research_design = None

        def player_research(self):
            self.research_progress(mc.int,mc.focus,mc.research_skill)

        def player_buy_supplies(self):
            self.supply_purchase(mc.focus,mc.charisma,mc.supply_skill)

        def supply_purchase(self,focus,cha,skill):
            max_supply = __builtin__.round(((3*focus) + (cha) + (2*skill) + 10) * (self.team_effectiveness))/100
            if max_supply + self.supply_count > self.supply_goal:
                max_supply = self.supply_goal - self.supply_count
                if max_supply <= 0:
                    return

            self.funds += -max_supply
            self.supply_count += max_supply
            self.supplies_purchased += max_supply #Used for end of day reporting

        def player_market(self):
            self.sale_progress(mc.charisma,mc.focus,mc.market_skill)

        def sale_progress(self,cha,focus,skill):

            serum_value_multiplier = 1.00 #For use with value boosting policies. Multipliers are multiplicative.
            if mc.business.m_div.uniform and male_focused_marketing_policy in mc.business.active_policies:
                #If there is a uniform and we have the policy to increase value based on that we change the multilier.
                sluttiness_multiplier = (mc.business.m_div.uniform.slut_requirement/100.0) + 1
                serum_value_multiplier = serum_value_multiplier * (sluttiness_multiplier)

            serum_sale_count = __builtin__.round(((3*cha) + (focus) + (2*skill) + 10) * (self.team_effectiveness))/100 #Total number of doses of serum that can be sold by this person.
            sorted_by_value = sorted(self.sale_inventory.serums_held, key = lambda serum: serum[0].value) #List of tuples [SerumDesign, count], sorted by the value of each design. Used so most valuable serums are sold first.
            if self.sale_inventory.get_any_serum_count() < serum_sale_count:
                serum_sale_count = self.sale_inventory.get_any_serum_count()

            if serum_sale_count > 0: #ie. we have serum in our inventory to sell, and the capability to sell them.
                for serum in sorted_by_value:
                    if serum_sale_count <= serum[1]:
                        #There are enough to satisfy order. Remove, add value to wallet, and break
                        value_sold = serum_sale_count * serum[0].value * serum_value_multiplier
                        self.funds += value_sold
                        self.sales_made += value_sold
                        self.sale_inventory.change_serum(serum[0],-serum_sale_count)
                        serum_sale_count = 0
                        break
                    else:
                        #There are not enough in this single order, remove _all_ of them, add value, go onto next thing.
                        serum_sale_count += -serum[1] #We were able to sell this number of serum.
                        value_sold = serum[1] * serum[0].value * serum_value_multiplier
                        self.funds += value_sold
                        self.sales_made += value_sold
                        self.sale_inventory.change_serum(serum[0],-serum[1]) #Should set serum count to 0.
                        #Don't break, we haven't used up all of the serum count


        def production_progress(self,focus,int,skill):
            production_amount = __builtin__.round(((3*focus) + (int) + (2*skill) + 10) * (self.team_effectiveness))/100
            self.production_potential += production_amount
            if production_amount > self.supply_count:
                production_amount = self.supply_count
            self.production_used += production_amount

            if self.serum_production_target != None:
                self.supply_count += -production_amount
                ##Check how many serum can be made, make them and add them to your inventory.
                self.production_points += production_amount
                serum_count = self.production_points//self.serum_production_target.production_cost
                if serum_count > 0:
                    self.add_counted_message("Produced " + self.serum_production_target.name,serum_count)
#                    self.message_list.append(["Produced " + self.serum_production_target.name + " x " + str(serum_count)])
                    self.production_points += -(serum_count * self.serum_production_target.production_cost)
                    if self.serum_production_target is not None and self.auto_sell_threshold is not None and self.inventory.get_serum_count(self.serum_production_target)+serum_count > self.auto_sell_threshold: #If there is a limit set, and the production takes us above the limit, sell extra
                        the_difference = (self.inventory.get_serum_count(self.serum_production_target) + serum_count) - self.auto_sell_threshold #Get the count of serum we can still add to the business inventory. ie set us to the limit.
                        self.inventory.change_serum(self.serum_production_target,serum_count-the_difference)
                        self.sale_inventory.change_serum(self.serum_production_target,the_difference)
                    else:
                        self.inventory.change_serum(self.serum_production_target,serum_count)

        def change_production(self,new_serum):
            self.serum_production_target = new_serum
            self.auto_sell_threshold = None
            self.production_points = 0

        def player_production(self):
            self.production_progress(mc.focus,mc.int,mc.production_skill)

        def player_hr(self):
            self.hr_progress(mc.charisma,mc.int,mc.hr_skill)

        def hr_progress(self,cha,int,skill): #Don't compute efficency cap here so that player HR effort will be applied against any efficency drop even though it's run before the rest of the end of the turn.
            self.team_effectiveness += (3*cha) + (int) + (2*skill) + 10

        def add_employee(self, new_person, division, to_room_as_well=True):
            division.people.append(new_person)
            new_person.job = division.employment_title
            if to_room_as_well:
                division.room.people.append(new_person)

        def remove_employee(self, the_person):
            for div in self.division:
                if the_person in div.people:
                    div.people.remove(the_person)
                    if the_person in div.room.people:
                        div.room.people.remove(the_person)
                    break

        def get_employee_list(self):
            return [people for div in self.division for people in div.people]

        def get_employee_count(self):
            return sum([len(div.people) for div in self.division])

        def get_max_employee_slut(self):
            max = -1 #Set to -1 for an empty business, all calls should require at least sluttiness 0
            for person in self.get_employee_list():
                if person.sluttiness > max:
                    max = person.sluttiness
            return max

        def get_employee_title(self, the_person):
            for div in self.division:
                if the_person in div.people:
                    return div.employment_title
            return "None"

        def get_employee_workstation(self, the_person): #Returns the location a girl should be working at, or "None" if the girl does not work for you
            for div in self.division:
                if the_person in div.people:
                    return div.room
            return None

        def give_daily_serum(self):
            for div in self.division:
                the_message = div.give_daily_serum(self.inventory)
                if the_message:
                    self.message_list.append(the_message)

        def purchase_policy(self, policy):
            self.funds -= policy.cost
            self.available_policies.remove(policy)
            self.active_policies.add(policy)

        def get_max_outfits_to_change(self):

            if maximal_arousal_uniform_policy in self.active_policies:
                return 999 #ie. no limit at all.
            elif corporate_enforced_nudity_policy in self.active_policies:
                return 80
            elif minimal_coverage_uniform_policy in self.active_policies:
                return 60
            elif reduced_coverage_uniform_policy in self.active_policies:
                return 40
            elif casual_uniform_policy in self.active_policies:
                return 25
            elif relaxed_uniform_policy in self.active_policies:
                return 15
            elif strict_uniform_policy in self.active_policies:
                return 5
            else:
                return 0


