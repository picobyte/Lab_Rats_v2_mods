
#How the new position code is set up:
#Each clothing set now has a dictionary of images. The only one that is required is "standing", which is used when you are talking to the person most of the time.
#Each position has a "position_tag". When you start having sex with someone the draw_person code will check it's dictionaryto see if it has a position_tag entry. If yes, it uses that set.
#Otherwise, it uses the default standing images. Right now, this should have changed absolutely nothing about the way the game works.

init -2 python:
    
    import copy
    import math
    import __builtin__
    import pygame
    import re
#    import shader
    
    config.image_cache_size = 12    
    config.layers.insert(1,"Active") ## The "Active" layer is used to display the girls images when you talk to them. The next two lines signal it is to be hidden when you bring up the menu and when you change contexts (like calling a screen)
    config.menu_clear_layers.append("Active")
    config.context_clear_layers.append("Active")
    
    preferences.gl_tearing = True ## Prevents juttery animation with text while using advanced shaders to display images
    pygame.scrap.init()

    def screen_link(r):
        def clicked():
            renpy.exports.launch_editor([r[0]], r[1], transient=1)

        return clicked

    def cursor_pos(st, at):
        return Text("{color=#222}{size=-8}(%d, %d){/size}{/color}"%renpy.get_mouse_pos()), .1

    def copy_cursor_pos():
        pygame.scrap.put(pygame.SCRAP_TEXT, "%d, %d"%renpy.get_mouse_pos())

    class Business(renpy.store.object):
        # main jobs to start with:
        # 1) buying raw supplies.
        # 2) researching new serums.
        # 2a) The player (only) designs new serums to be researched.
        # 3) working in the lab to produce serums.
        # 4) Working in marketing. Increases volumn you can sell, and max price you can sell for.
        # 5) Packaging and selling serums that have been produced.
        # 6) General secretary work. Starts at none needed, grows as your company does (requires an "HR", eventually). Maybe a general % effectivness rating.
        def __init__(self, name, m_div, p_div, r_div, s_div, h_div):
            self.name = name 
            self.funds = 1000 #Your starting wealth.
            
            self.bankrupt_days = 0 #How many days you've been bankrupt. If it hits the max value you lose.
            self.max_bankrupt_days = 3 #How many days you can be negative without loosing the game. Can be increased through research.
            
            self.m_div = m_div #The phsyical locations of all of the teams, so you can move to different offices in the future.
            self.p_div = p_div
            self.r_div = r_div
            self.s_div = s_div
            self.h_div = h_div
            
            self.m_uniform = None #These are the uniforms used by the various departments. If a girl is employed and currently at work she will be wearing her uniform
            self.p_uniform = None
            self.r_uniform = None
            self.s_uniform = None
            self.h_uniform = None
            
            self.m_serum = None #These are the serums given to the different departments if the daily serum dosage policy is researched.
            self.p_serum = None
            self.r_serum = None
            self.s_serum = None
            self.h_serum = None
            
            self.research_team = [] #Researches new serums that the player designs, does theoretical research into future designs, or improves old serums slightly over time
            self.market_team = [] # Increases company marketability. Raises max price serum can be sold for, and max volumn that can be sold.
            self.supply_team = [] # Buys the raw supplies used by the other departments.
            self.production_team = [] # Physically makes the serum and sends it off to be sold.
            self.hr_team = [] # Manages everyone else and improves effectiveness. Needed as company grows.
            
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
            
            self.policy_list = [] #This is a list of Policy objects.
            
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
            for person in self.supply_team + self.research_team + self.production_team + self.market_team:
                if person in self.s_div.people + self.r_div.people + self.p_div.people + self.m_div.people: #Only people in the office lower effectiveness, no loss on weekends, not in for the day, etc.
                    self.team_effectiveness += -1 #TODO: Make this dependant on charisma (High charisma have a lower impact on effectiveness) and happiness.
                
            #Compute effiency rise from HR
            for person in self.hr_team:
                if person in self.h_div.people:
                    self.hr_progress(person.charisma,person.int,person.hr_skill)
                
            if self.team_effectiveness < 50:
                self.team_effectiveness = 50
                
            if self.team_effectiveness > self.effectiveness_cap:
                self.team_effectiveness = self.effectiveness_cap
            
            #Compute other deparement effects
            for person in self.supply_team:
                if person in self.s_div.people: #Check to see if the person is in the room, otherwise don't count their progress (they are at home, dragged away by PC, weekend, etc.)
                    self.supply_purchase(person.focus,person.charisma,person.supply_skill)
            
            for person in self.research_team:
                if person in self.r_div.people:
                    self.research_progress(person.int,person.focus,person.research_skill)
                
            for person in self.production_team:
                if person in self.p_div.people:
                    self.production_progress(person.focus,person.int,person.production_skill)
            
            for person in self.market_team:
                if person in self.m_div.people:
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
            if title == "Marketing":
                return self.m_uniform
            elif title == "Researcher":
                return self.r_uniform
            elif title == "Production":
                return self.p_uniform
            elif title == "Supply":
                return self.s_uniform
            elif title == "Human Resources":
                return self.h_uniform
            else:
                return None
            
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
            for person in self.supply_team + self.research_team + self.production_team + self.market_team + self.hr_team:
                daily_cost += person.salary
            return daily_cost
            
        def add_serum_design(self,the_serum):
            self.serum_designs.append(the_serum)
            
        def set_serum_research(self,new_research):
            self.active_research_design = new_research
            
        def research_progress(self,int,focus,skill):
            research_amount = __builtin__.round(((3*int) + (focus) + (2*skill) + 10) * (self.team_effectiveness))/100
            self.research_produced += research_amount
            if not self.active_research_design == None:
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
            if mc.business.m_uniform and male_focused_marketing_policy.is_owned(): #If there is a uniform and we have the policy to increase value based on that we change the multilier.
                sluttiness_multiplier = (mc.business.m_uniform.slut_requirement/100.0) + 1
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
                
            if not self.serum_production_target == None:
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
                
        def add_employee_research(self, new_person):
            self.research_team.append(new_person)
            new_person.job = self.get_employee_title(new_person)
            
        def add_employee_production(self, new_person):
            self.production_team.append(new_person)
            new_person.job = self.get_employee_title(new_person)
            
        def add_employee_supply(self, new_person):
            self.supply_team.append(new_person)
            new_person.job = self.get_employee_title(new_person)
            
        def add_employee_marketing(self, new_person):
            self.market_team.append(new_person)
            new_person.job = self.get_employee_title(new_person)
            
        def add_employee_hr(self, new_person):
            self.hr_team.append(new_person)
            new_person.job = self.get_employee_title(new_person)
            
        def remove_employee(self, the_person):
            if the_person in self.research_team:
                self.research_team.remove(the_person)
            elif the_person in self.production_team:
                self.production_team.remove(the_person)
            elif the_person in self.supply_team:
                self.supply_team.remove(the_person)
            elif the_person in self.market_team:
                self.market_team.remove(the_person)
            elif the_person in self.hr_team:
                self.hr_team.remove(the_person)
        
        def get_employee_list(self):
            return self.research_team + self.production_team + self.supply_team + self.market_team + self.hr_team
        
        def get_employee_count(self):
            return len(self.get_employee_list())
            
        def get_max_employee_slut(self):
            max = -1 #Set to -1 for an empty business, all calls should require at least sluttiness 0
            for person in self.get_employee_list():
                if person.sluttiness > max:
                    max = person.sluttiness
            return max
            
        def get_employee_title(self, the_person):
            if the_person in self.research_team:
                return "Researcher"
                
            elif the_person in self.market_team:
                return "Marketing"
                
            elif the_person in self.supply_team:
                return "Supply"
                
            elif the_person in self.production_team:
                return "Production"
                
            elif the_person in self.hr_team:
                return "Human Resources"
            else:
                return "None"
                
        def get_employee_workstation(self, the_person): #Returns the location a girl should be working at, or "None" if the girl does not work for you
            if the_person in self.research_team:
                return self.r_div
                
            elif the_person in self.market_team:
                return self.m_div
                
            elif the_person in self.supply_team:
                return self.s_div
                
            elif the_person in self.production_team:
                return self.p_div
                
            elif the_person in self.hr_team:
                return self.h_div
            else:
                return None
                
        def give_daily_serum(self):
            if self.r_serum:
                the_serum = self.r_serum
                for person in self.research_team:
                    if self.inventory.get_serum_count(the_serum) > 0:
                        self.inventory.change_serum(the_serum,-1)
                        person.give_serum(copy.copy(the_serum)) #use a copy rather than the main class, so we can modify and delete the effects without changing anything else.
                    else:
                        the_message = "Stockpile ran out of [the_serum.name] to give to the research division."
                        if not the_message in self.message_list:
                            self.message_list.append(the_message)
                        
            if self.m_serum:
                the_serum = self.m_serum
                for person in self.market_team:
                    if self.inventory.get_serum_count(the_serum) > 0:
                        self.inventory.change_serum(the_serum,-1)
                        person.give_serum(copy.copy(the_serum)) #use a copy rather than the main class, so we can modify and delete the effects without changing anything else.
                    else:
                        the_message = "Stockpile ran out of [the_serum.name] to give to the marketing division."
                        if not the_message in self.message_list:
                            self.message_list.append(the_message)
                        
            if self.p_serum:
                the_serum = self.p_serum
                for person in self.production_team:
                    if self.inventory.get_serum_count(the_serum) > 0:
                        self.inventory.change_serum(the_serum,-1)
                        person.give_serum(copy.copy(the_serum)) #use a copy rather than the main class, so we can modify and delete the effects without changing anything else.
                    else:
                        the_message = "Stockpile ran out of [the_serum.name] to give to the production division."
                        if not the_message in self.message_list:
                            self.message_list.append(the_message)
                        
            if self.s_serum:
                the_serum = self.s_serum
                for person in self.supply_team:
                    if self.inventory.get_serum_count(the_serum) > 0:
                        self.inventory.change_serum(the_serum,-1)
                        person.give_serum(copy.copy(the_serum)) #use a copy rather than the main class, so we can modify and delete the effects without changing anything else.
                    else:
                        the_message = "Stockpile ran out of [the_serum.name] to give to the supply procurement division."
                        if not the_message in self.message_list:
                            self.message_list.append(the_message)
                        
            if self.h_serum:
                the_serum = self.h_serum
                for person in self.hr_team:
                    if self.inventory.get_serum_count(the_serum) > 0:
                        self.inventory.change_serum(the_serum,-1)
                        person.give_serum(copy.copy(the_serum)) #use a copy rather than the main class, so we can modify and delete the effects without changing anything else.
                    else:
                        the_message = "Stockpile ran out of [the_serum.name] to give to the human resources division."
                        if not the_message in self.message_list:
                            self.message_list.append(the_message)
            
    class SerumDesign(renpy.store.object):
        def __init__(self):
            self.name = ""
            self.traits = []
            
            self.researched = False
            self.obsolete = False #TODO: serums can be marked as obsolete so they do not show up on menus in the future.
            self.current_research = 0
            self.research_needed = 50 #Default for a serum with no special effects. "Grey" serum.
            
            self.value = 10 #Value in $ for each dose when sold.
            self.production_cost = 10 #Amount of production points that must be produced to manufacture the serum.
            
            self.duration = 1 #Number of segments the serum lasts for. Night counts as 3 segments. Default is 1.
            self.duration_counter = 0 #How many segments have we been on for so far.
            
            self.suggest_raise = 10 #Raises sugestability of the girl for the duration.
            self.happiness_raise = 0 #Changes happinesss for the duration.
            self.slut_raise = 0 #Changes slut for the duration.
            self.obedience_raise = 0 #changes obedience for the duration.
            
            self.cha_raise = 0 #raises cha for the duration
            self.int_raise = 0
            self.foc_raise = 0
            
            self.status_effects = [] #This array will hold pointers to Status_Effect objects, whose functions are called each cycle of the serum.
            
        def reset(self): #Resets the serum to the default serum values.
            self.__init__()
        
        def apply_serum(self, the_target): #Applies all of the effects of the serum to the target. Called when it is first given to them.
            the_target.change_suggest(self.suggest_raise)
            the_target.change_happiness(self.happiness_raise)
            the_target.change_slut(self.slut_raise)
            the_target.change_obedience(self.obedience_raise)
            
            the_target.change_cha(self.cha_raise)
            the_target.change_int(self.int_raise)
            the_target.change_focus(self.foc_raise)
            
            the_target.add_status_effects(self.status_effects) #Hand them a list of effects
            
            show_array = []
            style_array = []
            if self.suggest_raise > 0:
                show_array.append("+" + str(self.suggest_raise) + " Suggestability\n")
                style_array.append("float_text_blue")
            elif self.suggest_raise < 0:
                show_string.append("-" + str(self.suggest_raise) + " Suggestability\n")
                style_array.append("float_text_blue")
            
            if self.happiness_raise > 0:
                show_array.append("+" + str(self.happiness_raise) + " Happiness\n")
                style_array.append("float_text_blue")
            elif self.suggest_raise < 0:
                show_string.append("-" + str(self.happiness_raise) + " Happiness\n")
                style_array.append("float_text_blue")
                
            if self.slut_raise > 0:
                show_array.append("+" + str(self.slut_raise) + " Sluttiness\n")
                style_array.append("float_text_blue")
            elif self.slut_raise < 0:
                show_string.append("-" + str(self.slut_raise) + " Sluttiness\n")
                style_array.append("float_text_blue")
                
            if self.obedience_raise > 0:
                show_array.append("+" + str(self.obedience_raise) + " Obedience\n")
                style_array.append("float_text_blue")
            elif self.obedience_raise < 0:
                show_string.append("-" + str(self.obedience_raise) + " Obedience\n")
                style_array.append("float_text_blue")
                
            if self.cha_raise > 0:
                show_array.append("+" + str(self.cha_raise) + " Charisma\n")
                style_array.append("float_text_blue")
            elif self.cha_raise < 0:
                show_array.append("-" + str(self.cha_raise) + " Charisma\n")
                style_array.append("float_text_blue")
                
            if self.int_raise > 0:
                show_array.append("+" + str(self.int_raise) + " Intelligence\n")
                style_array.append("float_text_blue")
            elif self.int_raise < 0:
                show_array.append("-" + str(self.int_raise) + " Intelligence\n")
                style_array.append("float_text_blue")
                
            if self.foc_raise > 0:
                show_array.append("+" + str(self.foc_raise) + " Focus\n")
                style_array.append("float_text_blue")
            elif self.foc_raise < 0:
                show_array.append("-" + str(self.foc_raise) + " Focus\n")
                style_array.append("float_text_blue")
                
            for effect in self.status_effects:
                show_array.append("+ " + str(effect.name))
                style_array.append("float_text_blue")
            
            renpy.show_screen("float_up_screen",show_array,style_array)
            
        def remove_serum(self, the_target): #Removes all of the effects of the serum from the target. Called when the serum expires.
            the_target.change_suggest(-self.suggest_raise)
            the_target.change_happiness(-self.happiness_raise)
            the_target.change_slut(-self.slut_raise)
            the_target.change_obedience(-self.obedience_raise)
            
            the_target.change_cha(-self.cha_raise)
            the_target.change_int(-self.int_raise)
            the_target.change_focus(-self.foc_raise)
            
            the_target.remove_status_effects(self.status_effects) #Remove the list of effects we gave them before.
            
        def increment_time(self,amount): #Increases the counter, removes effects if duration is over.
            self.duration_counter += amount
            if self.duration_counter >= self.duration:
                return True #Returns true when it has expired
            else:
                return False #Returns false when there is more time to go
                
        def add_research(self, amount): #Returns true if "amount" research completes the research
            self.current_research += amount
            if self.current_research >= self.research_needed:
                self.researched = True
                return True
            else:
                return False
                
        def set_traits(self,traits_list): #Called when a design is finalized. No calculations are performed with this list, but they can be used as a record for what went into this serum.
            self.traits = traits_list
            
    class SerumInventory(renpy.store.object): #A bag class that lets businesses and people hold onto different types of serums, and move them around.
        def __init__(self,starting_list):
            self.serums_held = starting_list ##Starting list is a list of tuples, going [SerumDesign,count]. Count should be possitive.
            
        def get_serum_count(self, serum_design):
            for design in self.serums_held:
                if design[0] == serum_design:
                    return design[1]
            return 0
            
        def get_any_serum_count(self):
            count = 0
            for design in self.serums_held:
                count += design[1]
            return count
            
        def change_serum(self, serum_design,change_amount): ##Serum count must be greater than 0. Adds to stockpile of serum_design if it is already there, creates it otherwise.
            found = False
            for design in self.serums_held:
                if design[0] == serum_design and not found:
                    design[1] += int(change_amount)
                    found = True
                    if design[1] <= 0:
                        self.serums_held.remove(design)
                        
            if not found:
                if change_amount > 0:
                    self.serums_held.append([serum_design,int(change_amount)])
                    
                    
        def get_serum_type_list(self): ## returns a list of all the serum types that are in the inventory, without their counts.
            return_values = []
            for design in self.serums_held:
                return_values.append(design[0])
            return return_values
            
                
    class SerumTrait(renpy.store.object):
        def __init__(self,name,desc,effect,status_effects=[],requires=[],start_researched=False,research_needed=0): #effect is a function that takes a serumDesign as a parameter and modifies it based on whatever effect this trait has.
            self.name = name
            self.desc = desc
            self.effect = effect #A list of default effects to be applied.
            self.status_effects = status_effects #A list of Status_Effect objects that are applied by this serum to a person, with a function to be called each tick.
            self.requires = requires #A list of other traits that must be researched before this. TODO: Impliment theoretical research.
            self.researched = start_researched
            self.research_needed = research_needed
            self.current_research = 0
            
        def total_effect(self,design):
            self.effect(design)
            
        def add_research(self, amount):
            self.current_research += amount
            if self.current_research >= self.research_needed:
                self.researched = True
                return True
            else:
                return False
                
        def has_required(self):
            has_prereqs = True
            for trait in self.requires:
                if not trait.researched:
                    has_prereqs = False
            return has_prereqs
    
    class MainCharacter(renpy.store.object):
        def __init__(self, location, name, business, stat_array, skill_array, sex_array):
            self.location = location
            self.name = name
            self.energy = 50
            self.designed_wardrobe = Wardrobe("Designed Wardrobe", [])
            self.money = 100 ## Personal money that can be spent however you wish. Company funds are seperate (but can be manipulated in your favour)
            self.business = business
            self.inventory = SerumInventory([])
            
            ##Mental stats##
            #Mental stats are generally fixed and cannot be changed permanently.
            self.charisma = stat_array[0]#How likeable the person is. Mainly influences marketing, also determines how well interactions with other characters go. Main stat for HR and sales
            self.int = stat_array[1] #How smart the person is. Mainly influences research, small bonuses to most tasks. #Main stat for research and production.
            self.focus = stat_array[2]#How on task the person stays. Influences most tasks slightly. #Main stat for supplies
            
            ##Work Skills##
            #Skills can be trained up over time, but are limited by your raw stats.
            self.hr_skill = skill_array[0]
            self.market_skill = skill_array[1]
            self.research_skill = skill_array[2]
            self.production_skill = skill_array[3]
            self.supply_skill = skill_array[4]
            
            ##Sex Stats##
            # These are phyical stats about the character that impact how they behave in a sex scene. Future values might include penis size or sensitivity.
            self.arousal = 0 #How close to an orgasm you are. You are forced to cum when you reach 100, after which it generally resets to 0.
            
            ##Sex Skills##
            # These skill represent your knowledge and experience with different types of intimacy. Useful for raising a girls arousal faster than your own.
            self.sex_skills = {}
            self.sex_skills["Foreplay"] = sex_array[0] # A catch all for everything that goes on before blowjobs, sex, etc. Includes things like kissing, massages, etc.
            self.sex_skills["Oral"] = sex_array[1] # Your skill at eating a girl out.
            self.sex_skills["Vaginal"] = sex_array[2] # Your skill at different positions that involve vaginal sex.
            self.sex_skills["Anal"] = sex_array[3] # Your skill skill at different positions that involve anal sex.
            
        def change_location(self,new_location):
            self.location = new_location
            
        def use_energy(self,amount):
            self.energy = self.energy - amount
            if self.energy < 0:
                self.energy = 0
                
        def save_design(self,the_outfit,new_name):
            the_outfit.name = new_name
            self.designed_wardrobe.add_outfit(the_outfit)
            
        def change_arousal(self,amount):
            self.arousal += amount
            if self.arousal < 0:
                self.arousal = 0
                
        def reset_arousal(self):
            self.arousal = 0
            
        def is_at_work(self): #Checks to see if the main character is at work, generally used in crisis checks.
            if self.location == self.business.m_div or self.location == self.business.p_div or self.location == self.business.r_div or self.location == self.business.s_div or self.location == self.business.h_div:
                return True
            else:
                return False
                
                
    class Person(renpy.store.object): #Everything that needs to be known about a person.
        def __init__(self,name,last_name,age,body_type,tits,height,body_images,expression_images,hair_colour,hair_style,skin,eyes,job,wardrobe,personality,stat_list,skill_list,sluttiness=0,obedience=0,suggest=0,sex_list=[0,0,0,0]):
            ## Personality stuff, name, ect. Non-physical stuff.
            #TODO: Add ability to "discover" this stuff, you don't know it by default.
            self.name = name
            self.last_name = last_name
            self.job = job
            self.personality = personality
            #TODO: Have a "home" variable that tells people where to go at night
            #TODO: Relationship with other people (List of known people plus relationship with them.)
            
            #TODO: Integrate this with the rest of the game, so you can have different fonts for different characters, different colours, etc.
            self.char_object = Character(name,what_font="Avara.ttf") #We use this to customize the font in the dialogue boxes
            
            ## Physical things.
            self.age = age
            self.body_type = body_type
            self.tits = tits
            self.height = height #This is the scale factor for height, with the talest girl being 1.0 and the shortest being 0.8
            self.body_images = body_images #instance of Clothing class, which uses full body shots.
            self.expression_images = expression_images #instance of the Expression class, which stores facial expressions for different skin colours
            self.hair_colour = hair_colour
            self.hair_style = hair_style
            self.skin = skin
            self.eyes = eyes
            #TODO: Tattoos eventually
            
            self.serum_effects = [] #A list of all of the serums we are under the effect of.
            self.status_effects = [] #A list of functions that should be called each time chunk, usually given as the result of a serum.
            
            ##Mental stats##
            #Mental stats are generally fixed and cannot be changed permanently. Ranges from 1 to 5 at start, can go up or down (min 0)
            self.charisma = stat_list[0] #How likeable the person is. Mainly influences marketing, also determines how well interactions with other characters go. Main stat for HR and sales
            self.int = stat_list[1] #How smart the person is. Mainly influences research, small bonuses to most tasks. #Main stat for research and production.
            self.focus = stat_list[2] #How on task the person stays. Influences most tasks slightly. #Main stat for supplies
            
            ##Work Skills##
            #Skills can be trained up over time, but are limited by your raw stats. Ranges from 1 to 5 at start, can go up or down (min 0)
            self.hr_skill = skill_list[0]
            self.market_skill = skill_list[1]
            self.research_skill = skill_list[2]
            self.production_skill = skill_list[3]
            self.supply_skill = skill_list[4]
            
            self.salary = self.calculate_base_salary()
            
            if renpy.random.randint(0,1) == 0:
                self.idle_pose = "stand3"
            else:
                self.idle_pose = "stand2"
            
            ##Personality Stats##
            #Things like sugestability, that change over the course of the game when the player interacts with the girl
            self.suggestibility = 0 + suggest #How much events will influnce this girls stats. 100 means full possible effect, 0 means no long term effect.
            self.happiness = 100 #100 is default max, higher is better.
            self.sluttiness = 0 + sluttiness #How slutty the girl is by default. Higher will have her doing more things just because she wants to or you asked.
            self.obedience = 100 + obedience #How likely the girl is to listen to commands. Default is 100 (normal person), lower actively resists commands, higher follows them.
            
            ##Sex Stats##
            #These are physical stats about the girl that impact how she behaves in a sex scene. Future values might include things like breast sensitivity, pussy tighness, etc.
            self.arousal = 0 #How actively horny a girl is, and how close she is to orgasm. Generally resets to 0 after orgasming, and decreases over time while not having sex (or having bad sex).
            
            ##Sex Skills##
            #These represent how skilled a girl is at different kinds of intimacy, ranging from kissing to anal. The higher the skill the closer she'll be able to bring you to orgasm (whether you like it or not!)
            self.sex_skills = {}
            self.sex_skills["Foreplay"] = sex_list[0] #A catch all for everything that goes on before blowjobs, sex, etc. Includes things like kissing and strip teases.
            self.sex_skills["Oral"] = sex_list[1] #The girls skill at giving head.
            self.sex_skills["Vaginal"] = sex_list[2] #The girls skill at different positions that involve vaginal sex.
            self.sex_skills["Anal"] = sex_list[3] #The girls skill at different positions that involve anal sex.
            
            ## Clothing things.
            self.wardrobe = copy.copy(wardrobe)
            self.wardrobe.trim_wardrobe(self.sluttiness)
            self.outfit = self.wardrobe.pick_random_outfit()
            
        def run_turn(self):
            for effect in set(self.status_effects): #Compute the effects of all of the status effects we are under. Duplicates are not repeated! They are kept in place for overlapping effects.
                effect.function(self)
                
            remove_list = []
            for serum in self.serum_effects: #Compute the effects of all of the serum that the girl is under.
                if serum.increment_time(1): #Returns true if the serum effect is suppose to expire in this time, otherwise returns false. Always updates duration counter when called.
                    serum.remove_serum(self)
                    remove_list.append(serum) #Use a holder "remove" list to avoid modifying list while iterating.
                    
            for serum in remove_list:
                self.serum_effects.remove(serum)
                    
            #Now we want to see if she's unhappy enough to quit. We will tally her "happy points", a negative number means a chance to quit.
            
            if mc.business.get_employee_workstation(self) is not None: #Only let people who work for us quit their job.
                happy_points = self.get_job_happiness_score()
                if happy_points < 0: #We have a chance of quitting.
                    chance_to_quit = happy_points * -2 #there is a %2*unhappiness chance that the girl will quit.
                    if renpy.random.randint(0,100) < chance_to_quit: #She is quitting
                        potential_quit_action = Action(self.name + " is quitting.", quiting_crisis_requirement, "quitting_crisis_label", self)
                        if potential_quit_action not in mc.business.mandatory_crises_list:
                            mc.business.mandatory_crises_list.append(potential_quit_action)
                    
                    else: #She's not quitting, but we'll let the player know she's unhappy TODO: Only present this message with a certain research/policy.
                        warning_message = self.name + " " + self.last_name + " (" +mc.business.get_employee_title(self) + ") " + " is unhappy with her job and is considering quitting."
                        if warning_message not in mc.business.message_list:
                            mc.business.message_list.append(warning_message)
        
        def run_move(self,location): #Move to the apporpriate place for the current time unit, ie. where the player should find us.
              
            #Move the girl the appropriate location on the map. For now this is either a division at work (chunks 1,2,3) or downtown (chunks 0,5). TODO: add personal homes to all girls that you know above a certain amount.
            
            if time_of_day == 0 or time_of_day == 4: #Home time
                location.move_person(self, downtown) #Move to downtown as proxy for home.
            else:
                work_destination = mc.business.get_employee_workstation(self)
                
                if work_destination is not None: #She works for us, move her to her work station,
                    location.move_person(self, work_destination)
                    if self.should_wear_uniform():
                        self.wear_uniform()
                else: #She does not work for us, scatter her somewhere public on the map.
                    available_locations = [] #Check to see where is public (or where you are white listed) and move to one of those locations randomly
                    for potential_location in list_of_places:
                        if potential_location.public:
                            available_locations.append(potential_location)
                    location.move_person(self, get_random_from_list(available_locations))
                    
                
        def run_day(self): #Called at the end of the day. 
            self.outfit = self.wardrobe.pick_random_outfit() #Put on a new outfit for the day!
            remove_list = []
            for serum in self.serum_effects:
                if serum.increment_time(2): #Night is 3 segments, but 1 is allready called when run_turn is called.
                    serum.remove_serum(self)
                    remove_list.append(serum)
            
            for serum in remove_list:
                self.serum_effects.remove(serum)
            
        def draw_person(self,position = None,emotion = None): #Draw the person, standing as default if they aren't standing in any other position.
            renpy.scene("Active")
            if position is None:
                position = self.idle_pose
            #self.hair_style.draw_hair_back(self.hair_colour,self.height) #NOTE: Not currently used to see if it's actually needed.
            self.body_images.draw_item(self.body_type,self.height,self.tits,position)
            if emotion is not None:
                self.expression_images.draw_emotion(position,emotion,self.height)
            else:
                self.expression_images.draw_emotion(position,self.get_emotion(),self.height)
            self.outfit.draw_outfit(self.body_type,self.height,self.tits,position)
            self.hair_style.draw_item(self.hair_colour,self.height,position)
            
        def get_emotion(self): # Get the emotion state of a character, used when the persons sprite is drawn and no fixed emotion is required.
            if self.arousal>= 100:
                return "orgasm"
            
            if self.happiness > 100:
                return "happy"
            elif self.happiness < 80:
                return "sad"
            else:
                return "default"
            
        def call_greeting(self):
            self.personality.get_greeting(self)
            
        def call_sex_response(self):
            self.personality.get_sex_response(self)
            
        def call_climax_response(self):
            self.personality.get_climax_response(self)
            
        def call_clothing_accept(self):
            self.personality.get_clothing_accept(self)
            
        def call_clothing_reject(self):
            self.personality.get_clothing_reject(self)
            
        def call_clothing_review(self):
            self.personality.get_clothing_review(self)
            
        def call_strip_reject(self):
            self.personality.get_strip_reject(self)
            
        def call_sex_accept_response(self):
            self.personality.get_sex_accept_response(self)
        
        def call_sex_obedience_accept_response(self):
            self.personality.get_sex_obedience_accept_response(self)
            
        def call_sex_gentle_reject(self):
            self.personality.get_sex_gentle_reject(self)
            
        def call_sex_angry_reject(self):
            self.personality.get_sex_angry_reject(self)
            
        def call_seduction_response(self):
            self.personality.get_seduction_response(self)
            
        def call_flirt_response(self):
            self.personality.get_flirt_response(self)
        
        def call_cum_face(self):
            self.personality.get_cum_face(self)
            
        def call_cum_mouth(self):
            self.personality.get_cum_mouth(self)
            
        def call_suprised_exclaim(self):
            self.personality.get_suprised_exclaim(self)
            
        def add_outfit(self,the_outfit):
            self.wardrobe.add_outfit(the_outfit)
            
        def set_outfit(self,new_outfit):
            self.outfit = new_outfit
            
        def give_serum(self,the_serum_design): ##Make sure you are passing a copy of the serum, not a reference.
            self.serum_effects.append(the_serum_design)
            the_serum_design.apply_serum(self)
        
        def add_status_effects(self,effects):
            for effect in effects:
                self.status_effects.append(effect)
        
        def remove_status_effects(self,effects):
            for effect in effects:
                self.status_effects.remove(effect) #Find the effect and remove it. If it still exists somehwere else then they're still under the effect.
            
    
        def change_suggest(self,amount):
            self.suggestibility += amount
            if self.suggestibility < 0:
                self.suggestibility = 0
                
        def change_happiness(self,amount):
            self.happiness += amount
            if self.happiness < 0:
                self.happiness = 0
                
        def change_slut(self,amount):
            self.sluttiness += amount
            if self.sluttiness < 0:
                self.sluttiness = 0
                
        def change_slut_modified(self,amount): #Changes slut amount, but modified by current suggestibility.
            change_amount = (amount*self.suggestibility)/100
            self.change_slut(change_amount)
            return change_amount
                
        def change_obedience(self,amount):
            self.obedience += amount
            if self.obedience < 0:
                self.obedience = 0
                
        def change_obedience_modified(self,amount):
            change_amount = (amount*self.suggestibility)/100
            self.change_obedience(change_amount)
            return change_amount
                
        def change_cha(self,amount):
            self.charisma += amount
            if self.charisma < 0:
                self.charisma = 0
                
        def change_int(self,amount):
            self.int += amount
            if self.int < 0:
                self.int = 0
                
        def change_focus(self,amount):
            self.focus += amount
            if self.focus < 0:
                self.focus = 0
                
        def review_outfit(self):
            if self.should_wear_uniform():
                self.wear_uniform()#Reset uniform
#                self.call_uniform_review() #TODO: actually impliment this call, but only when her outfit significantly differs from the real uniform.
            
            elif self.outfit.slut_requirement > self.sluttiness:
                self.outfit = self.wardrobe.pick_random_outfit()
                self.call_clothing_review()
                
        def judge_outfit(self,outfit,temp_sluttiness_boost = 0): #Judge an outfit and determine if it's too slutty or not. Can be used to judge other people's outfits to determine if she thinks they look like a slut.
            # temp_sluttiness can be used in situations (mainly crises) where an outfit is allowed to be temporarily more slutty than a girl is comfortable wearing all the time.
            #Returns true if the outfit is wearable, false otherwise
            if outfit.slut_requirement > (the_person.effective_sluttiness() + temp_sluttiness_boost): #Arousal is important for judging potential changes to her outfit while being stripped down during sex.
                return False
            else:
                return True
                
        def should_wear_uniform(self):
            #Check to see if we are: 1) Employed by the PC. 2) At work right now. 3) there is a uniform set for our department.
            employment_title = mc.business.get_employee_title(self)
            if employment_title != "None":
                if mc.business.is_open_for_business(): #We should be at work right now, so if there is a uniform we should wear it.
                    if mc.business.get_uniform(employment_title) is not None:
                        return True
            
            return False #If we fail to meet any of the above conditions we should return false.
            
        def wear_uniform(self): #Puts the girl into her uniform, if it exists.
            the_uniform = mc.business.get_uniform(mc.business.get_employee_title(self)) #Get the uniform for her department.
            self.outfit = copy.deepcopy(the_uniform) #We already know we work for the mc if we should be wearing a uniform. Take a deep copy so strips don't leave us naked.
                
        def get_job_happiness_score(self):
            happy_points = self.happiness - 100 #Happiness over 100 gives a bonus to staying, happiness less than 100 gives a penalty
            happy_points += self.obedience - 100 #A more obedient character is more likely to stay, even if they're unhappy.
            happy_points += self.salary - self.calculate_base_salary() #A real salary greater than her base is a bonus, less is a penalty. TODO: Make this dependent on salary fraction, not abosolute pay.
            return happy_points
                
        def change_arousal(self,amount):
            self.arousal += amount
            if self.arousal < 0:
                self.arousal = 0
                
        def reset_arousal(self):
            self.arousal = 0
            
        def has_large_tits(self): #Returns true if the girl has large breasts. "D" cups and up are considered large enough for titfucking, swinging, etc.
            if self.tits == "D" or self.tits == "DD" or self.tits == "DDD" or self.tits == "E" or self.tits == "F" or self.tits == "FF":
                return True
            else:
                return False
                
        def effective_sluttiness(self): #Used in sex scenes where the girl will be more aroused, making it easier for her to be seduced.
            return self.sluttiness + (self.arousal/2)
            
        def calculate_base_salary(self): #returns the default value this person should be worth on a per day basis.
            return (self.int + self.focus + self.charisma)*2 + (self.hr_skill + self.market_skill + self.research_skill + self.production_skill + self.supply_skill)
                   
    class Personality(renpy.store.object): #How the character responds to various actions
        def __init__(self,type,greeting_label,sex_response_label,climax_response_label,clothing_accept_label, clothing_reject_label, clothing_review_label, strip_reject_label, sex_accept_label, sex_obedience_accept_label, sex_gentle_reject_label, 
            sex_angry_reject_label, seduction_response_label, flirt_response_label, cum_face_label, cum_mouth_label, suprised_exclaim_label): ##TODO: Add more stats when we know what they should be.
            self.type = type
            self.greeting_label = greeting_label
            self.sex_response_label = sex_response_label
            self.climax_response_label = climax_response_label
            self.clothing_accept_label = clothing_accept_label
            self.clothing_reject_label = clothing_reject_label
            self.clothing_review_label = clothing_review_label
            self.strip_reject_label = strip_reject_label
            self.sex_accept_label = sex_accept_label
            self.sex_obedience_accept_label = sex_obedience_accept_label
            self.sex_gentle_reject_label = sex_gentle_reject_label
            self.sex_angry_reject_label = sex_angry_reject_label
            self.seduction_response_label = seduction_response_label
            self.flirt_response_label = flirt_response_label
            self.cum_face_label = cum_face_label
            self.cum_mouth_label = cum_mouth_label
            self.suprised_exclaim_label = suprised_exclaim_label
            
            
        def get_greeting(self, the_person):
            renpy.call(self.greeting_label, the_person)
            
        def get_sex_response(self, the_person):
            renpy.call(self.sex_response_label, the_person)
            
        def get_climax_response(self, the_person):
            renpy.call(self.climax_response_label, the_person)
            
        def get_clothing_accept(self, the_person):
            renpy.call(self.clothing_accept_label, the_person)
            
        def get_clothing_reject(self, the_person):
            renpy.call(self.clothing_reject_label, the_person)
            
        def get_clothing_review(self, the_person):
            renpy.call(self.clothing_review_label, the_person)
            
        def get_strip_reject(self, the_person):
            renpy.call(self.strip_reject_label, the_person)
            
        def get_sex_accept_response(self, the_person):
            renpy.call(self.sex_accept_label, the_person)
        
        def get_sex_obedience_accept_response(self, the_person):
            renpy.call(self.sex_obedience_accept_label, the_person)
            
        def get_sex_gentle_reject(self, the_person):
            renpy.call(self.sex_gentle_reject_label, the_person)
            
        def get_sex_angry_reject(self, the_person):
            renpy.call(self.sex_angry_reject_label, the_person)
            
        def get_seduction_response(self, the_person):
            renpy.call(self.seduction_response_label, the_person)
            
        def get_flirt_response(self, the_person):
            renpy.call(self.flirt_response_label, the_person)
            
        def get_cum_face(self, the_person):
            renpy.call(self.cum_face_label, the_person)
            
        def get_cum_mouth(self, the_person):
            renpy.call(self.cum_mouth_label, the_person)
            
        def get_suprised_exclaim(self, the_person):
            renpy.call(self.suprised_exclaim_label, the_person)
            
    def make_person(): #This will generate a person, using a pregen body some of the time if they are available.
        split_proportion = 20 #1/5 characters generated will be a premade character.
        return_character = None
        if renpy.random.randint(1,100) < split_proportion:
            return_character = get_premade_character()
            
        if return_character is None: #Either we aren't getting a premade, or we are out of them.
            return_character = create_random_person()
        return return_character
            
    # create_random_person is used to generate a Person object from a list of random or provided stats. use "make_a_person" to properly get premade characters mixed with randoms.        
    def create_random_person(name = None, last_name = None, age = None, body_type = None, face_style = None, tits = None, height = None, hair_colour = None, hair_style = None, skin = None, eyes = None, job = None, personality = None):
        if name is None:
            name = get_random_name()
        if last_name is None:
            last_name = get_random_last_name()
        if age is None:
            age = renpy.random.randint(21,50)
        if body_type is None:
            body_type = get_random_body_type()
        if tits is None:
            tits = get_random_tit()
        if height is None:
            height = 0.9 + (renpy.random.random()/10)
        if hair_colour is None:
            hair_colour = get_random_hair_colour()
        if hair_style is None:
            hair_style = get_random_from_list(hair_styles)
        if skin is None:
            skin = get_random_skin()
        if face_style is None:
            face_style = get_random_face()
        if skin == "white":
            body_images = white_skin
        elif skin == "tan":
            body_images = tan_skin
        else:
            body_images = black_skin
            
        emotion_images = Expression(name+"\'s Expression Set", skin, face_style)
        
        if eyes is None:
            eyes = get_random_eye()
        if job is None:
            job = get_random_job()
        if personality is None:
            personality = get_random_personality()
        
        skill_cap = 5
        stat_cap = 5
        
        if recruitment_skill_improvement_policy.is_owned():
            skill_cap += 2
            
        if recruitment_stat_improvement_policy.is_owned():
            stat_cap += 2
        
        skill_array = [renpy.random.randint(1,skill_cap),renpy.random.randint(1,skill_cap),renpy.random.randint(1,skill_cap),renpy.random.randint(1,skill_cap),renpy.random.randint(1,skill_cap)]
        stat_array = [renpy.random.randint(1,stat_cap),renpy.random.randint(1,stat_cap),renpy.random.randint(1,stat_cap)]
        sex_array = [renpy.random.randint(0,5),renpy.random.randint(0,5),renpy.random.randint(0,5),renpy.random.randint(0,5)]
        
        start_suggest = 0
        if recruitment_suggest_improvment_policy.is_owned():
            start_suggest += 10
        
        start_obedience = renpy.random.randint(-10,10)
        if recruitment_obedience_improvement_policy.is_owned():
            start_obedience += 10
        
        start_sluttiness = renpy.random.randint(0,10)
        if recruitment_slut_improvement_policy.is_owned():
            start_sluttiness += 20        
        
        return Person(name,last_name,age,body_type,tits,height,body_images,emotion_images,hair_colour,hair_style,skin,eyes,job,default_wardrobe,personality,stat_array,skill_array,sex_list=sex_array,sluttiness=start_sluttiness,obedience=start_obedience,suggest=start_suggest)
        
    def height_to_string(the_height): #Height is a value between 0.9 and 1.0 which corisponds to 5' 0" and 5' 10"
        rounded_height = __builtin__.round(the_height,2) #Round height to 2 decimal points.
        if rounded_height >= 1.00:
            return "5' 10\""            
        elif rounded_height == 0.99:
            return "5' 9\""            
        elif rounded_height == 0.98:
            return "5' 8\""            
        elif rounded_height == 0.97:
            return "5' 7\""            
        elif rounded_height == 0.96:
            return "5' 6\""            
        elif rounded_height == 0.95:
            return "5' 5\""            
        elif rounded_height == 0.94:
            return "5' 4\""            
        elif rounded_height == 0.93:
            return "5' 3\""            
        elif rounded_height == 0.92:
            return "5' 2\""            
        elif rounded_height == 0.91:
            return "5' 1\""            
        elif rounded_height <= 0.90:
            return "5' 0\""
        else:
            return "Problem, height not found in chart."
            
    class Expression(renpy.store.object):
        def __init__(self,name,skin_colour,facial_style):
            self.name = name
            self.skin_colour = skin_colour
            self.facial_style = facial_style #The style of face the person has, currently creatively named "Face_1", "Face_2", and "Face_3".
            self.emotion_set = ["default","happy","sad","angry","orgasm"]
            self.positions_set = ["stand1","stand2","stand3"] #The set of images we are going to draw emotions for. These are positions that look towards the camera
            self.ignore_position_set = ["doggy"] #The set of positions that we are not goign to draw emotions for. These look away from the camera TODO: This should reference the Position class somehow.
            self.position_dict = {}
            for position in self.positions_set+self.ignore_position_set:
                self.position_dict[position] = {}
                
            for position in self.positions_set:
                for emotion in self.emotion_set:
                    self.position_dict[position][emotion] = Image(emotion + "_" + facial_style + "_" + skin_colour + "_" + position + ".png")
            
            for position in self.ignore_position_set:
                for emotion in self.emotion_set:
                    self.position_dict[position][emotion] = Image("empty_holder.png") ##An empty image to be drawn when we don't want to draw any emotion, because the character's face is turned away.
                
        def draw_emotion(self,position,emotion,height):
            if not position in self.positions_set+self.ignore_position_set:
                position = "stand1"
            if not emotion in self.emotion_set:
                emotion = "default"
            renpy.show(self.name+position+emotion+self.facial_style,at_list=[right,scale_person(height)],layer="Active",what=self.position_dict[position][emotion],tag=self.name+position+emotion)
    
    class Room(renpy.store.object): #Contains people and objects.
        def __init__(self,name,formalName,connections,background_image,objects,people,actions,public,map_pos):
            self.name = name
            self.formalName = formalName
            self.connections = connections
            self.background_image = background_image
            self.objects = objects
            self.people = people       
            self.actions = actions #A list of Action objects
            self.public = public #If True, random people can wander here. TODO: Update rooms to include this value.
            self.map_pos = map_pos #A tuple of two float values from 0.0 to 1.0, used to determine where this should be placed on the map dynamically.
            
        def link_locations(self,other): #This is a one way connection!
            self.connections.append(other)
            
        def link_locations_two_way(self,other): #Link it both ways. Great for adding locations after the fact, when you don't want to modify existing locations.
            self.link_locations(other)
            other.link_locations(self)
            
        def add_object(self,the_object):
            self.objects.append(the_object)  
            
        def add_person(self,the_person):
            self.people.append(the_person)
        
        def remove_person(self,the_person):
            self.people.remove(the_person)
            
        def move_person(self,the_person,the_destination):
            if not the_person in the_destination.people: # Don't bother moving people who are already there.
                self.remove_person(the_person)
                the_destination.add_person(the_person)
            
        def has_person(self,the_person):
            if the_person in self.people:
                return True
            else:
                return False
            
        def objects_with_trait(self,the_trait):
            return_list = []
            for object in self.objects:
                if object.has_trait(the_trait):
                    return_list.append(object)
            return return_list
            
        def has_object_with_trait(self,the_trait):
            if the_trait == "None":
                return True
            for object in self.objects:
                if object.has_trait(the_trait):
                    return True
            return False
            
        def valid_actions(self):
            count = 0
            for act in self.actions:
                if act.check_requirement():
                    count += 1
            return count

    
    class Action(renpy.store.object): #Contains the information about actions that can be taken in a room. Dispayed when you are asked what you want to do somewhere.
        # Also used for crises, those are not related to any partiular room and are not displayed in a list. They are forced upon the player.
        def __init__(self,name,requirement,effect,args=None):
            self.name = name
            self.requirement = requirement #requirement should be a function that has already been defined. Yay functional programming!
            self.effect = effect
            self.args = args #stores any arguments that we want passed to the action or requirement when the action is created. Should be a list of variables.
            
        def __cmp__(self,other): ##This and __hash__ are defined so that I can use "if Action in List" and have it find identical actions that are different instances.
            if type(other) is Action:
                if self.name == other.name and self.requirement == other.requirement and self.effect == other.effect and self.args == other.args:
                    return 0
                else:
                    if self.__hash__() < other.__hash__(): #Use hash values to break ties.
                        return -1
                    else:
                        return 1
            else:
                if self.__hash__() < other.__hash__(): #Use hash values to break ties.
                    return -1
                else:
                    return 1
        
        def __hash__(self):
            return hash((self.name,self.requirement,self.effect,self.args))
            
        def check_requirement(self): #Calls the function that was passed to the action when it was created. Currently can only use global variables, will change later to take arbitrary list.
            return self.requirement()
            
        def call_action(self): #Can only use global variables. args is a list of elements you want to include as arguments. None is default
            if self.args is None:
                renpy.call(self.effect)
            else:
                renpy.call(self.effect,self.args)
            renpy.return_statement()
            
    class Policy(renpy.store.object): # An upgrade that can be purchased by the character for their business.
        def __init__(self,name,desc,requirement,cost):
            self.name = name #A short name for the policy.
            self.desc = desc #A text description of the policy.
            self.requirement = requirement #a function that is run to see if the PC can purchase this policy.
            self.cost = cost #Cost in dollars.
            
        def __cmp__(self,other): #
            if type(other) is Policy:
                if self.name == other.name and self.desc == other.desc and self.cost == other.cost:
                    return 0
                else:
                    if self.__hash__() < other.__hash__(): #Use hash values to break ties.
                        return -1
                    else:
                        return 1
                
            else:
                if self.__hash__() < other.__hash__(): #Use hash values to break ties.
                    return -1
                else:
                    return 1
                    
        def __hash__(self):
            return hash((self.name,self.desc,self.cost))
            
        def is_owned(self):                
            if self in mc.business.policy_list:
                return True
            else:
                return False
        
    class Object(renpy.store.object): #Contains a list of traits for the object which decides how it can be used.
        def __init__(self,name,traits):
            self.traits = traits
            self.name = name
            
        def has_trait(self,the_trait):
            for trait in self.traits:
                if trait == the_trait:
                    return True
            return False
            
    class Hair_Style(renpy.store.object):
        def __init__(self, name, filename):
            self.name = name
            self.filename = filename
            self.black = {"stand1":Image(filename+"_black_stand1.png"),"stand2":Image(filename+"_black_stand2.png"),"stand3":Image(filename+"_black_stand3.png"),"doggy":Image(filename+"_black_doggy.png")}
            self.brown = {"stand1":Image(filename+"_brown_stand1.png"),"stand2":Image(filename+"_brown_stand2.png"),"stand3":Image(filename+"_brown_stand3.png"),"doggy":Image(filename+"_brown_doggy.png")}
            self.blond = {"stand1":Image(filename+"_blond_stand1.png"),"stand2":Image(filename+"_blond_stand2.png"),"stand3":Image(filename+"_blond_stand3.png"),"doggy":Image(filename+"_blond_doggy.png")}
            self.red = {"stand1":Image(filename+"_red_stand1.png"),"stand2":Image(filename+"_red_stand2.png"),"stand3":Image(filename+"_red_stand3.png"),"doggy":Image(filename+"_red_doggy.png")}
            
        def draw_item(self,colour,height,position = "stand1"): #colour = black,brown,blond, or red right now
            if colour == "black":
                image_set = self.black.get(position) #Backup in case a position is missing a correct image set tag.
                if image_set == None:
                    image_set = self.black["stand1"] #Default case is stand 1. TODO: put the default in a global location that everything refers to.
            elif colour == "brown":
                image_set = self.brown.get(position)
                if image_set == None:
                    image_set = self.brown.get["stand1"]
            elif colour == "blond":
                image_set = self.blond.get(position)
                if image_set == None:
                    image_set = self.blond["stand1"]
            else: #colour == "red"
                image_set = self.red.get(position)
                if image_set == None:
                    image_set = self.red["stand1"]
            
            shader_image = ShaderDisplayable(shader.MODE_2D, image_set.filename, shader.VS_2D,PS_COLOUR_SUB_LR2,{},uniforms={"colour_levels":[1,1,1,1]}) #TODO: This should take a colour parameter and colour the hair in game.
            renpy.show(self.name,at_list=[right,scale_person(height)],layer="Active",what=shader_image,tag=self.name) 
                
    class Clothing(renpy.store.object):
        #Slots are
        
        ##Feet##
        #Layer 1: Socks
        #Layer 2: Shoes

        ##Lower Body##
        #Layer 1: Panties
        #Layer 2: Pantyhose
        #Layer 3: Pants/Skirt
        
        ##Upper Body##
        #Layer 1: Bra
        #Layer 2: Shirt
        #Layer 3: Jacket
        
        ##Accessories##
        #TODO
        
        def __init__(self, name, layer, hide_below, anchor_below, proper_name, position_sets, draws_breasts, underwear, slut_value, has_extension = None, is_extension = False, colour = None): 
            self.name = name
            self.hide_below = hide_below #If true, it hides the clothing beneath so you can't tell what's on.
            self.anchor_below = anchor_below #If true, you must take this off before you can take off anything of a lower layer.
            self.layer = layer #A list of the slots above that this should take up or otherwise prevent from being filled. Slots are a list of the slot and the layer.
            self.position_sets = {} #A list of position set names. When the clothing is created it will make a dict containing these names and image sets for them.
            for set in position_sets:
                self.position_sets[set] = Clothing_Images(proper_name,set,draws_breasts)
            self.draws_breasts = draws_breasts
            self.underwear = underwear #True if the item of clothing satisfies the desire for underwear for upper or lower (bra or panties), false if it can pass as outerwear. Underwear on outside of outfit gives higher slut requirement.
            self.slut_value = slut_value #The amount of sluttiness that this piece of clothing adds to an outfit.
            self.has_extension = has_extension #If the item of clothing spans two zones (say, lower and feet or upper and lower body) has_extension points towards the placeholder item that fills the other part.
            self.is_extension = is_extension #If this is true the clothing item exists only as a placeholder. It will draw nothing and not be removed unless the main piece is removed.
            if not colour:
                self.colour = [1,1,1,1]
            else:
                self.colour = colour
                
        def __cmp__(self,other):
            if type(self) is type(other):
                if self.name == other.name and self.hide_below == other.hide_below and self.layer == other.layer:
                    return 0
                    
            if self.__hash__() < other.__hash__():
                return -1
            else:
                return 1
                    
        def __hash__(self):
            return hash((self.name,self.hide_below,self.anchor_below,self.layer,self.draws_breasts,self.underwear,self.slut_value))
            
        def get_layer(self,body_type,tit_size):
            return self.layer
            
        def draw_item(self,body_type,height,tit_size,position):
            if not self.is_extension: #We don't draw extension items, because the image is taken care of in the main object.
                #The character you are currently interacting with is listed under the "Active" layer, so you can clear them without clearing the rest of the scene and having to redraw it.
                body_name = "" + self.name + " body" #Used so the different sprites will be placed on different levels instead of overwritting iteslf repeatedly.
                tit_name = "" + self.name + " tit"
                
                image_set = self.position_sets.get(position) # The image set we are using should corrispond to the set named "positon".
                if image_set == None: # If no image set is found with that name in the dict, use the default standing one instead. Standing should always exist.
                    image_set = self.position_sets.get("stand1") #Position names are always lowercase.
                
                if self.draws_breasts:
                    the_image = image_set.images[body_type+"_"+tit_size] #We get the image set with mutliple breast sizes because we're drawing them
                else:
                    the_image = image_set.images[body_type+"_AA"] #We get the image set with no breast sizes because they are not needed.
                
                shader_image = ShaderDisplayable(shader.MODE_2D, the_image.filename, shader.VS_2D,PS_COLOUR_SUB_LR2,{},uniforms={"colour_levels":self.colour})
                renpy.show(body_name + tit_name,at_list=[right,scale_person(height)],layer="Active",what=shader_image,tag=body_name+tit_name)
                    
    class Clothing_Images(renpy.store.object): # Stores a set of images for a single piece of cloting in a single position. The position is stored when it is put into the clothing object dict.
        def __init__(self,clothing_name,position_name,is_top):
            
            self.images = {}
            self.body_types = ["Average","Thin","Fat"]
            self.breast_sizes = ["AA","A","B","C","D","DD","DDD","E","F","FF"]
            
            for body in self.body_types:
                if is_top:
                    for breast in self.breast_sizes:
                        self.images[body+"_"+breast] = Image(clothing_name+"_"+position_name+"_"+body+"_"+breast+".png")
                else:
                    self.images[body+"_AA"] = Image(clothing_name+"_"+position_name+"_"+body+"_AA.png")
            
    class Outfit(renpy.store.object): #A bunch of clothing added together, without slot conflicts.
        def __init__(self,name):
            self.name = name
            self.upper_body = []
            self.lower_body = []
            self.feet = []
            self.accessories = [] #Extra stuff that doesn't fit anywhere else. Hats, glasses, ect.
            self.slut_requirement = 0 #The slut score requirement for this outfit.
            self.update_slut_requirement()
            
        def draw_outfit(self, body_type, height, tit_size,position): 
            #Sort each catagory by layer, then send a draw request to the clothing. This will build up the person piece by piece.
            #Draw back to front, so that layer 0 (underwear) always shows up under jackets, shirts, etc.
            
            for cloth in sorted(self.feet+self.lower_body+self.upper_body, key=lambda clothing: clothing.layer):
                cloth.draw_item(body_type, height, tit_size, position)
                
        def can_add_dress(self, new_clothing):
            allowed = True
            if not (self.can_add_upper(new_clothing) and self.can_add_lower(new_clothing.has_extension)):
                allowed = False
            return allowed
            
        def add_dress(self, new_clothing):
            if self.can_add_dress(new_clothing):
                self.upper_body.append(new_clothing)
                self.lower_body.append(new_clothing.has_extension)
                self.update_slut_requirement()
                
        def can_add_upper(self, new_clothing):
            allowed = True
            for cloth in self.upper_body:
                if cloth.layer == new_clothing.layer:
                    allowed = False
            return allowed
            
        def add_upper(self, new_clothing):
            if self.can_add_upper(new_clothing): ##Always check to make sure the clothing is valid before you add it.
                self.upper_body.append(new_clothing)
                self.update_slut_requirement()
                
        def can_add_lower(self,new_clothing):
            allowed = True
            for cloth in self.lower_body:
                if cloth.layer == new_clothing.layer:
                    allowed = False
            return allowed
                
        def add_lower(self, new_clothing):
            if self.can_add_lower(new_clothing):
                self.lower_body.append(new_clothing)
                self.update_slut_requirement()
                
        def can_add_feet(self, new_clothing):
            allowed = True
            for cloth in self.feet:
                if cloth.layer == new_clothing.layer:
                    allowed = False
            return allowed
        
        def add_feet(self, new_clothing):
            if self.can_add_feet(new_clothing):
                self.feet.append(new_clothing)
                self.update_slut_requirement()
                
        def remove_clothing(self, old_clothing):
            if old_clothing.has_extension:
                self.remove_clothing(old_clothing.has_extension)
            
            if old_clothing in self.upper_body: #Can't use elif because there might be multi-slot items
                self.upper_body.remove(old_clothing)
            elif old_clothing in self.lower_body:
                self.lower_body.remove(old_clothing)
            elif old_clothing in self.feet:
                self.feet.remove(old_clothing)
            elif old_clothing in self.accessories:
                self.accessories.remove(old_clothing)   
                
            self.update_slut_requirement()
                
        def get_upper_ordered(self): #Returns a list of pieces from bottom to top, on the upper body. Other functions do similar things, but to lower and feet.
            return sorted(self.upper_body, key=lambda clothing: clothing.layer)
            
        def get_lower_ordered(self):
            return sorted(self.lower_body, key=lambda clothing: clothing.layer)
            
        def get_feet_ordered(self):
            return sorted(self.feet, key=lambda clothing: clothing.layer)
                
        def get_upper_visible(self):
            return get_visible_list(self.upper_body)
            
        def get_lower_visible(self):
            return get_visible_list(self.lower_body)
            
        def get_feet_visible(self):
            return get_visible_list(self.feet)
            
        def get_unanchored(self): #Returns a list of the pieces of clothing that can be removed.
            return_list = []
            for top in reversed(sorted(self.upper_body, key=lambda clothing: clothing.layer)):
                return_list.append(top)
                if top.anchor_below:
                    break #Search the list, starting at the outermost item, until you find something that anchors the stuff below it.
            
            for bottom in reversed(sorted(self.lower_body, key=lambda clothing: clothing.layer)):
                return_list.append(bottom)
                if bottom.anchor_below:
                    break
                    
            for foot in reversed(sorted(self.feet, key=lambda clothing: clothing.layer)):
                return_list.append(foot)
                if foot.anchor_below:
                    break
                    
            return return_list
            
        def vagina_available(self): ## Doubles for asshole for anal.
            reachable = True
            for cloth in self.lower_body:
                if cloth.anchor_below:
                    reachable = False
            return reachable
            
        def vagina_visible(self):
            visible = True
            for cloth in self.lower_body:
                if cloth.hide_below:
                    visible = False
            return visible
            
        def tits_available(self):
            reachable = True
            for cloth in self.upper_body:
                if cloth.anchor_below:
                    reachable = False
            return reachable
            
        def tits_visible(self):
            visible = True
            for cloth in self.upper_body:
                if cloth.hide_below:
                    visible = False
            return visible
            
        def wearing_bra(self):
            if self.get_upper_ordered():
                if self.get_upper_ordered()[0].underwear:
                    return True
            return False
                    
        def wearing_panties(self):
            if self.get_lower_ordered():
                if self.get_lower_ordered()[0].underwear:
                    return True
            return False
            
        def bra_covered(self):
            if self.get_upper_ordered():
                if not self.get_upper_ordered()[-1].underwear:
                    return True
            return False
            
        def panties_covered(self):
            if self.get_lower_ordered():
                if not self.get_lower_ordered()[-1].underwear:
                    return True
            return False
                    
            
        def update_slut_requirement(self): # Recalculates the slut requirement of the outfit. Should be called after each new addition.
            new_score = 0
            
            if self.get_upper_ordered(): # We're wearing something on our top.
                if self.tits_available(): # You can reach your tits easily for a titfuck.
                    new_score += 20
                if self.tits_visible(): # Everyone can see your tits clearly.
                    
                    new_score += 20
                if not self.wearing_bra():
                    new_score += 10
                if not self.bra_covered():
                    new_score += 20 # You're not wearing a top with your underwear. 
            else:
                new_score += 40 # No top is worth a flat 40.
                
            if self.get_lower_ordered(): # We're wearing something on our top.
                if self.vagina_available(): # You can reach your tits easily for a titfuck.
                    new_score += 20
                if self.vagina_visible(): # Everyone can see your tits clearly.
                    new_score += 20
                if not self.wearing_panties():
                    new_score += 10 # You're not wearing any underwear.
                if not self.panties_covered():
                    new_score += 20 # You're not wearing a top with your underwear. 
            else:
                new_score += 40 # No bottom is worth a flat 40.
            
            
                
            for cloth in self.upper_body + self.lower_body + self.feet: #Add the extra sluttiness values of any of the pieces of clothign we're wearing.
                new_score += cloth.slut_value
                
            self.slut_requirement = new_score
                
                
    def get_visible_list(list):
        temp_list = sorted(list, key=lambda clothing: clothing.layer) #Get a sorted list
        return_list = []
        visible = True #top layer is always visisble
        for cloth in reversed(temp_list): #Starting at the top layer (ie. 3, jackets and such)
            if visible == True: #If it's visible, add it to the list
                return_list.append(cloth)
                if cloth.hide_below: #If it hides everything below, do stop it from being visible. Nothing else will be added to the retrn list now.
                    visible = False
        return return_list        
            
                
    class Wardrobe(renpy.store.object): #A bunch of outfits!
        def __init__(self,name,outfits): #Outfits is a list of Outfit objects, or empty if the wardrobe starts empty
            self.name = name
            self.outfits = outfits
            
        def __copy__(self):
            copy_list = []
            for outfit in self.outfits:
                copy_list.append(outfit)
            return Wardrobe(self.name,copy_list)
                
        
        def add_outfit(self,new_outfit):
            self.outfits.append(new_outfit)
            
        def remove_outfit(self, old_outfit):
            if old_outfit in self.outfits:
                self.outfits.remove(old_outfit)
                
        def pick_random_outfit(self):
            return copy.deepcopy(get_random_from_list(self.outfits)) # Take a deep copy, so you can change the outfit in a scene without changing the wardrobe.
            
        def get_count(self):
            return len(self.outfits)
            
        def get_outfit_list(self):
            return self.outfits
            
        def has_outfit_with_name(self, the_name):
            has_name = False
            for outfit in self.outfits:
                if outfit.name == the_name:
                    has_name = True
            return has_name
            
        def get_outfit_with_name(self, the_name):
            for outfit in self.outfits:
                if outfit.name == the_name:
                    return copy.deepcopy(outfit)
            return None
            
        def trim_wardrobe(self,sluttiness_threshold):
            trim_list = [] #List of outfits to remove, kept seperate to avoid modifying list while travsering.
            for outfit in self.outfits:
                if outfit.slut_requirement > sluttiness_threshold:
                    trim_list.append(outfit)
            
            for outfit in trim_list:
                self.remove_outfit(outfit)
        
            
    def make_wall(): #Helper functions for creating instances of commonly used objects.
        the_wall = Object("wall",["Lean"])
        return the_wall
        
    def make_window():
        the_window = Object("window",["Lean"])
        return the_window
        
    def make_chair():
        the_chair = Object("chair",["Sit","Low"])
        return the_chair
        
    def make_bed():
        the_bed = Object("bed",["Sit","Lay","Low"])
        return the_bed
        
    def make_floor():
        the_floor = Object("floor",["Lay","Kneel","Stand"])
        return the_floor
        
    def make_grass():
        the_grass = Object("grass",["Lay","Kneel","Stand"])
        return the_grass
            
    class Position(renpy.store.object):
        def __init__(self,name,slut_requirement,position_tag,requires_location,requires_clothing,skill_tag,girl_arousal,guy_arousal,connections,intro,scenes,outro,transition_default):
            self.name = name
            self.slut_requirement = slut_requirement #The required slut score of the girl. Obedience will help fill the gap if possible, at a happiness penalty. Value from 0 (almost always possible) to ~100
            self.position_tag = position_tag # The tag used to get the correct position image set
            self.requires_location = requires_location
            self.requires_clothing = requires_clothing
            self.skill_tag = skill_tag #The skill that will provide a bonus to this position.
            self.girl_arousal = girl_arousal # The base arousal the girl recieves from this position.
            self.guy_arousal = guy_arousal # The base arousal the guy recieves from this position.
            self.connections = connections
            self.intro = intro
            self.scenes = scenes
            self.outro = outro
            self.transition_default = transition_default
            self.transitions = []
            
        def link_positions(self,other,transition_label): #This is a one way link!
            self.connections.append(other)
            self.transitions.append([other,transition_label])
            
        def link_positions_two_way(self,other,transition_label_1,transition_label_2): #Link it both ways. Great for adding a modded position without modifying other positions.
            self.link_positions(other,transition_label_1)
            other.link_positions(self,transition_label_2)
            
        def call_intro(self, the_person, the_location, the_object, round):
            renpy.call(self.intro,the_person, the_location, the_object, round)
            
        def call_scene(self, the_person, the_location, the_object, round):
            random_scene = renpy.random.randint(0,len(self.scenes)-1)
            renpy.call(self.scenes[random_scene],the_person, the_location, the_object, round)
            
        def call_outro(self, the_person, the_location, the_object, round):
            renpy.call(self.outro,the_person, the_location, the_object, round)
            
        def call_transition(self,the_position, the_person, the_location, the_object, round):
            transition_scene = the_position.transition_default
            for position_tuple in self.transitions:
                if position_tuple[0] == the_position: ##Does the position match the one we are looking for?
                    transition_scene = position_tuple[1] ##If so, set it's label as the one we are going to change to.
            renpy.call(transition_scene, the_person, the_location, the_object, round)
            
        def check_clothing(self, the_person):
            if self.requires_clothing == "Vagina":
                return the_person.outfit.vagina_available()
            elif self.requires_clothing == "Tits":
                return the_person.outfit.tits_available()
            else:
                return True ##If you don't have one of the requirements listed above just let it happen.
                
    ##Initialization of requirement functions go down here. Can also be moved to init -1 eventually##
                
    def sleep_action_requirement():
        if time_of_day == 4:
            return True
        else:
            return False
            
    def faq_action_requirement():
        return True
            
    def hr_work_action_requirement():
        if time_of_day < 4:
            return True
        else:
            return False
            
    def research_work_action_requirement():
        if time_of_day < 4:
            if not mc.business.active_research_design == None:
                return True
            else:
                return False
        else:
            return False
            
    def supplies_work_action_requirement():
        if time_of_day < 4:
            return True
        else:
            return False
            
    def market_work_action_requirement():
        if time_of_day < 4:
            return True
        else:
            return False
            
    def production_work_action_requirement():
        if time_of_day < 4:
            if not mc.business.serum_production_target == None:
                return True
            else:
                return False
        else:
            return False
            
    def interview_action_requirement():
        if time_of_day < 4:
            return True
        else:
            return False
            
    def serum_design_action_requirement():
        if time_of_day < 4:
            return True
        else:
            return False
            
    def research_select_action_requirement():
        return True
            
    def production_select_action_requirement():
        return True
        
    def trade_serum_action_requirement():
        return True
        
    def sell_serum_action_requirement():
        return True
    
    def set_autosell_action_requirement():
        return mc.business.serum_production_target is not None
        
    def pick_supply_goal_action_requirement():
        return True
        
    def move_funds_action_requirement():
        return True
        
    def policy_purchase_requirement():
        return True
        
    def set_uniform_requirement():
        return strict_uniform_policy.is_owned()
        
    def set_serum_requirement():
        return daily_serum_dosage_policy.is_owned()
            
    ##Serum effect functions##
    def improved_serum_production(the_serum):
        the_serum.research_needed += 50
        the_serum.production_cost += 10
        
        the_serum.value += 20
        the_serum.suggest_raise += 10
    
        
    def basic_medical_serum_production(the_serum):
        the_serum.research_needed += 50
        the_serum.production_cost += 10
        
        the_serum.value += 40
        
    def obedience_enhancer_effect(the_serum):
        the_serum.research_needed += 75
        the_serum.production_cost += 5
        
        the_serum.value += 5
        the_serum.obedience_raise += 10
        
    def improved_duration_effect(the_serum):
        the_serum.research_needed += 75
        the_serum.production_cost += 15
        
        the_serum.value += 10
        the_serum.duration += 2
        
    def aphrodisiac_effect(the_serum):
        the_serum.research_needed + 60
        the_serum.production_cost += 10
        
        the_serum.value += 25
        the_serum.slut_raise += 15
        
    def advanced_serum_production(the_serum):
        the_serum.research_needed += 200
        the_serum.production_cost += 25
        
        the_serum.value += 50
        the_serum.suggest_raise += 30
        
    def low_volatility_reagents_effect(the_serum):
        the_serum.research_needed += 150
        the_serum.production_cost += 40
        
        the_serum.value += 20
        the_serum.duration += 5
        
    def futuristic_serum_production(the_serum):
        the_serum.research_needed += 500
        the_serum.production_cost += 50
        
        the_serum.value += 200
        the_serum.suggest_raise += 100
    
    def growing_breast_effect(the_serum):
        the_serum.research_needed += 125
        the_serum.production_cost += 20
        
        the_serum.value += 50
        
    def shrinking_breast_effect(the_serum):
        the_serum.research_needed += 125
        the_serum.production_cost += 20
        
        the_serum.value += 50
        
    def focus_enhancement_production(the_serum):
        the_serum.research_needed += 150
        the_serum.production_cost += 20
        
        the_serum.value += 30
        
        the_serum.foc_raise += 2
        
    def int_enhancement_production(the_serum):
        the_serum.research_needed += 150
        the_serum.production_cost += 20
        
        the_serum.value += 30
        
        the_serum.int_raise += 2
        
    def cha_enhancement_production(the_serum):
        the_serum.research_needed += 150
        the_serum.production_cost += 20
        
        the_serum.value += 30
        
        the_serum.cha_raise += 2
        
    def happiness_tick_effect(the_serum):
        the_serum.research_needed += 100
        the_serum.production_cost += 20
        
        the_serum.value += 100
        
    class Status_Effect(renpy.store.object): #Holds the function, name, and description of a status effect all in one playce. Duplicate status effects are not processed.
        def __init__(self,name,description,function):
            self.name = name
            self.description = description
            self.function = function        
        
    ##Status effect functions##
    def growing_breasts_function(the_person): #The target has a 10% chance for their breast size to increase by one with each time tick.
        if renpy.random.randint(0,100) < 10:
            the_person.tits = get_larger_tits(the_person.tits)
            
    def shrinking_breasts_function(the_person):
        if renpy.random.randint(0,100) < 10:
            the_person.tits = get_smaller_tits(the_person.tits)
            
    def bliss_function(the_person):
        the_person.change_happiness(5)
        the_person.change_obedience(-5)
        
        
    ##Creator Defined Displayables, used in custom menues throughout the game##

    class Vren_Line(renpy.Displayable):
        def __init__(self, start, end, thickness, color, **kwargs):
            super(Vren_Line,self).__init__(**kwargs)
            ##Base attributes
            self.start = start ## tuple of x,y coords
            self.end = end ## tuple of x,y coords
            self.thickness = thickness
            self.color = color
            
            ##Store normal values for drawing anti-aliased lines
            self.normal_temp = [self.end[0]-self.start[0],self.end[1]-self.start[1]]
            self.normal = [0,0]
            self.normal[0] = -self.normal_temp[1]
            self.normal[1] = self.normal_temp[0]
            self.mag = math.sqrt(math.pow(self.normal[0],2) + math.pow(self.normal[1],2))
            self.normal = [(self.normal[0]*self.thickness)/self.mag,(self.normal[1]*self.thickness)/self.mag]
            
            ##Store point list so we don't have to calculate it each time
            self.start_right = [self.start[0]+self.normal[0],self.start[1]+self.normal[1]]
            self.start_left = [self.start[0]-self.normal[0],self.start[1]-self.normal[1]]
            self.end_left = [self.end[0]+self.normal[0],self.end[1]+self.normal[1]]
            self.end_right = [self.end[0]-self.normal[0],self.end[1]-self.normal[1]]
            
            self.point_list = [self.start_left,self.start_right,self.end_left,self.end_right]
            
        def render(self, width, height, st, at):
            
            render = renpy.Render(1920,1080)
            canvas = render.canvas()
            
            canvas.polygon(self.color,self.point_list,) ##Draw the polygon. It will have jagged edges so we...
            canvas.aalines(self.color,False,self.point_list) ##Also draw a set of antialiased lines around the edge so it doesn't look jagged any more.
            return render
            
        def __eq__(self,other): ## Used to see if two Vren_Line objects are equivelent and thus don't need to be redrawn each time any of the variables is changed.
            if not type(other) is Vren_Line:
                return False
            
            if not (self.start == other.start and self.end == other.end and self.thickness == other.thickness and self.color == other.color): ##ie not the same
                return False
            else:
                return True
            
            
        

init -1:
    python:
        list_of_positions = []
    
        day_names = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"] #Arrays that hold the names of the days of the week and times of day. Arrays start at 0.
        time_names = ["Early Morning","Morning","Afternoon","Evening","Night"]
    
transform scale_person(scale_factor = 1):
    zoom scale_factor
        
init -2 style textbutton_style: ##The generic style used for text button backgrounds. TODO: Replace this with a pretty background image instead of a flat colour.
    padding [5,5]
    margin [5,5]
    background "#000080"
    insensitive_background "#222222"
    hover_background "#aaaaaa"
    
init -2 style textbutton_text_style: ##The generic style used for the text within buttons
    size 20
    italic True
    bold True
    color "#dddddd"
    outlines [(2,"#222222",0,0)]
    
init -2 style menu_text_style:
    size 18
    italic True
    bold True
    color "#dddddd"
    outlines [(2,"#222222",0,0)]    

init -2 style outfit_style: ##The text style used for text inside of the outfit manager.
    size 16
    italic True
    color "#dddddd"
    outlines [(1,"#666666",0,0)]
    insensitive_color "#222222"
    hover_color "#ffffff"
    
init -2:
    default name = "Input Your Name"
    default b_name = "Input Your Company Name"
    python:
        def name_func(new_name):
            store.name = new_name
            
        def b_name_func(new_name):
            store.b_name = new_name
    
screen character_create_screen():

    default cha = 0
    default int = 0
    default foc = 0
    
    default h_skill = 0
    default m_skill = 0
    default r_skill = 0
    default p_skill = 0
    default s_skill = 0
    
    default F_skill = 0
    default O_skill = 0
    default V_skill = 0
    default A_skill = 0
    
    
    default name_select = 0
    
    default character_points = 25
    
    imagebutton auto "/gui/Text_Entry_Bar_%s.png" action SetScreenVariable("name_select",1) pos (320,120) xanchor 0.5 yanchor 0.5
    imagebutton auto "/gui/Text_Entry_Bar_%s.png" action SetScreenVariable("name_select",2) pos (1600,120) xanchor 0.5 yanchor 0.5
    imagebutton auto "/gui/button/choice_%s_background.png" action Return([[cha,int,foc],[h_skill,m_skill,r_skill,p_skill,s_skill],[F_skill,O_skill,V_skill,A_skill]]) pos (300,900) xanchor 0.5 yanchor 0.5 sensitive character_points == 0 and name[0:11] != "Input Your " and b_name[0:11] != "Input Your "
    
    if name_select == 1:
        input default name pos(320,120) changed name_func xanchor 0.5 yanchor 0.5 style "menu_text_style" length 25
    else:
        text name pos(320,120) xanchor 0.5 yanchor 0.5 style "menu_text_style"
        
    if name_select == 2:
        input default b_name pos(1600,120) changed b_name_func xanchor 0.5 yanchor 0.5 style "menu_text_style" length 25
    else:
        text b_name pos(1600,120) xanchor 0.5 yanchor 0.5 style "menu_text_style"
        
    if character_points > 0 or name[0:11] == "Input Your " or b_name[0:11] == "Input Your ":
        text "Spend All Character Points to Proceed" style "menu_text_style" anchor(0.5,0.5) pos(300,900)
    elif name[0:11] == "Input Your ":
        text "Change your Character Name" style "menu_text_style" anchor(0.5,0.5) pos(300,900)
    elif b_name[0:11] == "Input Your ":
        text "Change your Company Name" style "menu_text_style" anchor(0.5,0.5) pos(300,900)
    else:
        text "Finish Character Creation" style "menu_text_style" anchor(0.5,0.5) pos(300,900)
    
    text "Character Points Remaining: [character_points]" style "menu_text_style" xalign 0.5 yalign 0.1 size 30
    hbox: #Main Stats Section
        yalign 0.7
        xalign 0.5
        xanchor 0.5
        frame:
            background "#1a45a1aa"
            vbox:
                xsize 550
                text "Main Stats (3 points/level)" style "menu_text_style" size 25
                null height 40
                hbox:
                    text "Charisma: " style "menu_text_style"
                    textbutton "<" action [SetScreenVariable("cha",cha-1), SetScreenVariable("character_points", character_points+3)] sensitive cha>0 style "textbutton_style" text_style "textbutton_text_style"
                    text str(cha) style "textbutton_text_style"
                    textbutton ">" action [SetScreenVariable("cha",cha+1), SetScreenVariable("character_points", character_points-3)] sensitive character_points>2 style "textbutton_style" text_style "textbutton_text_style"
                text "     Your visual appearance and force of personality. Charisma is the key attribute for selling serums and managing your business." style "menu_text_style"
                null height 30
                hbox:
                    text "Intelligence: " style "menu_text_style"
                    textbutton "<" action [SetScreenVariable("int",int-1), SetScreenVariable("character_points", character_points+3)] sensitive int>0 style "textbutton_style" text_style "textbutton_text_style"
                    text str(int) style "textbutton_text_style"
                    textbutton ">" action [SetScreenVariable("int",int+1), SetScreenVariable("character_points", character_points-3)] sensitive character_points>2 style "textbutton_style" text_style "textbutton_text_style"
                text "     Your raw knowledge and ability to think quickly. Intelligence is the key attribute for research and development of serums." style "menu_text_style"
                null height 30
                hbox:
                    text "Focus: " style "menu_text_style"
                    textbutton "<" action [SetScreenVariable("foc",foc-1), SetScreenVariable("character_points", character_points+3)] sensitive foc>0 style "textbutton_style" text_style "textbutton_text_style"
                    text str(foc) style "textbutton_text_style"
                    textbutton ">" action [SetScreenVariable("foc",foc+1), SetScreenVariable("character_points", character_points-3)] sensitive character_points>2 style "textbutton_style" text_style "textbutton_text_style"
                text "     Your mental endurance and precision. Focus is the key attribute for production and supply procurement." style "menu_text_style"
        
        null width 40
        frame:
            background "#1a45a1aa"
            vbox:
                xsize 550
                text "Work Skills (1 point/level)" style "menu_text_style" size 25
                null height 40
                hbox:
                    text "Human Resources: " style "menu_text_style"
                    textbutton "<" action [SetScreenVariable("h_skill",h_skill-1), SetScreenVariable("character_points", character_points+1)] sensitive h_skill>0 style "textbutton_style" text_style "textbutton_text_style"
                    text str(h_skill) style "textbutton_text_style"
                    textbutton ">" action [SetScreenVariable("h_skill",h_skill+1), SetScreenVariable("character_points", character_points-1)] sensitive character_points>0 style "textbutton_style" text_style "textbutton_text_style"
                text "     Your skill at human resources. Crutial for maintaining an efficent business." style "menu_text_style"
                null height 30
                hbox:
                    text "Marketing: " style "menu_text_style"
                    textbutton "<" action [SetScreenVariable("m_skill",m_skill-1), SetScreenVariable("character_points", character_points+1)] sensitive m_skill>0 style "textbutton_style" text_style "textbutton_text_style"
                    text str(m_skill) style "textbutton_text_style"
                    textbutton ">" action [SetScreenVariable("m_skill",m_skill+1), SetScreenVariable("character_points", character_points-1)] sensitive character_points>0 style "textbutton_style" text_style "textbutton_text_style"
                text "     Your skill at marketing. Higher skill will allow you to ship more doses of serum per day." style "menu_text_style"
                null height 30
                hbox:
                    text "Research and Development: " style "menu_text_style"
                    textbutton "<" action [SetScreenVariable("r_skill",r_skill-1), SetScreenVariable("character_points", character_points+1)] sensitive r_skill>0 style "textbutton_style" text_style "textbutton_text_style"
                    text str(r_skill) style "textbutton_text_style"
                    textbutton ">" action [SetScreenVariable("r_skill",r_skill+1), SetScreenVariable("character_points", character_points-1)] sensitive character_points>0 style "textbutton_style" text_style "textbutton_text_style"
                text "     Your skill at researching new serum traits and designs. Critical for improving your serum inventorm." style "menu_text_style"
                null height 30
                hbox:
                    text "Production: " style "menu_text_style"
                    textbutton "<" action [SetScreenVariable("p_skill",p_skill-1), SetScreenVariable("character_points", character_points+1)] sensitive p_skill>0 style "textbutton_style" text_style "textbutton_text_style"
                    text str(p_skill) style "textbutton_text_style"
                    textbutton ">" action [SetScreenVariable("p_skill",p_skill+1), SetScreenVariable("character_points", character_points-1)] sensitive character_points>0 style "textbutton_style" text_style "textbutton_text_style"
                text "     Your skill at producing serum in the production lab. Produced serums can then be sold for profit or kept for personal use." style "menu_text_style"
                null height 30
                hbox:
                    text "Supply Procurement: " style "menu_text_style"
                    textbutton "<" action [SetScreenVariable("s_skill",s_skill-1), SetScreenVariable("character_points", character_points+1)] sensitive s_skill>0 style "textbutton_style" text_style "textbutton_text_style"
                    text str(s_skill) style "textbutton_text_style"
                    textbutton ">" action [SetScreenVariable("s_skill",s_skill+1), SetScreenVariable("character_points", character_points-1)] sensitive character_points>0 style "textbutton_style" text_style "textbutton_text_style"
                text "     Your skill at obtaining raw supplies for your production division. Without supply, nothing can be created in the lab." style "menu_text_style"
                null height 30
        null width 40
        frame:
            background "#1a45a1aa"
            vbox:
                xsize 550
                text "Sex Skills (1 point/level)" style "menu_text_style" size 25
                null height 40
                hbox:
                    text "Foreplay: " style "menu_text_style"
                    textbutton "<" action [SetScreenVariable("F_skill",F_skill-1), SetScreenVariable("character_points", character_points+1)] sensitive F_skill>0 style "textbutton_style" text_style "textbutton_text_style"
                    text str(F_skill) style "textbutton_text_style"
                    textbutton ">" action [SetScreenVariable("F_skill",F_skill+1), SetScreenVariable("character_points", character_points-1)] sensitive character_points>0 style "textbutton_style" text_style "textbutton_text_style"
                text "     Your skill at foreplay, including fingering, kissing, and groping." style "menu_text_style"
                null height 30
                hbox:
                    text "Oral: " style "menu_text_style"
                    textbutton "<" action [SetScreenVariable("O_skill",O_skill-1), SetScreenVariable("character_points", character_points+1)] sensitive O_skill>0 style "textbutton_style" text_style "textbutton_text_style"
                    text str(O_skill) style "textbutton_text_style"
                    textbutton ">" action [SetScreenVariable("O_skill",O_skill+1), SetScreenVariable("character_points", character_points-1)] sensitive character_points>0 style "textbutton_style" text_style "textbutton_text_style"
                text "     Your skill at giving oral to women, as well as being a pleasant recipiant." style "menu_text_style"
                null height 30
                hbox:
                    text "Vaginal: " style "menu_text_style"
                    textbutton "<" action [SetScreenVariable("V_skill",V_skill-1), SetScreenVariable("character_points", character_points+1)] sensitive V_skill>0 style "textbutton_style" text_style "textbutton_text_style"
                    text str(V_skill) style "textbutton_text_style"
                    textbutton ">" action [SetScreenVariable("V_skill",V_skill+1), SetScreenVariable("character_points", character_points-1)] sensitive character_points>0 style "textbutton_style" text_style "textbutton_text_style"
                text "     Your skill at vaginal sex in any position." style "menu_text_style"
                null height 30
                hbox:
                    text "Anal: " style "menu_text_style"
                    textbutton "<" action [SetScreenVariable("A_skill",A_skill-1), SetScreenVariable("character_points", character_points+1)] sensitive A_skill>0 style "textbutton_style" text_style "textbutton_text_style"
                    text str(A_skill) style "textbutton_text_style"
                    textbutton ">" action [SetScreenVariable("A_skill",A_skill+1), SetScreenVariable("character_points", character_points-1)] sensitive character_points>0 style "textbutton_style" text_style "textbutton_text_style"
                text "     Your skill at anal sex in any position. (NOTE: No content included in this version)." style "menu_text_style"
                null height 30

    
screen main_ui: #The UI that shows most of the important information to the screen.
    frame:
        background "Info_Frame_1.png"
        xsize 600
        ysize 400
        yalign 0.0
        vbox:
            textbutton "Outfit Manager" action ui.callsinnewcontext("outfit_design_loop") style "textbutton_style" text_style "textbutton_text_style"
            textbutton "Check Inventory" action ui.callsinnewcontext("check_inventory_loop") style "textbutton_style" text_style "textbutton_text_style"
            textbutton "Character Sheet" action Show("mc_character_sheet") style "textbutton_style" text_style "textbutton_text_style"
            text "Day: " + day_names[day%7] + "([day])" style "menu_text_style"
            text "Time: " + time_names[time_of_day] style "menu_text_style"
#            text "Energy: [mc.energy]" style "menu_text_style"
            text "Arousal: [mc.arousal]/100" style "menu_text_style"
            text "Cash: $[mc.money]" style "menu_text_style"
            text "Location: [mc.location.formalName]" style "menu_text_style"
        
screen business_ui: #Shows some information about your business.
    frame:
        background im.Flip("Info_Frame_1.png",vertical=True)
        xsize 600
        ysize 400
        yalign 1.0
        vbox:
            yanchor 1.0
            yalign 1.0
            text "Company Name: " style "menu_text_style"
            text "    [mc.business.name]" style "menu_text_style"
            text "Company Funds: $[mc.business.funds]" style "menu_text_style"
            text "Daily Salary Cost: $"+ str(mc.business.calculate_salary_cost()) style "menu_text_style"
            text "Company Efficency: [mc.business.team_effectiveness]%" style "menu_text_style"
#            text "Company Marketability: [mc.business.marketability]" style "menu_text_style"
            text "Current Raw Supplies: [mc.business.supply_count] (Target:[mc.business.supply_goal])" style "menu_text_style"
            if not mc.business.active_research_design == None:
                text "Current Research: " style "menu_text_style"
                text "    [mc.business.active_research_design.name] ([mc.business.active_research_design.current_research]/[mc.business.active_research_design.research_needed])" style "menu_text_style"
            else:
                text "Current Research: None!" style "menu_text_style" color "#DD0000"
            if not mc.business.serum_production_target == None:
                text "Currently Producing: " style "menu_text_style"
                text "    [mc.business.serum_production_target.name]" style "menu_text_style"
            else:
                text "Currently Producing: Nothing!" style "menu_text_style" color "#DD0000"
            textbutton "Review Staff" action Show("employee_overview") style "textbutton_style" text_style "textbutton_text_style"
            textbutton "Check Stock" action ui.callsinnewcontext("check_business_inventory_loop") style "textbutton_style" text_style "textbutton_text_style"
            
screen end_of_day_update():
    add "Paper_Background.png"
    text mc.business.name:
        style "textbutton_text_style"
        xanchor 0.5
        xalign 0.5
        yalign 0.1
        size 40
    
    frame:
        background "#1a45a1aa"
        xalign 0.1
        yalign 0.25
        xanchor 0.0
        vbox:
            xsize 1500
            ysize 200
            text "Daily Statistics:" style "textbutton_text_style" size 20
            text "     " + "Current Efficency Modifier: " + str(mc.business.team_effectiveness) + "%" style "textbutton_text_style"
            text "     " + "Production Potential: " + str(mc.business.production_potential) style "textbutton_text_style"
            text "     " + "Supplies Procured: " + str(mc.business.supplies_purchased) + " Units" style "textbutton_text_style"
            text "     " + "Production Used: " + str(mc.business.production_used) style "textbutton_text_style"
            text "     " + "Research Produced: " + str(mc.business.research_produced) style "textbutton_text_style"
            text "     " + "Sales Made: $" + str(mc.business.sales_made) style "textbutton_text_style"
            text "     " + "Daily Salary Paid: $" + str(mc.business.calculate_salary_cost()) style "textbutton_text_style"
    
    frame:
        background "#1a45a1aa"
        xalign 0.1
        yalign 0.45
        xanchor 0.0
        yanchor 0.0
        viewport:
            mousewheel True
            scrollbars "vertical"
            xsize 1500
            ysize 350
            vbox:
                text "Highlights:" style "textbutton_text_style" size 20
                for item in mc.business.message_list:
                    text "     " + item style "textbutton_text_style"
                
                for item in mc.business.counted_message_list:
                    text "     " + item + " x " + str(int(mc.business.counted_message_list[item])) style "textbutton_text_style"
    
    frame:
        background None
        anchor [0.5,0.5]
        align [0.5,0.9]
        xysize [500,125]
        imagebutton:
            align [0.5,0.5]
            auto "gui/button/choice_%s_background.png"
            focus_mask "gui/button/choice_idle_background.png"
            action Return()
        textbutton "End Day" align [0.5,0.5] style "button_text"
        
screen employee_overview():
    add "Paper_Background.png"
    default division_select = "None"
    default division_name = "None"
    $ showing_team = []
    modal True
    hbox:
        yalign 0.05
        xalign 0.05
        textbutton "Research" action SetScreenVariable("division_select","r") style "textbutton_style" text_style "textbutton_text_style"
        textbutton "Production" action SetScreenVariable("division_select","p") style "textbutton_style" text_style "textbutton_text_style"
        textbutton "Supply" action SetScreenVariable("division_select","s") style "textbutton_style" text_style "textbutton_text_style"
        textbutton "Marketing" action SetScreenVariable("division_select","m") style "textbutton_style" text_style "textbutton_text_style"
        textbutton "Human Resources" action SetScreenVariable("division_select","h") style "textbutton_style" text_style "textbutton_text_style"
    
    python:
        if division_select is None:
            showing_team = []
            division_name = "None"
        elif division_select == "r":
            showing_team = mc.business.research_team
            division_name = "Research"
        elif division_select == "p":
            showing_team = mc.business.production_team
            division_name = "Production"
        elif division_select == "s":
            showing_team = mc.business.supply_team
            division_name = "Supply Procurement"
        elif division_select == "m":
            showing_team = mc.business.market_team
            division_name = "Marketing"
        elif division_select == "h":
            showing_team = mc.business.hr_team
            division_name = "Human Resources"
    
    
    text "Position: " + division_name style "menu_text_style" size 20 yalign 0.18 xalign 0.02 xanchor 0.0
    frame:
        yalign 0.2
        xalign 0.5
        yanchor 0.0
        background "#1a45a1aa"
        xsize 1800
        side ("c r"):
            area (1,0,1800,600)
            viewport id "Positions_list":
                draggable True mousewheel True
                grid 14 len(showing_team)+1:
                    text "Name" style "menu_text_style"
                    text "Salary" style "menu_text_style"
                    text "Happiness" style "menu_text_style"
                    text "Obedience" style "menu_text_style"
                    text "Sluttiness" style "menu_text_style"
                    text "Suggest" style "menu_text_style"
                    text "Charisma" style "menu_text_style"
                    text "Int" style "menu_text_style"
                    text "Focus" style "menu_text_style"
                    text "Research" style "menu_text_style"
                    text "Production " style "menu_text_style"
                    text "Supply" style "menu_text_style"
                    text "Marketing " style "menu_text_style"
                    text "HR" style "menu_text_style"

                    for person in showing_team:
                        textbutton person.name + "\n" + person.last_name style "textbutton_style" text_style "menu_text_style" action Show("person_info_detailed",None,person)
#                        text person.name + "\n" + person.last_name style "menu_text_style"
                        text "$" + str(person.salary) + "/day" style "menu_text_style"
                        text str(int(person.happiness)) style "menu_text_style"
                        text str(int(person.obedience)) style "menu_text_style"
                        text str(int(person.sluttiness)) style "menu_text_style"
                        text str(int(person.suggestibility)) style "menu_text_style"
                        text str(int(person.charisma)) style "menu_text_style"
                        text str(int(person.int)) style "menu_text_style"
                        text str(int(person.focus)) style "menu_text_style"
                        text str(int(person.research_skill)) style "menu_text_style"
                        text str(int(person.production_skill)) style "menu_text_style"
                        text str(int(person.supply_skill)) style "menu_text_style"
                        text str(int(person.market_skill)) style "menu_text_style"
                        text str(int(person.hr_skill)) style "menu_text_style"
            vbar value YScrollValue("Positions_list") xalign 1.0
    frame:
        background None
        anchor [0.5,0.5]
        align [0.5,0.88]
        xysize [500,125]
        imagebutton:
            align [0.5,0.5]
            auto "gui/button/choice_%s_background.png"
            focus_mask "gui/button/choice_idle_background.png"
            action Hide("employee_overview")
        textbutton "Return" align [0.5,0.5] style "return_button_style"
    
            
screen person_info_ui(the_person): #Used to display stats for a person while you're talking to them.
    frame:
        background im.Flip("Info_Frame_1.png",vertical=True)
        xsize 400
        ysize 400
        yalign 1.0
        vbox:
            yalign 1.0
            text "Name: [the_person.name]" style "menu_text_style"
            if mc.business.get_employee_title(the_person) == "None":
                text "Job: Not employed." style "menu_text_style"
            else:
                text "Job: " + mc.business.get_employee_title(the_person) style "menu_text_style"
            #text "Height: " + height_to_string(the_person.height) #Showing this here during sex scenes breaks things for some reason, might be use of "height" as a variable name?
            text "Arousal: [the_person.arousal]/100" style "menu_text_style"
            text "***********" style "menu_text_style"
            text "Happiness: [the_person.happiness]" style "menu_text_style"
            text "Suggestibility: [the_person.suggestibility]" style "menu_text_style"
            text "Sluttiness: [the_person.sluttiness]" style "menu_text_style"
            text "Obedience: [the_person.obedience]" style "menu_text_style"
            textbutton "Detailed Information" action Show("person_info_detailed",the_person=the_person) style "textbutton_style" text_style "textbutton_text_style"
            
            
screen person_info_detailed(the_person):
    add "Paper_Background.png"
    modal True
    default hr_base = the_person.charisma*3 + the_person.hr_skill*2 + the_person.int + 10
    default market_base = the_person.charisma*3 + the_person.market_skill*2 + the_person.focus + 10
    default research_base = the_person.int*3 + the_person.research_skill*2 + the_person.focus + 10
    default prod_base = the_person.focus*3 + the_person.production_skill*2 + the_person.int + 10
    default supply_base = the_person.focus*3 + the_person.supply_skill*2 + the_person.charisma + 10
    
    hbox:
        xalign 0.1
        yalign 0.1
        vbox:
            xsize 1000
            text "Name: [the_person.name] [the_person.last_name]" style "menu_text_style" size 25
            text "Height: " + str(height_to_string(the_person.height)) style "menu_text_style" #TODO: Figure out why calling height while in a sex scene breaks everything.
            text "**********" style "menu_text_style"
            text "Happiness: [the_person.happiness]" style "menu_text_style"
            text "Suggestibility: [the_person.suggestibility]" style "menu_text_style"
            text "Sluttiness: [the_person.sluttiness]" style "menu_text_style"
            text "Obedience: [the_person.obedience]" style "menu_text_style"
            text "***********" style "menu_text_style"
            text "Charisma: [the_person.charisma]" style "menu_text_style"
            text "Intelligence: [the_person.int]" style "menu_text_style"
            text "Focus: [the_person.focus]" style "menu_text_style"
            text "***********" style "menu_text_style"
            text "HR Skill: [the_person.hr_skill]" style "menu_text_style"
            text "Marketing Skill: [the_person.market_skill]" style "menu_text_style"
            text "Researching Skill: [the_person.research_skill]" style "menu_text_style"
            text "Production Skill: [the_person.production_skill]" style "menu_text_style"
            text "Supply Skill: [the_person.supply_skill]" style "menu_text_style"
            text "***********" style "menu_text_style"
            for skill in the_person.sex_skills:
                text skill + " Skill: " + str(the_person.sex_skills[skill]) style "menu_text_style"
            
            null height 200
            if mc.business.get_employee_title(the_person) != "None":
                text "Position: " + mc.business.get_employee_title(the_person) style "menu_text_style"
                text "Current Salary: $[the_person.salary]" style "menu_text_style"
                text "Base HR Efficency Production (Cha x 3 + Skill x 2 + Int x 1 + 10): [hr_base]" style "menu_text_style"
                text "Base Marketing Sales Cap (Cha x 3 + Skill x 2 + Focus x 1 + 10): [market_base]" style "menu_text_style"
                text "Base Research Generation (Int x 3 + Skill x 2 + Focus x 1 + 10): [research_base]" style "menu_text_style"
                text "Base Production Generation (Focus x 3 + Skill x 2 + Int x 1 + 10): [prod_base]" style "menu_text_style"
                text "Base Supply Generation (Focus x 3 + Skill x 2 + Cha x 1 + 10): [supply_base]" style "menu_text_style"
                
        vbox:
            xsize 800
            text "Currently Affected By:" style "menu_text_style"
            for serum in the_person.serum_effects:
                text serum.name + " : " + str(serum.duration - serum.duration_counter) + " Turns Left" style "menu_text_style"
            null height 80
            text "Current Status Effects:" style "menu_text_style"
            for effect in set(the_person.status_effects):
                text effect.name style "menu_text_style"
        
    frame:
        background None
        anchor [0.5,0.5]
        align [0.5,0.88]
        xysize [500,125]
        imagebutton:
            align [0.5,0.5]
            auto "gui/button/choice_%s_background.png"
            focus_mask "gui/button/choice_idle_background.png"
            action Hide("person_info_detailed")
        textbutton "Return" align [0.5,0.5] style "return_button_style"
        
screen mc_character_sheet(): #TODO: Impliment a level up system for the main character
    add "Paper_Background.png"
    modal True
    vbox:
        xalign 0.5
        yalign 0.05
        text mc.name style "menu_text_style" size 40 xanchor 0.5 xalign 0.5
        text "Owner of: " + mc.business.name style "menu_text_style" size 30 xanchor 0.5 xalign 0.5
        
    hbox:
        xanchor 0.5
        xalign 0.5
        yalign 0.2
        vbox:
            xsize 600
            xanchor -0.5
            text "Main Stats" style "menu_text_style" size 25 xalign 0.5
            text "Charisma: " + str(mc.charisma) style "menu_text_style" xalign 0.5
            text "Intelligence: " + str(mc.int) style "menu_text_style" xalign 0.5
            text "Focus: " + str(mc.focus) style "menu_text_style" xalign 0.5
            
        vbox:
            xsize 600
            xalign 0.5
            text "Work Skills" style "menu_text_style" size 25 xalign 0.5
            text "Human Resources: " + str(mc.hr_skill) style "menu_text_style" xalign 0.5
            text "Marketing: " + str(mc.market_skill) style "menu_text_style" xalign 0.5
            text "Research and Development: " + str(mc.research_skill) style "menu_text_style" xalign 0.5
            text "Production: " + str(mc.production_skill) style "menu_text_style" xalign 0.5
            text "Supply Procurement: " + str(mc.supply_skill) style "menu_text_style" xalign 0.5
            
        vbox:
            xsize 600
            xanchor 0.5
            text "Sex Skills" style "menu_text_style" size 25 xalign 0.5
            text "Foreplay: " + str(mc.sex_skills["Foreplay"]) style "menu_text_style" xalign 0.5
            text "Oral: " + str(mc.sex_skills["Oral"]) style "menu_text_style" xalign 0.5
            text "Vaginal: " + str(mc.sex_skills["Vaginal"]) style "menu_text_style" xalign 0.5
            text "Anal: " + str(mc.sex_skills["Anal"]) style "menu_text_style" xalign 0.5
            
    frame:
        background None
        anchor [0.5,0.5]
        align [0.5,0.88]
        xysize [500,125]
        imagebutton:
            align [0.5,0.5]
            auto "gui/button/choice_%s_background.png"
            focus_mask "gui/button/choice_idle_background.png"
            action Hide("mc_character_sheet")
        textbutton "Return" align [0.5,0.5] text_style "return_button_style"
        
    
    
    
        
screen interview_ui(the_candidates,count):
    default current_selection = 0
    default the_candidate = the_candidates[current_selection]
    hbox:
        vbox:
            xsize 600
            text "Name: [the_candidate.name]" style "menu_text_style"
            text "Age: [the_candidate.age]" style "menu_text_style"
            text "Daily Salary: $[the_candidate.salary]" style "menu_text_style"
        
        vbox:
            xsize 600
            text "Stats" style "menu_text_style"
            text "Charisma: [the_candidate.charisma]" style "menu_text_style"
            text "Intelligence: [the_candidate.int]" style "menu_text_style"
            text "Focus: [the_candidate.focus]" style "menu_text_style"
            text "*******" style "menu_text_style"
            text "Skills" style "menu_text_style"
            text "Human Resources: [the_candidate.hr_skill]" style "menu_text_style"
            text "Marketing: [the_candidate.market_skill]" style "menu_text_style"
            text "Research: [the_candidate.research_skill]" style "menu_text_style"
            text "Production: [the_candidate.production_skill]" style "menu_text_style"
            text "Procurement: [the_candidate.supply_skill]" style "menu_text_style"
            
    hbox:
        xalign 0.0
        yalign 1.0
        vbox:
            textbutton "Hire " action Return(the_candidate) style "textbutton_style" text_style "textbutton_text_style"
            textbutton "Next Candidate" action [SetScreenVariable("current_selection",current_selection+1),
                SetScreenVariable("the_candidate",the_candidates[current_selection+1]),
                Function(show_candidate,the_candidates[current_selection+1])] sensitive current_selection < count-1 selected False style "textbutton_style" text_style "textbutton_text_style"
            
            
            textbutton "Previous Candidate" action [SetScreenVariable("current_selection",current_selection-1),
                SetScreenVariable("the_candidate",the_candidates[current_selection-1]),
                Function(show_candidate,the_candidates[current_selection-1])] sensitive current_selection > 0 selected False style "textbutton_style" text_style "textbutton_text_style"
            
            textbutton "Hire Nobody" action Return("None") style "textbutton_style" text_style "textbutton_text_style"
         
init -2 python: # Some functions used only within screens for modifying variables
    def show_candidate(the_candidate):
        renpy.scene("Active")
        the_candidate.draw_person("stand1")
    
    def apply_trait_add_list(the_serum,current_traits,the_trait): #Called by the serum design UI so I can keep a list organized
        current_traits.append(the_trait)
        the_trait.effect(the_serum)
        the_serum.status_effects.extend(the_trait.status_effects)
        
    def remove_trait_recalc(the_serum,current_traits,the_trait): #Removes the trait and recalculates the serum based on the other traits still in the list
        current_traits.remove(the_trait)
        the_serum.reset()
        for trait in current_traits:
            trait.effect(the_serum)
            the_serum.status_effects.extend(the_trait.status_effects)
            
            
    def set_trait_list(traits,serum):
        serum.set_traits(traits)
        
screen show_serum_inventory(the_inventory):
    add "Science_Menu_Background.png"
    vbox:
        xalign 0.02
        yalign 0.02
        text "Serums in Inventory" style "menu_text_style" size 25
        for design in the_inventory.serums_held:
            textbutton design[0].name + ": " + str(design[1]) style "textbutton_style" text_style "textbutton_text_style" action NullAction() sensitive True hovered Show("serum_tooltip",None,design[0]) unhovered Hide("serum_tooltip")
                
        textbutton "Return" action Return() style "textbutton_style" text_style "textbutton_text_style"
            
screen serum_design_ui(starting_serum,current_traits):
    add "Science_Menu_Background.png"
    hbox:
        xalign 0.01
        ysize 400
        vbox:
            xsize 600
            text "Add a new trait" style "menu_text_style"
            for trait in list_of_traits:
                if not trait in current_traits and trait.researched:
                    textbutton "Add " + trait.name action [Hide("trait_tooltip"),Function(apply_trait_add_list,starting_serum,current_traits,trait)] style "textbutton_style" text_style "textbutton_text_style" hovered Show("trait_tooltip",None,trait,0.3,0.6) unhovered Hide("trait_tooltip")
            
        vbox:
            xsize 600
            text "Remove a trait" style "menu_text_style"
            for trait in current_traits:
                textbutton "Remove " + trait.name action Function(remove_trait_recalc,starting_serum,current_traits,trait) style "textbutton_style" text_style "textbutton_text_style"
                
        vbox:
            xsize 600
            text "Current Traits:" style "menu_text_style"
            for trait in current_traits:
                text "Trait: " + trait.name style "menu_text_style"
                text "*******" style "outfit_style"
                text "Description: " + trait.desc style "menu_text_style"
                text " " style "ouftit_style"
    
    hbox:
        ysize 300
        yalign 0.6
        xalign 0.01
        vbox:
            text "Current Serum Statistics:" style "menu_text_style"
            text "Research Required: [starting_serum.research_needed]" style "menu_text_style"
            text "Production Cost: [starting_serum.production_cost]" style "menu_text_style"
            text "Value: [starting_serum.value]" style "menu_text_style"
            text "Duration (Time Segments): [starting_serum.duration]" style "menu_text_style"
            text "Suggestion: [starting_serum.suggest_raise]" style "menu_text_style"
            text "Happiness: [starting_serum.happiness_raise]" style "menu_text_style"
            text "Sluttiness: [starting_serum.slut_raise]" style "menu_text_style"
            text "Obedience: [starting_serum.obedience_raise]" style "menu_text_style"
            text "Charisma Boost: [starting_serum.cha_raise]" style "menu_text_style"
            text "Intelligence Boost: [starting_serum.int_raise]" style "menu_text_style"
            text "Focus Boost: [starting_serum.foc_raise]" style "menu_text_style"
            
    hbox:
        yalign 0.9
        xalign 0.01
        vbox:
            textbutton "Create serum design." action [Function(set_trait_list,current_traits,starting_serum),Return(starting_serum)] style "textbutton_style" text_style "textbutton_text_style"
            textbutton "Quit." action Return("None") style "textbutton_style" text_style "textbutton_text_style"
            
screen serum_tooltip(the_serum):
    vbox:
        xalign 0.9
        yalign 0.0
        xsize 500
        text "Research Required: [the_serum.research_needed]" style "menu_text_style"
        text "Production Cost: [the_serum.production_cost]" style "menu_text_style"
        text "Value: [the_serum.value]" style "menu_text_style"
        text "Duration (Time Segments): [the_serum.duration]" style "menu_text_style"
        text "Suggestion: [the_serum.suggest_raise]" style "menu_text_style"
        text "Happiness: [the_serum.happiness_raise]" style "menu_text_style"
        text "Sluttiness: [the_serum.slut_raise]" style "menu_text_style"
        text "Obedience: [the_serum.obedience_raise]" style "menu_text_style"
        text "Charisma Boost: [the_serum.cha_raise]" style "menu_text_style"
        text "Intelligence Boost: [the_serum.int_raise]" style "menu_text_style"
        text "Focus Boost: [the_serum.foc_raise]" style "menu_text_style" 
        text ""
        if len(the_serum.traits) > 0:
            text "*********\n" style "menu_text_style"
        for trait in the_serum.traits:
            text "Trait: " + trait.name style "menu_text_style"
            text trait.desc style "menu_text_style"
            text "\n*********\n" style "menu_text_style"
            
screen trait_tooltip(the_trait,given_xalign=0.9,given_yalign=0.0):
    vbox:
        xalign given_xalign
        yalign given_yalign
        xsize 500
        text the_trait.name style "menu_text_style"
        text "\n*********\n" style "menu_text_style"
        text "Research Required: [the_trait.research_needed]" style "menu_text_style"
        text the_trait.desc style "menu_text_style"
            
            
screen serum_trade_ui(inventory_1,inventory_2,name_1="Player",name_2="Business"): #Lets you trade serums back and forth between two different inventories. Inventory 1 is assumed to be the players.
    add "Science_Menu_Background.png"
    vbox:
        xalign 0.02
        yalign 0.02
        text "Trade Serums Between Inventories." style "menu_text_style" size 25
        for serum in set(inventory_1.get_serum_type_list()) | set(inventory_2.get_serum_type_list()): #Gets a unique entry for each serum design that shows up in either list. Doesn't duplicate if it's in both.
            # has a few things. 1) name of serum design. 2) count of first inventory, 3) arrows for transfering, 4) count of second inventory.
            vbox:
                textbutton serum.name + ": " style "textbutton_style" text_style "menu_text_style" action NullAction() hovered Show("serum_tooltip",None,serum) unhovered Hide("serum_tooltip") #displays the name of this particular serum
                hbox:
                    null width 40
                    text name_1 + " has: " + str(inventory_1.get_serum_count(serum)) style "menu_text_style"#The players current inventory count. 0 if there is nothing in their inventory
                    textbutton "#<#" action [Function(inventory_1.change_serum,serum,1),Function(inventory_2.change_serum,serum,-1)] sensitive (inventory_2.get_serum_count(serum) > 0) style "textbutton_style" text_style "textbutton_text_style"
                    #When pressed, moves 1 serum from the business inventory to the player. Not active if the business has nothing in it.
                    null width 40
                    textbutton "#>#" action [Function(inventory_2.change_serum,serum,1),Function(inventory_1.change_serum,serum,-1)] sensitive (inventory_1.get_serum_count(serum) > 0) style "textbutton_style" text_style "textbutton_text_style"
                    text name_2 + " has: " + str(inventory_2.get_serum_count(serum)) style "menu_text_style"
        textbutton "Finished." action Return() style "textbutton_style" text_style "textbutton_text_style"
                
                
screen serum_select_ui: #How you select serum and trait research
    add "Science_Menu_Background.png"
    vbox:
        if not mc.business.active_research_design == None:
            text "Current Research: [mc.business.active_research_design.name] ([mc.business.active_research_design.current_research]/[mc.business.active_research_design.research_needed])" style "menu_text_style"
        else:
            text "Current Research: None!" style "menu_text_style"
        
        hbox:
            vbox:
                text "Serum Designs:" style "menu_text_style"
                for serum in mc.business.serum_designs:
                    if not serum.researched:
                        textbutton "Research [serum.name] ([serum.current_research]/[serum.research_needed])" action [Hide("serum_tooltip"),Return(serum)] style "textbutton_style" text_style "textbutton_text_style" hovered Show("serum_tooltip",None,serum) unhovered Hide("serum_tooltip")
             
            null width 40
            
        vbox:
            text "New Traits:" style "menu_text_style"
            for trait in list_of_traits:
                if not trait.researched and trait.has_required():
                    textbutton "Research [trait.name] ([trait.current_research]/[trait.research_needed])" action [Hide("trait_tooltip"),Return(trait)] style "textbutton_style" text_style "textbutton_text_style" hovered Show("trait_tooltip",None,trait) unhovered Hide("trait_tooltip")
                    
    textbutton "Do not change research." action Return("None") style "textbutton_style" text_style "textbutton_text_style" yalign 0.995
        
screen serum_production_select_ui:
    add "Science_Menu_Background.png"
    vbox:
        xalign 0.1
        xsize 1200
        null height 40 
        if not mc.business.serum_production_target == None:
            text "Currently Producing: [mc.business.serum_production_target.name] - $[mc.business.serum_production_target.value]/dose (Current Progress: [mc.business.production_points]/[mc.business.serum_production_target.production_cost])" style "menu_text_style" size 25
        else:
            text "Currently Producing: Nothing!" style "menu_text_style"
        
        null height 40
        text "Change Production To:" style "menu_text_style" size 20
        vbox:
            xsize 1000
            xalign 0.2
            for serum in mc.business.serum_designs:
                if serum.researched:
                    textbutton "Produce [serum.name] (Requires [serum.production_cost] production points per dose. Worth $[serum.value]/dose)" action [Hide("serum_tooltip"),Return(serum)] style "textbutton_style" text_style "textbutton_text_style" hovered Show("serum_tooltip",None,serum) unhovered Hide("serum_tooltip")
        textbutton "Do not change production." action Return("None") style "textbutton_style" text_style "textbutton_text_style"
        
screen serum_inventory_select_ui(the_inventory): #Used to let the player select a serum from an inventory.
    add "Science_Menu_Background.png"
    vbox:
        for serum in the_inventory.serums_held:
            textbutton serum[0].name + "(" + str(serum[1]) + ")" action [Hide("serum_tooltip"),Return(serum[0])] style "textbutton_style" text_style "textbutton_text_style" hovered Show("serum_tooltip",None,serum[0]) unhovered Hide("serum_tooltip")
        textbutton "Return" action Return("None") style "textbutton_style" text_style "textbutton_text_style"
            
        
screen outfit_creator(starting_outfit): ##Pass a completely blank outfit instance for a new outfit, or an already existing instance to load an old one.\
    add "Paper_Background.png"
    default panties_label = "None"
    default bra_label = "None"
    default pants_label = "None"
    default skirts_label = "None"
    default dress_label = "None"
    default shirts_label = "None"
    default socks_label = "None"
    default shoes_label = "None"
    default demo_outfit = copy.deepcopy(starting_outfit)
    #Each catagory below has a click to enable button. If it's false, we don't show anything for it.
    hbox:
        vbox:
            xsize 400
            spacing -20
            text "Add Clothing" style "menu_text_style"
            null height 50
            
            textbutton "Panties" action ToggleScreenVariable("panties_label","Panties","None") style "textbutton_style" text_style "textbutton_text_style"
            null height 30
            if panties_label == "Panties":
                for cloth in panties_list:
                    textbutton "    " + cloth.name:
                        action Function(starting_outfit.add_lower, cloth) sensitive starting_outfit.can_add_lower(cloth) text_style "outfit_style" hovered Function(demo_outfit.add_lower, cloth) unhovered Function(demo_outfit.remove_clothing, cloth)
            null height 30
            
            textbutton "Bras" action ToggleScreenVariable("bra_label","Bras","None") style "textbutton_style" text_style "textbutton_text_style"
            null height 30
            if bra_label == "Bras":
                for cloth in bra_list:
                    textbutton "    " + cloth.name action Function(starting_outfit.add_upper, cloth) sensitive starting_outfit.can_add_upper(cloth) text_style "outfit_style" hovered Function(demo_outfit.add_upper, cloth) unhovered Function(demo_outfit.remove_clothing, cloth)
            null height 30
            
            textbutton "Pants" action ToggleScreenVariable("pants_label","Pants","None") style "textbutton_style" text_style "textbutton_text_style"
            null height 30
            if pants_label == "Pants":
                for cloth in pants_list:
                    textbutton "    " + cloth.name action Function(starting_outfit.add_lower, cloth) sensitive starting_outfit.can_add_lower(cloth) text_style "outfit_style" hovered Function(demo_outfit.add_lower, cloth) unhovered Function(demo_outfit.remove_clothing, cloth)
            null height 30
            
            textbutton "Skirts" action ToggleScreenVariable("skirts_label","Skirts","None") style "textbutton_style" text_style "textbutton_text_style"
            null height 30
            if skirts_label == "Skirts":
                for cloth in skirts_list:
                    textbutton "    " + cloth.name action Function(starting_outfit.add_lower, cloth) sensitive starting_outfit.can_add_lower(cloth) text_style "outfit_style" hovered Function(demo_outfit.add_lower, cloth) unhovered Function(demo_outfit.remove_clothing, cloth)
            null height 30
            
            textbutton "Dresses" action ToggleScreenVariable("dress_label","Dress","None") style "textbutton_style" text_style "textbutton_text_style"
            null height 30
            if dress_label == "Dress":
                for cloth in dress_list:
                    textbutton "    " + cloth.name action Function(starting_outfit.add_dress, cloth) sensitive starting_outfit.can_add_dress(cloth) text_style "outfit_style" hovered Function(demo_outfit.add_dress, cloth) unhovered Function(demo_outfit.remove_clothing, cloth)
            null height 30
             
            textbutton "Shirts" action ToggleScreenVariable("shirts_label","Shirts","None") style "textbutton_style" text_style "textbutton_text_style"
            null height 30
            if shirts_label == "Shirts":
                for cloth in shirts_list:
                    textbutton "    " + cloth.name action Function(starting_outfit.add_upper, cloth) sensitive starting_outfit.can_add_upper(cloth) text_style "outfit_style" hovered Function(demo_outfit.add_upper, cloth) unhovered Function(demo_outfit.remove_clothing, cloth)
            null height 30
            
            textbutton "Socks" action ToggleScreenVariable("socks_label","Socks","None") style "textbutton_style" text_style "textbutton_text_style"
            null height 30
            if socks_label == "Socks":
                for cloth in socks_list:
                    textbutton "    " + cloth.name action Function(starting_outfit.add_feet, cloth) sensitive starting_outfit.can_add_feet(cloth) text_style "outfit_style" hovered Function(demo_outfit.add_feet, cloth) unhovered Function(demo_outfit.remove_clothing, cloth)
            null height 30
                
            textbutton "Shoes" action ToggleScreenVariable("shoes_label","Shoes","None") style "textbutton_style" text_style "textbutton_text_style"
            null height 30
            if shoes_label == "Shoes":
                for cloth in shoes_list:
                    textbutton "    " + cloth.name action Function(starting_outfit.add_feet, cloth) sensitive starting_outfit.can_add_feet(cloth) text_style "outfit_style" hovered Function(demo_outfit.add_feet, cloth) unhovered Function(demo_outfit.remove_clothing, cloth)
            null height 30
        
        null width 80 height 100 ## Adds an empty space
        
        vbox:
            text "Remove Clothing" style "menu_text_style"
            for cloth in starting_outfit.upper_body:
                if not cloth.is_extension: #Don't list extensions for removal.
                    textbutton cloth.name action [Function(starting_outfit.remove_clothing, cloth),Function(demo_outfit.remove_clothing, cloth)] text_style "outfit_style"
                
            for cloth in starting_outfit.lower_body:
                if not cloth.is_extension:
                    textbutton cloth.name action [Function(starting_outfit.remove_clothing, cloth),Function(demo_outfit.remove_clothing, cloth)] text_style "outfit_style"
                
            for cloth in starting_outfit.feet:
                if not cloth.is_extension:
                    textbutton cloth.name action [Function(starting_outfit.remove_clothing, cloth),Function(demo_outfit.remove_clothing, cloth)] text_style "outfit_style"
                
            for cloth in starting_outfit.accessories:
                if not cloth.is_extension:
                    textbutton cloth.name action [Function(starting_outfit.remove_clothing, cloth),Function(demo_outfit.remove_clothing, cloth)] text_style "outfit_style"
                
        null width  80 height 100 ## More whitespace
        
        vbox:
            text "Outfit Stats" style "menu_text_style"
            text "Sluttiness Required: " + str(demo_outfit.slut_requirement) style "menu_text_style"
            text "Tits Visible: " + str(demo_outfit.tits_visible()) style "menu_text_style"
            text "Tits Usable: " + str(demo_outfit.tits_available()) style "menu_text_style"
            text "Wearing a Bra: " + str(demo_outfit.wearing_bra()) style "menu_text_style"
            text "Bra Covered: " + str(demo_outfit.bra_covered()) style "menu_text_style"
            text "Pussy Visible: " + str(demo_outfit.vagina_visible()) style "menu_text_style"
            text "Pussy Usable: " + str(demo_outfit.vagina_available()) style "menu_text_style"
            text "Wearing Panties: " + str(demo_outfit.wearing_panties()) style "menu_text_style"
            text "Panties Covered: " + str(demo_outfit.panties_covered()) style "menu_text_style"
        
        null width  80 height 100 ## More whitespace
        
        vbox:
            textbutton "Save Outfit" pos (0,0) action Return(copy.deepcopy(starting_outfit)) style "textbutton_style" text_style "textbutton_text_style"
            
        null width  80 height 100
            
        vbox:
            textbutton "Leave Without Saving" pos (0,0) action Return("Not_New") style "textbutton_style" text_style "textbutton_text_style"
        
    fixed: #TODO: Move this to it's own screen so it can be shown anywhere
        pos (1500,0)
        
        add mannequin_average
        for cloth in sorted(demo_outfit.feet+demo_outfit.lower_body+demo_outfit.upper_body, key=lambda clothing: clothing.layer):
            if not cloth.is_extension:
                if cloth.draws_breasts:
                    add ShaderDisplayable(shader.MODE_2D, cloth.position_sets.get("stand1").images["Average_D"].filename, shader.VS_2D,PS_COLOUR_SUB_LR2,{},uniforms={"colour_levels":cloth.colour})
                else:
                    add ShaderDisplayable(shader.MODE_2D, cloth.position_sets.get("stand1").images["Average_AA"].filename, shader.VS_2D,PS_COLOUR_SUB_LR2,{},uniforms={"colour_levels":cloth.colour})
                
screen outfit_delete_manager(the_wardrobe): ##Allows removal of outfits from players saved outfits. TODO: Expand this to general manager.
    add "Paper_Background.png"
    default preview_outfit = None
    vbox:
        for outfit in the_wardrobe.get_outfit_list():
            textbutton "Delete "+outfit.name+ " (Sluttiness " +str(outfit.slut_requirement) +")" action Function(the_wardrobe.remove_outfit,outfit) hovered SetScreenVariable("preview_outfit", copy.deepcopy(outfit)) unhovered SetScreenVariable("preview_outfit", None) style "textbutton_style" text_style "textbutton_text_style"
        
        textbutton "Return" action Return() style "textbutton_style" text_style "textbutton_text_style"
        
    fixed:
        pos (1500,0)
        add mannequin_average
        if preview_outfit:
            for cloth in sorted(preview_outfit.feet+preview_outfit.lower_body+preview_outfit.upper_body, key=lambda clothing: clothing.layer):
                if not cloth.is_extension:
                    if cloth.draws_breasts:
                        add ShaderDisplayable(shader.MODE_2D, cloth.position_sets.get("stand1").images["Average_D"].filename, shader.VS_2D,PS_COLOUR_SUB_LR2,{},uniforms={"colour_levels":cloth.colour})
                    else:
                        add ShaderDisplayable(shader.MODE_2D, cloth.position_sets.get("stand1").images["Average_AA"].filename, shader.VS_2D,PS_COLOUR_SUB_LR2,{},uniforms={"colour_levels":cloth.colour})
                    
screen outfit_select_manager(slut_limit = 999): ##Brings up a list of the players current saved outfits, returns the selected outfit or None.
    #If sluttiness_limit is passed, you cannot exit the creator until the proposed outfit has a sluttiness below it.
    add "Paper_Background.png"
    
    default preview_outfit = None
    vbox:
        for outfit in mc.designed_wardrobe.get_outfit_list():
            textbutton "Load "+outfit.name+ " (Sluttiness " +str(outfit.slut_requirement) +")" action Return(copy.deepcopy(outfit)) sensitive (outfit.slut_requirement <= slut_limit) hovered SetScreenVariable("preview_outfit", copy.deepcopy(outfit)) unhovered SetScreenVariable("preview_outfit", None) style "textbutton_style" text_style "textbutton_text_style"
            
        textbutton "Return" action Return("No Return") style "textbutton_style" text_style "textbutton_text_style"
        
    fixed:
        pos (1500,0)
        add mannequin_average
        if preview_outfit:
            for cloth in sorted(preview_outfit.feet+preview_outfit.lower_body+preview_outfit.upper_body, key=lambda clothing: clothing.layer):
                if not cloth.is_extension:
                    if cloth.draws_breasts:
                        add ShaderDisplayable(shader.MODE_2D, cloth.position_sets.get("stand1").images["Average_D"].filename, shader.VS_2D,PS_COLOUR_SUB_LR2,{},uniforms={"colour_levels":cloth.colour})
                    else:
                        add ShaderDisplayable(shader.MODE_2D, cloth.position_sets.get("stand1").images["Average_AA"].filename, shader.VS_2D,PS_COLOUR_SUB_LR2,{},uniforms={"colour_levels":cloth.colour})
                        
screen girl_outfit_select_manager(the_wardrobe): ##Brings up a list of outfits currently in a girls wardrobe.
    add "Paper_Background.png"
    default preview_outfit = None
    vbox:
        for outfit in the_wardrobe.get_outfit_list():
            textbutton "Delete "+outfit.name+ " (Sluttiness " +str(outfit.slut_requirement) +")" action Return(outfit) hovered SetScreenVariable("preview_outfit", copy.deepcopy(outfit)) unhovered SetScreenVariable("preview_outfit", None) style "textbutton_style" text_style "textbutton_text_style"
        
        textbutton "Return" action Return("None") style "textbutton_style" text_style "textbutton_text_style"
        
    fixed:
        pos (1500,0)
        add mannequin_average
        if preview_outfit:
            for cloth in sorted(preview_outfit.feet+preview_outfit.lower_body+preview_outfit.upper_body, key=lambda clothing: clothing.layer):
                if not cloth.is_extension:
                    if cloth.draws_breasts:
                        add ShaderDisplayable(shader.MODE_2D, cloth.position_sets.get("stand1").images["Average_D"].filename, shader.VS_2D,PS_COLOUR_SUB_LR2,{},uniforms={"colour_levels":cloth.colour})
                    else:
                        add ShaderDisplayable(shader.MODE_2D, cloth.position_sets.get("stand1").images["Average_AA"].filename, shader.VS_2D,PS_COLOUR_SUB_LR2,{},uniforms={"colour_levels":cloth.colour})

                        
screen map_manager():
    add "Paper_Background.png"
    for place in list_of_places: #Draw the background
        for connected in place.connections:
            add Vren_Line([int(place.map_pos[0]*1920),int(place.map_pos[1]*1080)],[int(connected.map_pos[0]*1920),int(connected.map_pos[1]*1080)],4,"#117bff") #Draw a white line between each location 
        
    for place in list_of_places: #Draw the text buttons over the background
        if not place == mc.location:
            frame:
                background None
                xysize [171,150] 
                anchor [0.0,0.0]
                align place.map_pos
                imagebutton:
                    anchor [0.5,0.5]
                    auto "gui/LR2_Hex_Button_%s.png"
                    focus_mask "gui/LR2_Hex_Button_idle.png"
                    action Function(mc.change_location,place) 
                    sensitive True #TODO: replace once we want limited travel again with: place in mc.location.connections
                text place.formalName + "\n(" + str(len(place.people)) + ")" anchor [0.5,0.5] style "map_text_style"

        else:
            frame:
                background None
                xysize [171,150]
                anchor [0.0,0.0]
                align place.map_pos
                imagebutton:
                    
                    anchor [0.5,0.5]
                    idle "gui/LR2_Hex_Button_Alt_idle.png"
                    focus_mask "gui/LR2_Hex_Button_Alt_idle.png"
                    action Function(mc.change_location,place) 
                    sensitive False 
                text place.formalName + "\n(" + str(len(place.people)) + ")" anchor [0.5,0.5] style "map_text_style" 
    
    frame:
        background None
        anchor [0.5,0.5]
        align [0.5,0.88]
        xysize [500,125]
        imagebutton:
            align [0.5,0.5]
            auto "gui/button/choice_%s_background.png"
            focus_mask "gui/button/choice_idle_background.png"
            action Return(mc.location)
        textbutton "Return" align [0.5,0.5] text_style "return_button_style"
        
init -2 python:
    def purchase_policy(the_policy):
        mc.business.funds -= the_policy.cost
        mc.business.policy_list.append(the_policy)
        
init -2 screen policy_selection_screen():
    add "Paper_Background.png"
    modal True
    $ tooltip = GetTooltip()
    vbox:
        xalign 0.1
        yalign 0.1
        for policy in policies_list:
            if policy.is_owned():
                textbutton policy.name +" - $" +str(policy.cost):
                    tooltip policy.desc
                    action NullAction()
                    style "textbutton_style"
                    text_style "textbutton_text_style"
                    background "#59853f"
                    hover_background "#78b156"
                    sensitive True
            else:
                if policy.requirement() and (policy.cost < mc.business.funds or policy.cost == mc.business.funds):
                    textbutton policy.name +" - $" +str(policy.cost):
                        tooltip policy.desc
                        style "textbutton_style"
                        text_style "textbutton_text_style"
                        action Function(purchase_policy,policy)
                        sensitive policy.requirement() and (policy.cost < mc.business.funds or policy.cost == mc.business.funds)
                else:
                    textbutton policy.name +" - $" +str(policy.cost):
                        tooltip policy.desc
                        style "textbutton_style"
                        text_style "textbutton_text_style"
                        background "#666666"
                        action NullAction()
                        sensitive True
                

    if tooltip:
        frame:
            background None
            anchor [1.0,0.0]
            align [0.9,0.1]
            xysize [500,500]
            text tooltip style "menu_text_style"
            
    frame:
        background None
        anchor [0.5,0.5]
        align [0.5,0.88]
        xysize [500,125]
        imagebutton:
            align [0.5,0.5]
            auto "gui/button/choice_%s_background.png"
            focus_mask "gui/button/choice_idle_background.png"
            action Return()
        textbutton "Return" align [0.5,0.5] text_style "return_button_style"
    
        
init -2 style return_button_style:
    text_align 0.5
    size 30
    italic True
    bold True
    color "#dddddd"
    outlines [(2,"#222222",0,0)]
        
init -2 style map_text_style:
    text_align 0.5
    size 14
    italic True
    bold True
    color "#dddddd"
    outlines [(2,"#222222",0,0)]
    
init -2 style map_frame_style:
    background "#094691"
    
init -2 style map_frame_blue_style:
    background "#5fa7ff"
    
init -2 style map_frame_grey_style:
    background "#222222"
    
transform float_up:
    xalign 0.92
    yalign 1.0
    alpha 1.0
    ease 1.0 yalign 0.4
    linear 2.0 alpha 0.0
    
style float_text:
    size 30
    italic True
    bold True
    outlines [(2,"#222222",0,0)] 
    
style float_text_pink is float_text:
    color "#FFB6C1"
    
style float_text_red is float_text:
    color "B22222"
    
style float_text_grey is float_text:
    color "696969"
    
style float_text_green is float_text:
    color "228B22"
    
style float_text_yellow is float_text:
    color "D2691E"
    
style float_text_blue is float_text:
    color "483D8B"
    
screen float_up_screen (text_array, style_array): #text_array is a list of the text to be displayed on each line, style_array is the list of corisponding styles to be used for that text.
    vbox at float_up:
        xanchor 0.5
        for index, update_text in enumerate(text_array):
            text update_text style style_array[index]
    timer 3.0 action Hide("float_up_screen") #Hide this screen after 3 seconds, so it can be called again by something else.

label start:
    scene bg paper_menu_background with fade
    "Lab Rats 2 contains adult content. If you are not over 18 or your contries equivalent age you should not view this content."
    menu:
        "I am over 18.":
            "Excellent, let's continue then."
            
        "I am not over 18.":
            $renpy.full_restart()

    "Vren" "v0.3 represents an early iteration of Lab Rats 2. Expect to run into limited content, unexplained features, and unbalanced game mechanics."
    "Vren" "Would you like to view the FAQ?"
    menu:
        "View the FAQ.":
            call faq_loop from _call_faq_loop
        "Get on with the game!":
            "You can access the FAQ from your bedroom at any time."
    $ renpy.block_rollback() 
    call screen character_create_screen()
    $ renpy.block_rollback()
    $ return_arrays = _return #These are the stat, skill, and sex arrays returned from the character creator.
    call create_test_variables(store.name,store.b_name,return_arrays[0],return_arrays[1],return_arrays[2]) from _call_create_test_variables ##Moving some of this to an init block (init 1 specifically) would let this play better with updates in the future.
            
    "You have recently graduated from university, after completing your degree in chemical engineering. You've moved away from home, closer to the industrial district of the city to be close to any potential engineering jobs."
    "While the job search didn't turn up any paying positions, it did lead you to a bank posting for an old pharmaceutical lab. The bank must have needed money quick, because they were practically giving it away."
    "Without any time to consider the consequences you bought the lab. It came stocked with all of the standard equipment you would expect, and after a few days of cleaning you're ready to get to work."
    "A lab is nothing without it's product though, and you have just the thing in mind. You still remember the basics for the mind altering serum you produced in university."
    "With a little work in your new research and development lab you think you could recreate the formula completely, or even improve on it. Hiring some help would improve your research and production speeds."
    "You yawn and stretch as you greet the dawn early in the morning. Today feels like the start of a brand new chapter in your life!"
    ## For now, this ensures reloadin the game doesn't reset any of the variables.
    $ renpy.show
    show screen main_ui
    show screen business_ui
    $ renpy.show(bedroom.name,what=bedroom.background_image) #show the bedroom background as our starting point.
    call examine_room(mc.location) from _call_examine_room
    jump game_loop
    
label faq_loop:
    menu:
        "Gameplay Basics.":
            menu:
                "Making Serum.":
                    "Vren" "Making serum in your lab is the most important task for success in Lab Rats 2. You begin the game with a fully equipt lab."
                    "Vren" "The first step to make a serum is to design it in your lab. The most basic serum design can be made without any additions, but most will be made by adding serum traits."
                    "Vren" "Serum traits modify the effects of a serum. The effects can be simple - increasing duration or Suggestion increase - or it may be much more complicated."
                    "Vren" "Once you have decided on the traits you wish to include in your serum you will have to spend time in the lab researching it. Place it in the research queue and spend a few hours working in the lab."
                    "Vren" "More complicated serums will take more time to research. Once the serum is completely researched it can be produced by your production division. Move over their and slot it into the current production queue."
                    "Vren" "Before you can produce the serum you will need raw supplies. One unit of supply is needed for every production point the serum requires. You can order supply from your main office."
                    "Vren" "Once you have supplies you can spend time in your production lab. After some number of hours you will find a dose, or several, in your companies inventory!"
                    "Vren" "You can either take this serum for your own personal use, or you can head to the main office and mark it for sale. Once a serum is marked for sale you can spend time in your marketting division to find a buyer."
                    "Vren" "Your research and development lab can also spend time researching new traits for serum instead of producing new serum designs. You slot these into your research queue in the same way you do a new serum design."
                    
                "Hiring Staff.":
                    "Vren" "While you can do all the necessary tasks for your company yourself, that isn't how you're going to make it big. Hiring employees will let you spend you grow your business and pull in more and more money."
                    "Vren" "To hire someone, head over to your main office. From there you can request a trio of resumes to choose from, for a small cost. The stats of the three candidates will be chosen, and you can choose who to hire."
                    "Vren" "The three primary stats - Charisma, Intelligence, and Focus - are the most important traits for a character. Each affects the jobs in your company differently."
                    "Vren" "Charisma is the primary stat for marketing and human resources, as well as being a secondary stat for purchasing supplies."
                    "Vren" "Intelligence is the primary stat for research, as well as a secondary stat for human resources and production."
                    "Vren" "Focus is the primary stat for supply procurement and production, as well as a secondary stat for research."
                    "Vren" "Each character will also have an expected salary, to be paid each day. Higher stats will result in a more expensive employee, so consider hiring specialists rather than generalists."
                    "Vren" "Your staff will come into work each morning and perform their appropriate tasks, freeing up your time for other pursuits..."
                    
                "Corrupting People.":
                    "Vren" "You may be wondering what you can do with all this serum you produce. The main use of serum is to increase the Suggestability statistic of another character."
                    "Vren" "While a character has a Suggestability value of 0 nothing you do will have a long lasting effect on their personality. Once Suggestability is raised, their personality will change in response to your actions."
                    "Vren" "Interacting with a character may change their Obedience or Sluttiness. The most direct way to do that is to have sex with them. As a characters Sluttiness score increases the farther she will be willing to go with you."
                    "Vren" "When you finish having sex with a girl you will change her Sluttiness, modified by her current Suggestability. The higher her arousal, the larger the change in Sluttiness."
                    "Vren" "As Sluttiness increases a character will also be more willing to wear revealing clothing, or nothing at all. Design an outfit using the outfit manager in the top left, then interact with the character and ask them to wear it."
                                        
        "Development Questions.":
            menu:
                "Are the Lab Rats 1 Characters in the game?":
                    "Vren" "Not yet, but they will be added. As the options available to me in the character creator improve they will be added, and their personality will be written into the game."
                    "Vren" "Lab Rats 2 assumes an imperfect end to it's prequel, where the main character realises the potential of the serum but fails to take advantage of it over the summer."
                    "Vren" "There will also be the option to import a saved game from Lab Rats 1, letting you start off with familiar characters that have higher Sluttiness or Obedience stats."
                    
                "Will there be more character poses?":
                    "Vren" "Absolutely! The current standing poses proved that the rendering workflow for the game is valid, which means I will be able to introduce character poses for different sex positions."
                    "Vren" "Doggy style is currently the only sex position with a unique character pose associated with it, it gives a good taste of what will be possible in the future."
                    
                "Will there be animation?":
                    "Vren" "No, there will not be full animation in the game. There may be small sprite based animations added later, but this will require more experimentation by me before I can commit to it."
                    
                "Why are their holes in some pieces of clothing?":
                    "Vren" "Some character positions cause portions of the character model to poke out of their clothing when I am rendering them."
                    "Vren" "I will be adjusting my render settings and rerendering any clothing items that need it as we go forward."
                    
                "Why do all of the characters have the same face?":
                    "Vren" "All of the current character faces use the same base render, which means they all end up looking the same."
                    "Vren" "I have finished improvements to my rendering automation which will let me generate a different set of faces; expect to see more variation in future versions."
                    
                "Why do names repeat so often?":
                    "Vren" "Patrons have the ability to suggest new names for the name pool each month. This process has just started, so there are only a small collection of names in the game for now."
                 
        "Done.":
            return
    call faq_loop from _call_faq_loop_1
    return
    
label check_inventory_loop:
    call screen show_serum_inventory(mc.inventory)
    return
    
label check_business_inventory_loop:
    call screen show_serum_inventory(mc.business.inventory)
    return
    
label outfit_design_loop:
    menu:
        "Create a new outfit.":
            call create_outfit(None) from _call_create_outfit
            
        "Load an old outfit." if mc.designed_wardrobe.get_count() > 0:   
            call screen outfit_select_manager()
            if not _return == "No Return":
                call create_outfit(_return) from _call_create_outfit_1
            
        "Delete an old outfit." if mc.designed_wardrobe.get_count() > 0:
            call screen outfit_delete_manager(mc.designed_wardrobe)
    return
            
    
label create_outfit(the_outfit):
    if the_outfit is None:
        call screen outfit_creator(Outfit("New Outfit"))
    else:
        call screen outfit_creator(the_outfit)
    $ new_outfit = _return
    if not new_outfit == "Not_New": ##Only try and save the outfit if there was actually a new outfit made
        $ new_outfit_name = renpy.input ("Please name this outfit.")
        while new_outfit_name is None:
            $ new_outfit_name = renpy.input ("Please name this outfit.")
        if mc.designed_wardrobe.has_outfit_with_name(new_outfit_name):
            "An outfit with this name already exists. Would you like to overwrite it?"
            menu:
                "Overwrite existing outfit.":
                    $ mc.designed_wardrobe.remove_outfit(mc.designed_wardrobe.get_outfit_with_name(new_outfit_name))
                    $ mc.save_design(new_outfit, new_outfit_name)
                    
                "Rename outfit.":
                    $ new_outfit_name = renpy.input ("Please input a new name.")
                    while mc.designed_wardrobe.has_outfit_with_name(new_outfit_name):
                        $ new_outfit_name = renpy.input ("That name already exists. Please input a new name.")
                    $ mc.save_design(new_outfit, new_outfit_name)
        else:
            $ mc.save_design(new_outfit, new_outfit_name)
    return
    
label game_loop: ##THIS IS THE IMPORTANT SECTION WHERE YOU DECIDE WHAT ACTIONS YOU TAKE
    #"Now, what would you like to do? You can talk to someone, go somewhere else, perform an action, or reexamine the room."
    python:
        tuple_list = [("Go somewhere else.", "Go somewhere else."), ("Examine the room.", "Examine the room.")]
        act_ct = mc.location.valid_actions()
        if act_ct < 5:
            for act in mc.location.actions:
                if act.check_requirement():
                    tuple_list.append((act.name,act))
        else:
            tuple_list.append(("Do something.", "Do something."))

        pers_ct = len(mc.location.people)
        if pers_ct < 5:
            for people in mc.location.people:
                tuple_list.append(("Talk to " + people.name + " " + people.last_name[0] + ".",people))
        else:
            tuple_list.append(("Talk to someone.", "Talk to someone."))

        choice = renpy.display_menu(tuple_list,True,"Choice")

    if isinstance(choice, basestring):
        if choice == "Go somewhere else.":
            call screen map_manager
            call change_location(_return) from _call_change_location #_return is the location returned from the map manager.

        elif choice == "Examine the room.":
            call examine_room(mc.location) from _call_examine_room_1

        elif choice == "Do something.":
            python:
                i = 0
                while not isinstance(choice, Action) and choice != "Back":
                    tuple_list = [(act.name,act) for act in mc.location.actions[i:i+9]]
                    if act_ct > i+10:
                        tuple_list.append(("Something else", "Something else"))
                        i += 9
                    elif act_ct == i+10:
                        act = mc.location.actions[i+9]
                        tuple_list.append((act.name,act))
                    tuple_list.append(("Back", "Back"))
                    choice = renpy.display_menu(tuple_list,True, "Choice")

        elif choice == "Talk to someone.":
            python:
                i = 0
                while not isinstance(choice, Person) and choice != "Back":
                    tuple_list = [(p.name + " " + p.last_name[0] + ".", p) for p in mc.location.people[i:i+9]]
                    if pers_ct > i+10:
                        tuple_list.append(("Someone else", "Someone else"))
                        i += 9
                    elif pers_ct == i+10:
                        people = mc.location.people[i+9]
                        tuple_list.append((people.name + " " + people.last_name[0] + ".",people))
                    tuple_list.append(("Back", "Back"))
                    choice = renpy.display_menu(tuple_list,True, "Choice")

    if isinstance(choice, Person):
        "You approach [choice.name] and chat for a little bit."
        $ choice.call_greeting()
        call talk_person(choice) from _call_talk_person

    elif isinstance(choice, Action):
        $ choice.call_action()

    jump game_loop
    

        
label change_location(the_place):
    $ renpy.scene()
    $ renpy.show(the_place.name,what=the_place.background_image)
#    "You spend some time travelling to [the_place.name]." #TODO: Only show this when there is a significant time use? Otherwise takes up too much time changing between locations.
    return

label talk_person(the_person, repeat_choice = None):
    $the_person.draw_person()
    show screen person_info_ui(the_person)
    hide screen business_ui

    menu:
        "Finish talking.":
            $ repeat_choice = None
            "Eventually you're done say goodbye to each other."
        "Repeat" if repeat_choice:
            # print the repeat choice and then replace characters so it can be called as a label
            "You [repeat_choice]"
            $ renpy.call(re.sub(' ', '_', repeat_choice))

        "Chat about something.":
            $ repeat_choice = None
            menu:
                "Compliment her outfit.":
                    $ repeat_choice = "compliment her outfit"
                    call compliment_her_outfit from chat_compliment_outfit
                "Flirt with her.":
                    $ repeat_choice = "flirt with her"
                    call flirt_with_her  from chat_flirt
                "Compliment her recent work." if mc.business.get_employee_workstation(the_person):
                    $ repeat_choice = "compliment her recent work"
                    call compliment_her_recent_work  from chat_compliment_work
                "Insult her recent work." if mc.business.get_employee_workstation(the_person):
                    $ repeat_choice = "insult her recent work"
                    call insult_her_recent_work  from chat_insult

                "Offer a cash bonus." if  mc.business.get_employee_workstation(the_person) and 0 < time_of_day < 4:
                    mc.name "So [the_person.name], you've been putting in a lot of good work at the lab lately and I wanted to make sure you were rewarded properly for that."
                    "You pull out your wallet and start to pull out a few bills."
                    $weeks_wages = the_person.salary*5
                    $months_wages = the_person.salary*20
                    $raise_amount = int(the_person.salary*0.1)
                    menu:
                        "Give her a pat on the back.":
                            mc.name "And I'll absolutely reward you once the next major deal goes through."
                            $ the_person.draw_person(emotion = "sad")
                            $ change_amount = 5-mc.charisma
                            show screen float_up_screen(["-[change_amount] Happiness"],["float_text_yellow"])
                            $the_person.change_happiness(-change_amount)
                            "[the_person.name] looks visibly disapointed."
                            the_person.name "Right, of course."

                        "Give her a days wages. -$[the_person.salary]" if mc.money >= the_person.salary:
                            mc.name "Here you go, treat yourself to something nice tonight."
                            $ the_person.draw_person(emotion = "happy")
                            $ change_amount = 1+mc.charisma
                            show screen float_up_screen(["+[change_amount] Happiness"],["float_text_yellow"])
                            $ the_person.change_happiness(change_amount)
                            $ mc.money -= the_person.salary
                            "[the_person.name] takes the bills from you and smiles."
                            the_person.name "Thank you sir."

                        "Give her a weeks wages. -$[weeks_wages]" if mc.money >= weeks_wages:
                            mc.name "Here you go, don't spend it all in once place."
                            $ the_person.draw_person(emotion = "happy")
                            $ change_amount = 1+mc.charisma
                            $ change_amount_happiness = 5+mc.charisma
                            $ the_person.change_happiness(change_amount_happiness)
                            $ the_person.change_obedience_modified(change_amount)
                            $ mc.money -= weeks_wages
                            show screen float_up_screen(["+[change_amount] Happiness","+[change_amount] Obedience"],["float_text_yellow","float_text_grey"])
                            "[the_person.name] takes the bills, then smiles broadly at you."
                            the_person.name "That's very generous of you sir, thank you."

                        "Give her a months wages. -$[months_wages]" if mc.money >= months_wages:
                            mc.name "Here, you're a key part of the team and you deserved to be rewarded as such."
                            $ the_person.draw_person(emotion = "happy")
                            $ change_amount = 5+mc.charisma
                            $ change_amount_happiness = 10+mc.charisma
                            $ mc.money -= months_wages
                            $the_person.change_happiness(change_amount_happiness)
                            $the_person.change_obedience_modified(change_amount)
                            "[the_person.name] takes the bills, momentarily stunned by the amount."
                            show screen float_up_screen(["+[change_amount] Happiness","+[change_amount] Obedience"],["float_text_yellow","float_text_grey"])
                            if the_person.sluttiness > 40 and the_person.happiness > 100:
                                the_person.name "Wow... this is amazing sir. I'm sure there's something I can do to pay you back, right?"
                                "She steps close to you and runs a finger down your chest."
                                call fuck_person(the_person) from _call_fuck_person_3  #TODO: add a temporary obedience and sluttiness modifier to the function to allow for modifiers during situations like this (and firing her)
                                #Now that you've had sex, we calculate the change to her stats and move on.
                                $ change_amount = the_person.change_slut_modified(the_person.arousal) #Change her slut score by her final arousal. This should be _about_ 100 if she climaxed, but you may keep fucking her silly if you can overcome the arousal loss.
                                show screen float_up_screen(["+[change_amount] Sluttiness"],["float_text_pink"])
                                $ the_person.reset_arousal()
                                $ the_person.review_outfit()
                            else:
                                the_person.name "Wow... this is amazing sir. I'll do everything I can for you and the company!"

                        "Give her a permanent 10%% Raise ($[raise_amount]/day)":
                            mc.name "[the_person.name], it's criminal that I pay you as little as I do. I'm going to mark you down for a 10%% raise, effective by the end of today."
                            $ change_amount = 5+mc.charisma
                            $ change_amount_happiness = 10+mc.charisma
                            $ the_person.change_happiness(change_amount_happiness)
                            $ change_amount_obedience = the_person.change_obedience_modified(change_amount)
                            show screen float_up_screen(["+$[raise_amount]/day Salary","+[change_amount] Happiness","+[change_amount_obedience] Obedience"],["float_text_green","float_text_yellow","float_text_grey"])
                            $ the_person.salary += raise_amount
                            the_person.name "Thank you sir, that's very generous of you!"

                    call talk_person(the_person) from _call_talk_person_4

        "Modify her wardrobe." if the_person.obedience >= 120:
            $ repeat_choice = None
            menu:
                "Add an outfit.":
                    mc.name "[the_person.name], I've got something I'd like you to wear for me." ## Do we want a completely silent protag? Speaks only through menu input maybe?
                    hide screen main_ui
                    $ renpy.scene("Active")
                    call screen outfit_select_manager()
                    show screen main_ui
                    $ the_person.draw_person()
                    if not _return == "No Return":
                        $ new_outfit = _return
                        if new_outfit.slut_requirement > the_person.sluttiness:
                            $ the_person.call_clothing_reject()
                        else:
                            $ the_person.add_outfit(new_outfit)
                            $ the_person.call_clothing_accept()
                            the_person.name "Would you like me to wear it now?" ##TODO: Only have them ask this question if their devotion is a certain level
                            menu:
                                "Yes, wear it now.":
                                    $ the_person.set_outfit(new_outfit)
                                    $ renpy.scene("Active") ## Clear the persons image
                                    $ the_person.draw_person() ## And redraw it now that they're in a new outfit
                                "No, save it for some other time.":
                                    pass
                    else:
                        mc.name "On second thought, nevermind."
                        
                "Delete an outfit.":
                    mc.name "[the_person.name], lets have a talk about what you've been wearing."
                    hide screen main_ui
                    $ renpy.scene("Active")
                    call screen outfit_delete_manager(the_person.wardrobe)
                    show screen main_ui
                    $ the_person.draw_person()
                    #TODO: Figure out what happens when someone doesn't have anything in their wardrobe.
                
                "Wear an outfit right now.":
                    mc.name "[the_person.name], I want you to get changed for me."
                    hide screen main_ui
                    $ renpy.scene("Active")
                    call screen girl_outfit_select_manager(the_person.wardrobe)
                    if _return != "None":
                        $ the_person.set_outfit(_return)
                    
                    $ the_person.draw_person()
                    show screen main_ui
                    the_person.name "Is this better?"
            call talk_person(the_person) from _call_talk_person_1
            
        "Move her to a new division." if not mc.business.get_employee_title(the_person) == "None" and 0 < time_of_day < 4:
            $ repeat_choice = None
            the_person.name "Where would you like me then?"
            $ mc.business.remove_employee(the_person)
            
            if rd_division.has_person(the_person):
                $ rd_division.remove_person(the_person)
            elif p_division.has_person(the_person):
                $ p_division.remove_person(the_person)
            elif office.has_person(the_person):
                $ office.remove_person(the_person)
            elif m_division.has_person(the_person):
                $ m_division.remove_person(the_person)
            menu:
                "Research and Development.":
                    $ mc.business.add_employee_research(the_person)
                    $ rd_division.add_person(the_person)
                
                "Production.":
                    $ mc.business.add_employee_production(the_person)
                    $ p_division.add_person(the_person)
                    
                "Supply Procurement.":
                    $ mc.business.add_employee_supply(the_person)
                    $ office.add_person(the_person)
                    
                "Marketing.":
                    $ mc.business.add_employee_marketing(the_person)
                    $ m_division.add_person(the_person)
                    
                "Human Resources.":
                    $ mc.business.add_employee_hr(the_person)
                    $ office.add_person(the_person)
            
            the_person.name "I'll get started right away!"
            
        "Fire them!" if not mc.business.get_employee_title(the_person) == "None" and 0 < time_of_day < 4:
            $ repeat_choice = None
            "You tell [the_person.name] to collect their things and leave the building."
            $ mc.business.remove_employee(the_person) #TODO: check if we should actually be physically removing the person from the location without putting them somewhere else (person leak?)
            if rd_division.has_person(the_person):
                $ rd_division.remove_person(the_person)
            elif p_division.has_person(the_person):
                $ p_division.remove_person(the_person)
            elif office.has_person(the_person):
                $ office.remove_person(the_person)
            elif m_division.has_person(the_person):
                $ m_division.remove_person(the_person)
            
        "Take a closer look at [the_person.name].":
            $ repeat_choice = None
            call examine_person(the_person) from _call_examine_person
            call talk_person(the_person) from _call_talk_person_2
        "Give her a dose of serum." if mc.inventory.get_any_serum_count() > 0 and mandatory_serum_testing_policy.is_owned():
            $ repeat_choice = "give her a dose of serum"
            call give_her_a_dose_of_serum
        "Seduce her.":
            $ repeat_choice = None
            call seduce_her from chat_seduce
    if repeat_choice:
        call talk_person(the_person, repeat_choice) from _call_talk_person_3
    hide screen person_info_ui
    show screen business_ui
    $renpy.scene("Active")
    return

label compliment_her_outfit:
    mc.name "Hey [the_person.name], I just wanted to say that you look great today. That style really suits you." #TODO: Add more context aware dialogue.
    $ slut_difference = int(the_person.sluttiness - the_person.outfit.slut_requirement) #Negative if their outfit is sluttier than what they would normally wear.
    # Note: The largest effect should occure when the outfit is just barely in line with her sluttiness. Too high or too low and it will have no effect.

    $ sweet_spot_range = 10
    if slut_difference < -sweet_spot_range : #Outfit is too slutty, she will never get use to wearing it.
        $ the_person.draw_person(emotion = "default")
        the_person.name "Really? It's just so revealing, what do people think of me when they see me? I don't think I'll ever get use to wearing this."

    elif slut_difference > sweet_spot_range:  #Outfit is conservative, no increase.
        $ the_person.draw_person(emotion = "default")
        the_person.name "Really? I think it looks too bland, showing a little more skin would be nice."

    else: #We are within the sweet_spot_range with the outfit.
        $ slut_difference = math.fabs(slut_difference)
        if slut_difference > sweet_spot_range:
            $ slut_difference = sweet_spot_range
        $ slut_difference = sweet_spot_range - slut_difference #invert the value so we now have 10 - 10 at both extreme ends, 10 - 0 at the middle where it will have the most effect.
        $ change_amount = the_person.change_slut_modified(mc.charisma + 1 + slut_difference) #Increase their sluttiness if they are suggestable right now.
        show screen float_up_screen(["+[change_amount] Sluttiness"],["float_text_pink"])
        the_person.name "Glad you think so, I was on the fence, but it's nice to know that somebody likes it!"
    return

label flirt_with_her:
    mc.name "Hey [the_person.name], you're looking particularly good today. I wish I got to see a little bit more of that fabulous body."
    $ change_amount = the_person.change_slut_modified(mc.charisma + 1)
    show screen float_up_screen(["+[change_amount] Sluttiness"],["float_text_pink"])
    $the_person.call_flirt_response()
    return

label compliment_her_recent_work:
    mc.name "[the_person.name], I wanted to tell you that you've been doing a great job lately. Keep it up, you're one of hte most important players in this whole operation."
    $ change_amount = mc.charisma + 1
    $ change_amount_obedience = the_person.change_obedience_modified(-change_amount)
    $ the_person.change_happiness(change_amount)
    $ the_person.draw_person(emotion = "happy")
    show screen float_up_screen(["+[change_amount] Happiness","[change_amount_obedience] Obedience"],["float_text_yellow","float_text_grey"])
    the_person.name "Thanks [mc.name], it means a lot to hear that from you. I'll just keep doing what I'm doing I guess."
    return

label insult_her_recent_work:
    mc.name "[the_person.name], I have to say I've been disappointed in your work for a little while now. Try to shape up, or we'll have to have a more offical talk about it."
    $ change_amount = mc.charisma*2 + 1
    $ change_amount_happiness = 5-mc.charisma
    $ change_amount= the_person.change_obedience_modified(change_amount)
    $ the_person.change_happiness(-change_amount_happiness)
    $ the_person.draw_person(emotion = "sad")
    show screen float_up_screen(["-[change_amount_happiness] Happiness","+[change_amount] Obedience"],["float_text_yellow","float_text_grey"])
    the_person.name "Oh... I didn't know there was an issue. I'll try follow your instructions closer then."
    return

label give_her_a_dose_of_serum:
    $renpy.scene("Active")
    call give_serum(the_person) from _call_give_serum
    return

label seduce_her:
    "You step close to [the_person.name] and hold her hand."
    $ the_person.call_seduction_response()
    call fuck_person(the_person) from _call_fuck_person
    #Now that you've had sex, we calculate the change to her stats and move on.
    $ change_amount = the_person.change_slut_modified(the_person.arousal) #Change her slut score by her final arousal. This should be _about_ 100 if she climaxed, but you may keep fucking her silly if you can overcome the arousal loss.
    show screen float_up_screen(["+[change_amount] Sluttiness"],["float_text_pink"])
    $ the_person.reset_arousal()
    $ the_person.review_outfit()
    return

label fuck_person(the_person): #TODO: Add a conditional obedience and sluttiness increase for situations like blackmail or getting drunk
    python:
        tuple_list = []
        for position in list_of_positions:
            if mc.location.has_object_with_trait(position.requires_location) and position.check_clothing(the_person):
                tuple_list.append([position.name,position])
        tuple_list.append(["Leave","Leave"]) #Stop having sex, since cumming is now a locked in thing.
        #TODO: What if there are no options. Should there always be a standing option? Add positions with "None" requirement.
        position_choice = renpy.display_menu(tuple_list,True,"Choice")
        
    if not position_choice == "Leave":
        python:
            tuple_list = []
            for object in mc.location.objects:
                if object.has_trait(position_choice.requires_location):
                    tuple_list.append((object.name,object))
            if len(tuple_list) > 1:
                renpy.say("","Where do you do it?")
                object_choice = renpy.display_menu(tuple_list,True,"Choice")
            else:
                renpy.say("", "You decide to do it on the %s."%tuple_list[0][0])
                object_choice = tuple_list[0][1]
            
        call sex_description(the_person, position_choice, object_choice, 0) from _call_sex_description
    
    return
    
label sex_description(the_person, the_position, the_object, round): ##TODO: Refactor this into one long python section. It's a mutant hybrid right now for no good reason.
    
    ##Describe the current round
    $ the_person.draw_person(the_position.position_tag)
    
    ## FIRST ROUND EXCLUSIVE STUFF ##
    if round == 0: ##First round means you just started, so do intro stuff before we get on with it. Also where we check to see if they are into having this type of sex.
        if the_person.effective_sluttiness() >= the_position.slut_requirement: #The person is slutty enough to want to have sex like this.
            $ the_person.call_sex_accept_response()
            $ the_position.call_intro(the_person, mc.location, the_object, round)
        else: #The person isn't slutty enough for this. First, try and use obedience. If you still fail, but by a little, she rebukes you but you keep seducing her. Otherwise, the entire thing ends.
            if the_person.effective_sluttiness() + (the_person.obedience-100) >= the_position.slut_requirement:
                #You can use obedience to do it.
                $ the_person.draw_person(the_position.position_tag,emotion="sad")
                $ change_amount = the_position.slut_requirement - the_person.sluttiness
                show screen float_up_screen(["-[change_amount] Happiness"],["float_text_yellow"])
                $ the_person.call_sex_obedience_accept_response()
                $ the_person.change_happiness(-change_amount) #She looses happiness equal to the difference between her sluttiness and the requirement. ie the amount obedience covered.
                $ the_position.call_intro(the_person, mc.location, the_object, round)
            else:
                #No amount of obedience will help here. How badly did you screw up?
                if the_person.effective_sluttiness() < the_position.slut_requirement/2: #Badly, not even half way to what you needed
                    $ the_person.draw_person(the_position.position_tag,emotion="angry")
                    show screen float_up_screen(["-5 Happiness"],["float_text_yellow"])
                    $ the_person.change_happiness(-5) #She's pissed you would even try that
                    $ the_person.call_sex_angry_reject()
                    return #Don't do anything else, just return.
                else:
                    $ the_person.call_sex_gentle_reject()
                    call fuck_person(the_person) from _call_fuck_person_1 #Gives you a chance to fuck them some other way, but this path is ended by the return right after you finish having sex like that.
                    return
    
    ## ONCE WE HAVE DONE FIRST ROUND CHECKS WE GO HERE ##
    $ the_position.call_scene(the_person, mc.location, the_object, round)
    
    $ change_amount = the_position.girl_arousal + (the_position.girl_arousal * mc.sex_skills[the_position.skill_tag] * 0.1)
    show screen float_up_screen(["+[change_amount] Arousal"],["float_text_red"])
    $ the_person.change_arousal(change_amount) #The girls arousal gain is the base gain + 10% per the characters skill in that category.
    $ mc.change_arousal(the_position.guy_arousal + (the_position.guy_arousal * the_person.sex_skills[the_position.skill_tag] * 0.1)) # The same calculation but for the guy
    
    ## POST ROUND CALCULATION AND DECISIONS PAST HERE ##
    
    if the_person.arousal >= 100:
        #She's climaxing.
        $the_person.call_climax_response()
        $the_person.draw_person(the_position.position_tag,emotion="orgasm")
        show screen float_up_screen(["+5 Happiness"],["float_text_yellow"])
        $the_person.change_happiness(5) #Orgasms are good, right?
    else:
        $the_person.call_sex_response()
    
    ##Ask how you want to keep fucking her##
    $ position_choice = "Keep Going" #Default value just to make sure scope is correct.
    python:
        if (mc.arousal >= 100):
            "You're past your limit, you have no choice but to cum!"
            position_choice = "Finish"
        else:
            tuple_list = []
            tuple_list.append(["Keep going some more.",the_position])
            tuple_list.append(["Back off and change positions.","Pull Out"])
            if (mc.arousal > 80): #Only let you finish if you've got a high enough arousal score. #TODO: Add stat that controls how much control you have over this.
                tuple_list.append(["Cum!","Finish"]) 
            tuple_list.append(["Strip her down.","Strip"])
            for position in the_position.connections: 
                if the_object.has_trait(position.requires_location) and position.check_clothing(the_person):
                    appended_name = "Change to " + position.name + "."
                    tuple_list.append([appended_name,position])
            position_choice = renpy.display_menu(tuple_list,True,"Choice")
    
    if position_choice == "Finish":
        $ the_position.call_outro(the_person, mc.location, the_object, round)
        $ mc.reset_arousal()
        # TODO: have you finishing bump her arousal up so you might both cum at once.
        
    elif position_choice == "Strip":
        call strip_menu(the_person) from _call_strip_menu
        call sex_description(the_person, the_position, the_object, round+1) from _call_sex_description_1
        
    elif position_choice == "Pull Out": #Also how you leave if you don't want to fuck till you cum.
        call fuck_person(the_person) from _call_fuck_person_2
        
    else:
        #TODO: Clean up the code for arousal and slutiness interactions. Add an "effective slutiness" 
        if not position_choice == the_position: #We are changing to a new position.
            if the_person.effective_sluttiness() >= position_choice.slut_requirement: #The person is slutty enough to want to have sex like this. Higher arousal can get you up to a +50 slutiness boost.
                $ the_person.call_sex_accept_response()
                $ the_position.call_transition(position_choice, the_person, mc.location, the_object, round)
            else: #The person isn't slutty enough for this. First, try and use obedience. If you still fail, but by a little, she rebukes you but you keep seducing her. Otherwise, the entire thing ends.
                if the_person.effective_sluttiness() + (the_person.obedience-100) >= position_choice.slut_requirement:
                    #You can use obedience to do it.
                    $ change_amount = the_person.effective_sluttiness() - the_person.sluttiness
                    $ the_person.draw_person(the_position.position_tag,emotion = "sad")
                    $ the_person.change_happiness(-change_amount) #She looses happiness equal to the difference between her sluttiness and the requirement. ie the amount obedience covered.
                    show screen float_up_screen(["-[change_amount] Happiness"],["float_text_yellow"])
                    $ the_person.call_sex_obedience_accept_response()
                    $ the_position.call_transition(position_choice, the_person, mc.location, the_object, round)
                else:
                    #No amount of obedience will help here. How badly did you screw up?
                    if (the_person.effective_sluttiness() < (position_choice.slut_requirement/2)): #Badly, not even half way to what you needed
                        show screen float_up_screen(["-5 Happiness"],["float_text_yellow"])
                        $ the_person.change_happiness(-5) #She's pissed you would even try that
                        $ the_person.call_sex_angry_reject()
                        return #Don't do anything else, just return.
                    else:
                        $ the_position.call_transition(position_choice, the_person, mc.location, the_object, round)
                        $ the_person.call_sex_gentle_reject()
                        $ position_choice.call_transition(the_position, the_person, mc.location, the_object, round)
                        $ position_choice = the_position
                        
        call sex_description(the_person, position_choice, the_object, round+1) from _call_sex_description_2
                        
    return
    
label strip_menu(the_person):
    python:
        second_tuple_list = []
        for clothing in the_person.outfit.get_unanchored():
            if not clothing.is_extension: #Extension clothing is placeholder for multi-slot items like dresses.
                second_tuple_list.append(["Take off " + clothing.name + ".",clothing])
        second_tuple_list.append(["Go back to fucking her.","Finish"])
        strip_choice = renpy.display_menu(second_tuple_list,True,"Choice")
        
        if not strip_choice == "Finish":
            test_outfit = copy.deepcopy(the_person.outfit)
            test_outfit.remove_clothing(strip_choice)
            if the_person.judge_outfit(test_outfit):
                the_person.outfit.remove_clothing(strip_choice)
                the_person.draw_person()
                renpy.say("", "You pull her " + strip_choice.name + " off, dropping it to the ground.")
                renpy.call("strip_menu", the_person) #TODO: Girl sometimes interupts you to get you to keep going. Have to strip them down in segments.
            else:
                renpy.say("", "You start to pull off " + the_person.name + "'s " + strip_choice.name + " when she grabs your hand and stops you.") 
                the_person.call_strip_reject()
                renpy.call("strip_menu", the_person) #TODO: Girl sometimes interupts you to get you to keep going. Have to strip them down in segments.
    return   
    
label examine_room(the_room):
    python:
        desc = "You are at the [the_room.name]. "

        people_here = the_room.people #Format the names of people in the room with you so it looks nice.
        pers_ct = len(people_here)
        if pers_ct == 1:
            desc += people_here[0].name + " is here. "
        elif pers_ct > 0:
            if pers_ct < 6:
                desc = "You see "
                if pers_ct > 2:
                    for person in people_here[0:pers_ct-3]:
                        desc += person.name
                        desc += ", "
                desc += people_here[pers_ct-2].name + "and " + people_here[pers_ct-1].name + " here. "
            else:
                desc += "It is filled with people here. "

        connections_here = the_room.connections # Now we format the output for the connections so that it is readable.
        conn_ct = len(connections_here)
        if conn_ct == 0:
            desc += "There are no exits from here. You're trapped! " #Shouldn't ever happen, hopefully."
        else:
            desc += "From here you can head to "
            if conn_ct == 2:
                desc += "either the " + connections_here[0].name + " or "
            elif conn_ct > 2:
                for place in connections_here[0:conn_ct-2]:
                    desc += "the " + place.name + ", the "
                desc += connections_here[conn_ct-2].name + " or "
            desc += "the " + connections_here[conn_ct-1].name +". "
        #desc += "That's all there is to see nearby." # don't state the obvious
        renpy.say("",desc) ##This is the actual print statement!!
    return
    
label examine_person(the_person):
    #Take a close look and figure out their physical attributes (tit size, ass size?, hair colour, hair style)
    
    python:
        string = "She has " + the_person.skin + " coloured skin, along with " + the_person.hair_colour + " coloured hair and pretty " + the_person.eyes + " coloured eyes. She stands " + height_to_string(the_person.height) + " tall."
        renpy.say("",string)
        
        outfit_top = the_person.outfit.get_upper_visible()
        outfit_bottom = the_person.outfit.get_lower_visible()
        string = ""
        
        if len(outfit_top) == 0: ##ie. is naked
            string += "She's wearing nothing at all on top, with her nice " + the_person.tits + " sized tits on display for you."
        elif len(outfit_top) == 1:
            string += "She's wearing a " + outfit_top[0].name + " with her nice " + the_person.tits + " sized tits underneath."
        elif len(outfit_top) == 2:
            string += "She's wearing a " + outfit_top[1].name + " with a " + outfit_top[0].name + " underneath. Her tits look like they're " + the_person.tits + "'s."
        elif len(outfit_top) == 3:
            string += "She's wearing a " + outfit_top[2].name + " with a " + outfit_top[1].name + " and " + outfit_top[0].name + " underneath. Her tits look like they're " + the_person.tits + "'s."
        renpy.say("",string)
        
        string = ""
        if len(outfit_bottom) == 0: #naked
            string += "Her legs are completely bare, and you have a clear view of her pussy."
        elif len(outfit_bottom) == 1:
            string += "She's also wearing " + outfit_bottom[0].name + " below."
            if not outfit_bottom[0].hide_below:
                string += " You can see her pussy underneath."
        elif len(outfit_bottom) == 2:
            string += "She's also wearing " + outfit_bottom[0].name + " below, with " + outfit_bottom[1].name +  " visible below."
            if not outfit_bottom[1].hide_below:
                string += " You can see her pussy underneath."
        renpy.say("",string)
        title = mc.business.get_employee_title(the_person)
        if title == "Researcher":
            renpy.say("", the_person.name + " currently works in your research department.")
        elif title == "Marketing":
            renpy.say("", the_person.name + " currently works in your marketing department.")
        elif title == "Supply":
            renpy.say("", the_person.name + " currently works in your supply procurement department.")
        elif title == "Production":
            renpy.say("", the_person.name + " currently works in your production department.")
        elif title == "Human Resources":
            renpy.say("", the_person.name + " currently works in your human resources department.")
        else:
            renpy.say("", the_person.name + " does not currently work for you.")
    
    return
    
label give_serum(the_person):
    call screen serum_inventory_select_ui(mc.inventory)
    if not _return == "None":
        $ the_serum = _return
        "You decide to give [the_person.name] a dose of [the_serum.name]."
        $ mc.inventory.change_serum(the_serum,-1)
        $ the_person.give_serum(copy.copy(the_serum)) #use a copy rather than the main class, so we can modify and delete the effects without changing anything else.
    else:
        "You decide not to give [the_person.name] anything right now."
    return
    
label sleep_action_description:
    "You go to bed after a hard days work."
    call advance_time from _call_advance_time
    return
    
label faq_action_description:
    call faq_loop from _call_faq_loop_2
    return
    
label hr_work_action_description:
    $ mc.business.player_hr()
    call advance_time from _call_advance_time_1
    "You settle in and spend a few hours filling out paperwork."
    return
    
label research_work_action_description:
    $ mc.business.player_research()
    call advance_time from _call_advance_time_2
    "You spend a few hours in the lab, experimenting with different chemicals and techniques."
    return
    
label supplies_work_action_description:
    $ mc.business.player_buy_supplies()
    call advance_time from _call_advance_time_3
    "You spend a few hours securing new supplies for the lab, spending some of it's available funds to do so."
    return
    
label market_work_action_description:
    $ mc.business.player_market()
    call advance_time from _call_advance_time_4    
    "You spend a few hours making phone calls to your clients and shipping out orders that have been marked for sale."
    return
    
label production_work_action_description:
    $ mc.business.player_production()
    call advance_time from _call_advance_time_5
    "You spend a few hours in the lab, synthesizing serum from the it's raw chemical precursors."
    return
    
label interview_action_description:
    $ count = 3 #Num of people to generate, by default is 3. Changed with some policies
    if recruitment_batch_three_policy.is_owned():
        $ count = 10
    elif recruitment_batch_two_policy.is_owned():
        $ count = 6
    elif recruitment_batch_one_policy.is_owned():
        $ count = 4
    
    $ interview_cost = 50
    "Bringing in [count] people for an interview will cost $[interview_cost]. Do you want to spend time interviewing potential employees?"
    menu:
        "Yes, I'll pay the cost. -$[interview_cost]":
            $ mc.business.funds += -interview_cost #T
            $ renpy.scene("Active")
            hide screen main_ui
            hide screen business_ui
            python:
                candidates = []
                
                for x in range(0,count+1): #NOTE: count is given +1 because the screen tries to pre-calculate the result of button presses. This leads to index out-of-bounds, unless we pad it with an extra character (who will not be reached).
                    candidates.append(make_person())
                show_candidate(candidates[0]) #Show the first candidate, updates are taken care of by actions within the screen.
                
            call screen interview_ui(candidates,count)
            $ renpy.scene("Active")
            show screen main_ui
            show screen business_ui
            if not _return == "None":
                $ new_person = _return
                "You complete the nessesary paperwork and hire [_return.name]. What division do you assign them to?"
                menu:
                    "Research and Development.":
                        $ mc.business.add_employee_research(new_person)
                        $ rd_division.add_person(new_person)
                        
                    "Production.":
                        $ mc.business.add_employee_production(new_person)
                        $ p_division.add_person(new_person)
                        
                    "Supply Procurement.":
                        $ mc.business.add_employee_supply(new_person)
                        $ office.add_person(new_person)
                        
                    "Marketing.":
                        $ mc.business.add_employee_marketing(new_person)
                        $ m_division.add_person(new_person)
                        
                    "Human Resources.":
                        $ mc.business.add_employee_hr(new_person)
                        $ office.add_person(new_person)
                        
            else:
                "You decide against hiring anyone new for now."
            call advance_time from _call_advance_time_6
        "Nevermind.":
            $ temp = 0 #NOTE: just here so that this isn't technically an empty block.
    return
    
label serum_design_action_description:
    $counter = len(list_of_traits)
    hide screen main_ui
    hide screen business_ui
    call screen serum_design_ui(SerumDesign(),[]) #This will return the final serum design, or None if the player backs out.
    show screen main_ui
    show screen business_ui
    if not _return == "None":
        $ serum = _return
        $ name = renpy.input("Please give this serum design a name.")
        $ serum.name = name
        $ mc.business.add_serum_design(serum)
        call advance_time from _call_advance_time_7
    else:
        "You decide not to spend any time designing a new serum type."
    return
    
label research_select_action_description:
    hide screen main_ui
    hide screen business_ui
    call screen serum_select_ui
    show screen main_ui
    show screen business_ui
    if not _return == "None":
        $mc.business.set_serum_research(_return)
        "You change your research to [_return.name]."
    else:
        "You decide to leave your labs current research topic as it is."
    return
    
label production_select_action_description:
    hide screen main_ui
    hide screen business_ui
    call screen serum_production_select_ui
    show screen main_ui
    show screen business_ui
    if not _return == "None":
        $mc.business.change_production(_return)
        "You change your production line over to [_return.name]."
    else:
        "You decide not to change the way your production line is set up."
    return
    
label trade_serum_action_description:
    "You step into the stock room to check what you currently have produced."
    hide screen main_ui
    hide screen business_ui
    $ renpy.block_rollback()
    call screen serum_trade_ui(mc.inventory,mc.business.inventory)
    $ renpy.block_rollback()
    show screen main_ui
    show screen business_ui
    return
    
label sell_serum_action_description:
    "You look through your stock of serum, marking some to be sold by your marketing team."
    hide screen main_ui
    hide screen business_ui
    $ renpy.block_rollback()
    call screen serum_trade_ui(mc.business.inventory,mc.business.sale_inventory,"Production Stockpile","Sales Stockpile")
    $ renpy.block_rollback()
    show screen main_ui
    show screen business_ui
    return
    
label set_autosell_action_description:
    $ amount = renpy.input("How many units of " + mc.business.serum_production_target.name + " would you like to keep in stock? Extra will automatically be moved to the sales department.")
    $ amount = amount.strip()
    while not (amount.isdigit() and int(amount) >= 0):
        $ amount = renpy.input("Please put in positive integer value.")
    $ amount = int(amount)
    
    $ mc.business.auto_sell_threshold = amount
    "Extra doses of the serum [mc.business.serum_production_target.name] will be automatically moved to the sales department now."
    return
    
    
label pick_supply_goal_action_description:
    $ amount = renpy.input("How many units of serum supply would you like your supply procurement team to keep stocked?")
    $ amount = amount.strip()
    
    while not amount.isdigit():
        $ amount = renpy.input("Please put in an integer value.")
        
    $ amount = int(amount)
    $ mc.business.supply_goal = amount
    if amount <= 0:
        "You tell your team to keep [amount] units of serum supply stocked. They question your sanity, but otherwise continue with their work. Perhaps you should use a positive number."
    else:
        "You tell your team to keep [amount] units of serum supply stocked."
    
    return
    
label move_funds_action_description:
    menu:
        "Move funds from the company to yourself." if mc.business.funds>0:
            $ amount = renpy.input("How much would you like to withdraw from the company bank account? (Currently has $[mc.business.funds])")
            $ amount.strip()
            while (not amount.isdigit() or int(amount) > mc.business.funds):
                $ amount = renpy.input("Please put in a positive value equal to or lower than the current funds in the business account. (Currently has $[mc.business.funds])")
                $ amount.strip()
                
            $ mc.business.funds -= int(amount)
            $ mc.money += int(amount)
            return
            
        "Move funds from yourself into the company." if mc.money>0:
            $ amount = renpy.input("How much would you like to deposit into the company account? (You currently have $[mc.money])")
            $ amount.strip()
            while (not amount.isdigit() or int(amount) > mc.money):
                $ amount = renpy.input("Please put in a positive value equal to or lower than the current funds in the business account. (Currently has $[mc.money])")
                $ amount.strip()
                
            $ mc.business.funds += int(amount)
            $ mc.money -= int(amount)
            return
            
        "Do nothing.":
            return
            
label policy_purchase_description:
    call screen policy_selection_screen()
    return
            
label set_uniform_description:
    "Which division do you want to set the uniform for?"
    $ selected_div = None
    menu:
        "All.":
            $ selected_div = "All"
        
        "Research and Development.":
            $ selected_div = "R"
        
        "Production.":
            $ selected_div = "P"
            
        "Supply Procurement.":
            $ selected_div = "S"
            
        "Marketing.":
            $ selected_div = "M"
            
        "Human Resources.":
            $ selected_div = "H"
            
    if maximal_arousal_uniform_policy.is_owned():
        $slut_limit = 999 #ie. no limit at all.
    elif corporate_enforced_nudity_policy.is_owned():
        $slut_limit = 80
    elif minimal_coverage_uniform_policy.is_owned():
        $slut_limit = 60
    elif reduced_coverage_uniform_policy.is_owned():
        $slut_limit = 40
    elif casual_uniform_policy.is_owned():
        $slut_limit = 25
    elif relaxed_uniform_policy.is_owned():
        $slut_limit = 15
    elif strict_uniform_policy.is_owned():
        $slut_limit = 5
    else:
        $slut_limit = 0
            
    call screen outfit_select_manager(slut_limit)
    $ selected_outfit = _return
    
    if selected_outfit == "No Return":
        return
        
    if selected_div == "All":
        $ mc.business.m_uniform = selected_outfit
        $ mc.business.p_uniform = selected_outfit
        $ mc.business.r_uniform = selected_outfit
        $ mc.business.s_uniform = selected_outfit
        $ mc.business.h_uniform = selected_outfit
        
    elif selected_div == "R":
        $ mc.business.r_uniform = selected_outfit
        
    elif selected_div == "P":
        $ mc.business.p_uniform = selected_outfit
        
    elif selected_div == "S":
        $ mc.business.s_uniform = selected_outfit
        
    elif selected_div == "M":
        $ mc.business.m_uniform = selected_outfit
        
    elif selected_div == "H":
        $ mc.business.h_uniform = selected_outfit
    
    return
    
label set_serum_description:
    "Which divisions would you like to set a daily serum for?"
    $ selected_div = None
    menu:
        "All.":
            $ selected_div = "All"
        
        "Research and Development.":
            $ selected_div = "R"
        
        "Production.":
            $ selected_div = "P"
            
        "Supply Procurement.":
            $ selected_div = "S"
            
        "Marketing.":
            $ selected_div = "M"
            
        "Human Resources.":
            $ selected_div = "H"
    
    menu:
        "Pick a new serum.":
            call screen serum_inventory_select_ui(mc.business.inventory)
            $ selected_serum = _return

        "Clear existing serum.":
            $ selected_serum = None
    
    if selected_serum == "None": #IF we didn't select an actual serum, just return and don't chagne anything.
        return
    
    if selected_div == "All":
        $ mc.business.m_serum = selected_serum
        $ mc.business.p_serum = selected_serum
        $ mc.business.r_serum = selected_serum
        $ mc.business.s_serum = selected_serum
        $ mc.business.h_serum = selected_serum
        
    elif selected_div == "R":
        $ mc.business.r_serum = selected_serum
        
    elif selected_div == "P":
        $ mc.business.p_serum = selected_serum
        
    elif selected_div == "S":
        $ mc.business.s_serum = selected_serum
        
    elif selected_div == "M":
        $ mc.business.m_serum = selected_serum
        
    elif selected_div == "H":
        $ mc.business.h_serum = selected_serum
    
    return
    
label advance_time:
    # 1) Turns are processed _before_ the time is advanced.
    # 1a) crises are processed if they are triggered.
    # 2) Time is advanced, day is advanced if required.
    # 3) People go to their next intended location.
    # Note: This will require breaking people's turns into movement and actions.
    # Then: Add research crisis when serum is finished, requiring additional input from the player and giving the chance to test a serum on the R&D staff.

    python: 
        people_to_process = [] #This is a master list of turns of need to process, stored as tuples [character,location]. Used to avoid modifying a list while we iterate over it, and to avoid repeat movements.
        for place in list_of_places:
            for people in place.people:
                people_to_process.append([people,place])
                
    python:
        for (people,place) in people_to_process: #Run the results of people spending their turn in their current location.
            people.run_turn()
        mc.business.run_turn()
        
    $ count = 0
    $ max = len(mc.business.mandatory_crises_list)
    $ clear_list = []
    while count < max: #We need to keep this in a renpy loop, because a return call will always return to the end of an entire python block.
        $crisis = mc.business.mandatory_crises_list[count]
        if crisis.check_requirement():
            $ crisis.call_action()
            $ renpy.scene("Active")
            $ renpy.show(mc.location.name,what=mc.location.background_image) #Make sure we're showing the correct background for our location, which might have been temporarily changed by a crisis.
            $ clear_list.append(crisis)
        $ count += 1
            
    
    python: #Needs to be a different python block, otherwise the rest of the block is not called when the action returns.
        for crisis in clear_list:
            mc.business.mandatory_crises_list.remove(crisis) #Clean up the list.
    
    if renpy.random.randint(0,100) < 10: #ie. run a crisis 25% of the time. TODO: modify this.
        python:
            possible_crisis_list = []
            for crisis in crisis_list:
                if crisis[0].check_requirement(): #Get the first element of the weighted tuple, the action.
                    possible_crisis_list.append(crisis) #Build a list of valid crises from ones that pass their requirement.
                    
        $ the_crisis = get_random_from_weighted_list(possible_crisis_list)
        if the_crisis:
            $ the_crisis.call_action()
    
    $ renpy.scene("Active")
    $ renpy.show(mc.location.name,what=mc.location.background_image) #Make sure we're showing the correct background for our location, which might have been temporarily changed by a crisis.
    hide screen person_info_ui
    show screen business_ui
    
    if time_of_day == 4: ##First, determine if we're going into the next chunk of time. If we are, advance the day and run all of the end of day code.
        $ time_of_day = 0
        $ day += 1
        python:
            for (people,place) in people_to_process:
                people.run_day()
        $ mc.business.run_day()
        
        if mc.business.funds < 0:
            $ mc.business.bankrupt_days += 1
            if mc.business.bankrupt_days == mc.business.max_bankrupt_days:
                $ renpy.say("","With no funds to pay your creditors you are forced to close your business and auction off all of your materials at a fraction of their value. Your story ends here.")
                $ renpy.full_restart()
            else:
                $ days_remaining = mc.business.max_bankrupt_days-mc.business.bankrupt_days
                $ renpy.say("","Warning! Your company is losing money and unable to pay salaries or purchase necessary supplies! You have [days_remaining] days to restore yourself to positive funds or you will be foreclosed upon!")
        else:
            $ mc.business.bankrupt_days = 0
            
        call screen end_of_day_update() # We have to keep this outside of a python block, because the renpy.call_screen function does not properly fade out the text bar.
        $ mc.business.clear_messages()

    else:
        $ time_of_day += 1 ##Otherwise, just run the end of day code.
        
    if time_of_day == 1 and daily_serum_dosage_policy.is_owned(): #It is the start of the work day, give everyone their daily dose of serum
        $ mc.business.give_daily_serum()
        
    python:    
        for (people,place) in people_to_process: #Now move everyone to where the should be in the next time chunk. That may be home, work, etc.
            people.run_move(place)
        
    return

label create_test_variables(character_name,business_name,stat_array,skill_array,_sex_array): #Gets all of the variables ready. TODO: Move some of this stuff to an init block?
    python:
        bliss = Status_Effect("Bliss", "Giddy with happiness. Raises happiness over time, but lowers obedience.", bliss_function)
        growing_breasts = Status_Effect("Growing Breasts", "Day by day her breasts are getting bigger.", growing_breasts_function)
        shrinking_breasts = Status_Effect("Shrinking Breasts", "Day by day her breasts are getting smaller.", shrinking_breasts_function)
        
        list_of_traits = [] #List of serum traits that can be used. Established here so they play nice with rollback, saving, etc.
        #TODO: Add list of keywords for similar trait exclusion (ie. production, medical, breast, etc.)
    
        improved_serum_prod = SerumTrait("Improved Serum Production","General improvements to the basic serum design. Improves suggestion gain and value.",improved_serum_production,
            research_needed = 200)
        
        basic_med_app = SerumTrait("Basic Medical Application","Adding a few basic medical applications significantly increases the value of this serum.",basic_medical_serum_production,
            research_needed = 200)
        
        obedience_enhancer = SerumTrait("Obedience Enhancer","A blend of off the shelf pharmaceuticals will make the recipient more receptive to direct orders.",obedience_enhancer_effect,
            requires =[improved_serum_prod,basic_med_app],research_needed = 300)
        
        improved_duration_trait = SerumTrait("Improved Reagent Purification","By carefully purifying the starting materials the length of time a serum remains active can be greatly increased.",improved_duration_effect,
            requires=[improved_serum_prod,basic_med_app],research_needed = 350)
        
        aphrodisiac = SerumTrait("Distilled Aprodisac","Careful distilation can concentrate the active ingredient from common aprodisiacs, producing a sudden spike in sluttiness when consumed.",aphrodisiac_effect,
            requires=[improved_duration_trait,basic_med_app],research_needed = 250)
        
        advanced_serum_prod = SerumTrait("Advanced Serum Production","Advanced improvements to the basic serum design. Greatly improves suggestion gain and value.",advanced_serum_production,
            requires=[improved_serum_prod,basic_med_app], research_needed = 800)
        
        low_volatility_reagents = SerumTrait("Low Volatility Reagents","Carefully sourced and stored reagents will greatly prolong the effects of a serum, at an increased production cost.", low_volatility_reagents_effect,
            requires=[advanced_serum_prod,improved_duration_trait], research_needed = 600)
        
        futuristic_serum_prod = SerumTrait("Futuristic Serum Production","Space age technology makes the serum incredibly valuable and maxes out suggestion gain.",futuristic_serum_production,
            requires=[advanced_serum_prod], research_needed= 3000)
        
        breast_enhancement = SerumTrait("Breast Enhancement", "Grows breasts overnight. Has a 10% chance of increasing a girls breast size by one step with each time unit.", growing_breast_effect,
            status_effects=[growing_breasts],requires=[advanced_serum_prod,basic_med_app],research_needed = 500)
        
        breast_reduction = SerumTrait("Breast Reduction", "Shrinks breasts overnight. Has a 10% chance of decreasing a girls breast size by one step with each time unit.", shrinking_breast_effect,
            status_effects=[shrinking_breasts],requires=[advanced_serum_prod,basic_med_app], research_needed = 500)

        focus_enhancement = SerumTrait("Medical Amphetamines", "The inclusion of low doses of amphetamines help the user focus intently for long periods of time.",focus_enhancement_production,
            requires=[advanced_serum_prod,basic_med_app], research_needed = 800)
        
        int_enhancement = SerumTrait("Quick Release Nootropics", "Nootropics enhance cognition and learning. These fast acting nootropics produce results almost instantly, but for a limited period of time.",int_enhancement_production,
            requires=[advanced_serum_prod,basic_med_app], research_needed = 800)
        
        cha_enhancement = SerumTrait("Stress Inhibitors", "By reducing the users natural stress response to social interactions they are able to express themselves more freely and effectively. Takes effect immediately, but lasts only for a limited time", cha_enhancement_production,
            requires=[advanced_serum_prod,basic_med_app], research_needed = 800)
        
        happiness_tick = SerumTrait("Slow Release Dopamine", "By slowly flooding the users dopamine receptors they can be put into a long lasting sense of bliss. Raises happiness by 5 each time unit, but users will become more carefree as time goes on, lowering obedience by 5.", happiness_tick_effect,
            status_effects=[bliss],requires=[futuristic_serum_prod,basic_med_app], research_needed = 2500)
        
        list_of_traits.append(improved_serum_prod)
        list_of_traits.append(basic_med_app)
        list_of_traits.append(improved_duration_trait)
        list_of_traits.append(advanced_serum_prod)
        list_of_traits.append(futuristic_serum_prod)
        list_of_traits.append(breast_enhancement)
        list_of_traits.append(breast_reduction)
        list_of_traits.append(focus_enhancement)
        list_of_traits.append(int_enhancement)
        list_of_traits.append(cha_enhancement)
        list_of_traits.append(happiness_tick)
        list_of_traits.append(low_volatility_reagents)
        list_of_traits.append(aphrodisiac)
        list_of_traits.append(obedience_enhancer)
        
        list_of_places = [] #By having this in an init block it may be set to null each time the game is reloaded, because the initialization stuff below is only called once.
        
        ##Actions##
        hr_work_action = Action("Spend time orgainizing your business.",hr_work_action_requirement,"hr_work_action_description")
        research_work_action = Action("Spend time researching in the lab.",research_work_action_requirement,"research_work_action_description")
        supplies_work_action = Action("Spend time ordering supplies.",supplies_work_action_requirement,"supplies_work_action_description")
        market_work_action = Action("Spend time shipping doses of serum marked for sale.",market_work_action_requirement,"market_work_action_description")
        production_work_action = Action("Spend time producing serum in the lab.",production_work_action_requirement,"production_work_action_description")
        
        interview_action = Action("Hire someone new.", interview_action_requirement,"interview_action_description")
        design_serum_action = Action("Create a new serum design.", serum_design_action_requirement,"serum_design_action_description")
        pick_research_action = Action("Pick a new research topic.", research_select_action_requirement,"research_select_action_description")
        pick_production_action = Action("Change production to a new serum.", production_select_action_requirement,"production_select_action_description")
        pick_supply_goal_action = Action("Set the amount of supply you would like to maintain.", pick_supply_goal_action_requirement,"pick_supply_goal_action_description")
        move_funds_action = Action("Siphon money into your personal account.", move_funds_action_requirement,"move_funds_action_description")
        policy_purhase_action = Action("Purchase new business policies.", policy_purchase_requirement,"policy_purchase_description")
        
        trade_serum_action = Action("Trade serums between yourself and the business inventory.", trade_serum_action_requirement, "trade_serum_action_description")
        sell_serum_action = Action("Mark serum to be sold.", sell_serum_action_requirement, "sell_serum_action_description")
        set_autosell_action = Action("Set autosell threshold.", set_autosell_action_requirement, "set_autosell_action_description")
        
        sleep_action = Action("Go to sleep for the night.",sleep_action_requirement,"sleep_action_description")
        faq_action = Action("Check the FAQ.",faq_action_requirement,"faq_action_description")
        
        set_uniform_action = Action("Set Employee Uniforms",set_uniform_requirement,"set_uniform_description")
        set_serum_action = Action("Set Daily Serum Doses",set_serum_requirement,"set_serum_description")
        
        ##PC's Home##
        bedroom = Room("bedroom","Bedroom",[],house_background,[],[],[sleep_action,faq_action],False,[0.1,0.5])
        kitchen = Room("kitchen", "Kitchen",[],house_background,[],[],[],False,[0.1,0.7])
        hall = Room("house entrance","House Entrance",[],house_background,[],[],[],False,[0.2,0.6])
        
        ##PC's Work##
        lobby = Room(business_name + " lobby",business_name + " Lobby",[],office_background,[],[],[],False,[0.8,0.6])
        office = Room("main office","Main Office",[],office_background,[],[],[policy_purhase_action,hr_work_action,supplies_work_action,interview_action,sell_serum_action,pick_supply_goal_action,move_funds_action,set_uniform_action,set_serum_action],False,[0.85,0.82])
        rd_division = Room("R&D division","R&D Division",[],lab_background,[],[],[research_work_action,design_serum_action,pick_research_action],False,[0.9,0.67])
        p_division = Room("Production division", "Production Division",[],office_background,[],[],[production_work_action,pick_production_action,trade_serum_action,set_autosell_action],False,[0.9,0.53])
        m_division = Room("marketing division","Marketing Division",[],office_background,[],[],[market_work_action],False,[0.85,0.38])
        
        ##Connects all Locations##
        downtown = Room("downtown","Downtown",[],outside_background,[],[],[],True,[0.5,0.65])
        
        ##A mall, for buying things##
        office_store = Room("office supply store","Office Supply Store",[],mall_background,[],[],[],True,[0.68,0.24])
        clothing_store = Room("clothing store","Clothing Store",[],mall_background,[],[],[],True,[0.6,0.15])
        sex_store = Room("sex store","Sex Store",[],mall_background,[],[],[],True,[0.5,0.13])
        home_store = Room("home improvement store","Home Improvement Store",[],mall_background,[],[],[],True,[0.4,0.15])
        gym = Room("gym","Gym",[],mall_background,[],[],[],True,[0.32,0.24])
        mall = Room("mall","Mall",[],mall_background,[],[],[],True,[0.5,0.3])
        
        ##PC starts in his bedroom## 
        main_business = Business(business_name, m_division, p_division, rd_division, office, office)
        mc = MainCharacter(bedroom,character_name,main_business,stat_array,skill_array,_sex_array)
        generate_premade_list() # Creates the list with all the premade characters for the game in it. Without this we both break the policies call in create_random_person, and regenerate the premade list on each restart.
        
        ##Keep a list of all the places##
        list_of_places.append(bedroom)
        list_of_places.append(kitchen)
        list_of_places.append(hall)
        
        list_of_places.append(lobby)
        list_of_places.append(office)
        list_of_places.append(rd_division)
        list_of_places.append(p_division)
        list_of_places.append(m_division)
        
        list_of_places.append(downtown)
        
        list_of_places.append(office_store)
        list_of_places.append(clothing_store)
        list_of_places.append(sex_store)
        list_of_places.append(home_store)
        list_of_places.append(gym)
        list_of_places.append(mall)
        
        hall.link_locations_two_way(bedroom)
        hall.link_locations_two_way(kitchen)
        
        downtown.link_locations_two_way(hall)
        downtown.link_locations_two_way(lobby)
        downtown.link_locations_two_way(mall)
        
        lobby.link_locations_two_way(office)
        lobby.link_locations_two_way(rd_division)
        lobby.link_locations_two_way(m_division)
        lobby.link_locations_two_way(p_division)
        
        mall.link_locations_two_way(office_store)
        mall.link_locations_two_way(clothing_store)
        mall.link_locations_two_way(sex_store)
        mall.link_locations_two_way(home_store)
        mall.link_locations_two_way(gym)
        
        bedroom.add_object(make_wall())
        bedroom.add_object(make_floor())
        bedroom.add_object(make_bed())
        bedroom.add_object(make_window())
        
        kitchen.add_object(make_wall())
        kitchen.add_object(make_floor())
        kitchen.add_object(make_chair())
        
        hall.add_object(make_wall())
        hall.add_object(make_floor())
        
        lobby.add_object(make_wall())
        lobby.add_object(make_floor())
        lobby.add_object(make_chair())
        lobby.add_object(make_window())
        
        office.add_object(make_wall())
        office.add_object(make_floor())
        office.add_object(make_chair())
        office.add_object(make_window())
        
        rd_division.add_object(make_wall())
        rd_division.add_object(make_floor())
        rd_division.add_object(make_chair())
        
        m_division.add_object(make_wall())
        m_division.add_object(make_floor())
        m_division.add_object(make_chair())
        
        p_division.add_object(make_wall())
        p_division.add_object(make_floor())
        p_division.add_object(make_chair())
        
        downtown.add_object(make_floor())
        
        office_store.add_object(make_wall())
        office_store.add_object(make_floor())
        office_store.add_object(make_chair())
        
        clothing_store.add_object(make_wall())
        clothing_store.add_object(make_floor())
        
        sex_store.add_object(make_wall())
        sex_store.add_object(make_floor())
    
        home_store.add_object(make_wall())
        home_store.add_object(make_floor())
        home_store.add_object(make_chair())
        
        mall.add_object(make_wall())
        mall.add_object(make_floor())
        
        max_num_of_random = 4 ##Default use to be 4
        for place in list_of_places:
            if place.public:
                random_count = renpy.random.randint(1,max_num_of_random)
                for x in range(0,random_count):
                    place.add_person(create_random_person()) #We are using create_random_person instead of make_person because we want premade character bodies to be hirable instead of being eaten up by towns-folk.
                
        ##Global Variable Initialization##
        day = 0 ## Game starts on day 0.
        time_of_day = 0 ## 0 = Early morning, 1 = Morning, 2 = Afternoon, 3 = Evening, 4 = Night
    
    return
