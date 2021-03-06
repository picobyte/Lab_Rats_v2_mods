init -30 python:
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

            return -1 if self.__hash__() < other.__hash__() else 1 #Use hash values to break ties.

        def __hash__(self):
            return hash((self.name,self.requirement,self.effect,self.args))

        def check_requirement(self): #Calls the function that was passed to the action when it was created. Currently can only use global variables, will change later to take arbitrary list.
            return self.requirement()

        def call_action(self): #Can only use global variables. args is a list of elements you want to include as arguments. None is default
            if self.args is None:
                renpy.call(self.effect)
            else:
                renpy.call(self.effect, self.args)
            renpy.return_statement()

    ##Initialization of requirement functions go down here.##
    def sleep_action_requirement():
        return world.time_of_day == 4

    def faq_action_requirement():
        return preferences.show_faq

    def hr_work_action_requirement():
        return world.time_of_day < 4

    def research_work_action_requirement():
        return world.time_of_day < 4 and mc.business.research.subject != None

    def supplies_work_action_requirement():
        return world.time_of_day < 4

    def market_work_action_requirement():
        return world.time_of_day < 4

    def production_work_action_requirement():
        return world.time_of_day < 4 and mc.business.production.serum != None

    def interview_action_requirement():
        return world.time_of_day < 4

    def serum_design_action_requirement():
        return world.time_of_day < 4

    def research_select_action_requirement():
        return True

    def production_select_action_requirement():
        return True

    def trade_serum_action_requirement():
        return True

    def sell_serum_action_requirement():
        return True

    def set_autosell_action_requirement():
        return mc.business.production.serum is not None

    def pick_supply_goal_action_requirement():
        return True

    def move_funds_action_requirement():
        return True

    def policy_purchase_requirement():
        return True

#    def can_hr_open_job():
#        return len(mc.business.division[4].people) > 1

    def set_uniform_requirement():
        return "Strict Corporate Uniforms" in mc.business.active_policies

    def set_serum_requirement():
        return "Daily Serum Dosage" in mc.business.active_policies

    ##Actions##
    hr_work_action = Action("Spend time orgainizing your business.", hr_work_action_requirement, "hr_work_action_description")
    research_work_action = Action("Spend time researching in the lab.", research_work_action_requirement, "research_work_action_description")
    supplies_work_action = Action("Spend time ordering supplies.", supplies_work_action_requirement, "supplies_work_action_description")
    market_work_action = Action("Spend time shipping doses of serum marked for sale.", market_work_action_requirement, "market_work_action_description")
    production_work_action = Action("Spend time producing serum in the lab.", production_work_action_requirement, "production_work_action_description")

    interview_action = Action("Hire someone new.", interview_action_requirement, "interview_action_description")
    design_serum_action = Action("Create a new serum design.", serum_design_action_requirement, "serum_design_action_description")
    pick_research_action = Action("Pick a new research topic.", research_select_action_requirement, "research_select_action_description")
    pick_production_action = Action("Change production to a new serum.", production_select_action_requirement, "production_select_action_description")
    pick_supply_goal_action = Action("Set the amount of supply you would like to maintain.", pick_supply_goal_action_requirement, "pick_supply_goal_action_description")
    move_funds_action = Action("Siphon money into your personal account.", move_funds_action_requirement, "move_funds_action_description")
    policy_purhase_action = Action("Purchase new business policies.", policy_purchase_requirement, "policy_purchase_description")
    #policy_hire_action = Action("Set job openings.", can_hr_open_job, "set_job_opening_description")

    trade_serum_action = Action("Trade serums between yourself and the business inventory.", trade_serum_action_requirement, "trade_serum_action_description")
    sell_serum_action = Action("Mark serum to be sold.", sell_serum_action_requirement, "sell_serum_action_description")
    set_autosell_action = Action("Set autosell threshold.", set_autosell_action_requirement, "set_autosell_action_description")

    sleep_action = Action("Go to sleep for the night.", sleep_action_requirement, "sleep_action_description")
    faq_action = Action("Check the FAQ.", faq_action_requirement, "faq_action_description")

    set_uniform_action = Action("Set Employee Uniforms", set_uniform_requirement, "set_uniform_description")
    set_serum_action = Action("Set Daily Serum Doses", set_serum_requirement, "set_serum_description")

init:
    pass

label sleep_action_description:
    "You go to bed after a hard world.days work."
    call advance_time from _call_advance_time
    return

label faq_action_description:
    call faq_loop from _call_faq_loop_2
    return

label hr_work_action_description:
    $ mc.job = "Human Resources"
    call advance_time from _call_advance_time_1
    $ mc.job = "Supervisor"
    "You settle in and spend a few hours filling out paperwork."
    return

label research_work_action_description:
    $ mc.job = "Researcher"
    call advance_time from _call_advance_time_2
    $ mc.job = "Supervisor"
    "You spend a few hours in the lab, experimenting with different chemicals and techniques."
    return

label supplies_work_action_description:
    $ mc.job = "Supply"
    call advance_time from _call_advance_time_3
    $ mc.job = "Supervisor"
    "You spend a few hours securing new supplies for the lab, spending some of it's available funds to do so."
    return

label market_work_action_description:
    $ mc.job = "Marketing"
    call advance_time from _call_advance_time_4
    $ mc.job = "Supervisor"
    "You spend a few hours making phone calls to your clients and shipping out orders that have been marked for sale."
    return

label production_work_action_description:
    $ mc.job = "Production"
    call advance_time from _call_advance_time_5
    $ mc.job = "Supervisor"
    "You spend a few hours in the lab, synthesizing serum from the it's raw chemical precursors."
    return

label interview_action_description:
    $ count = 3 + sum(policies[p].get("interview batch increase", 0) for p in mc.business.active_policies) #Num of people to generate, by default is 3. Changed with some policies
    $ mc.business.funds += -mc.business.interview_cost #T
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
    if _return != "None":
        $ new_person = _return
        "You complete the nessesary paperwork and hire [_return.name]. What division do you assign them to?"
        python:
            mc.business.remove_employee(new_person)
            selected_div = renpy.display_menu([(div.name, div) for div in mc.business.division], True, "Choice")
            mc.business.add_employee(new_person, selected_div)
    else:
        "You decide against hiring anyone new for now."
    call advance_time from _call_advance_time_6
    return

label serum_design_action_description:
    hide screen main_ui
    hide screen business_ui
    call screen serum_design_ui() #This will return the final serum design, or None if the player backs out.
    show screen main_ui
    show screen business_ui
    if _return != "None":
        $ mc.business.production.add_serum_design(_return)
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
    if _return != "None":
        $mc.business.research.subject = _return
        $renpy.say("", "You change your research to %(name)s." % _return)
    else:
        "You decide to leave your labs current research topic as it is."
    return

label production_select_action_description:
    hide screen main_ui
    hide screen business_ui
    call screen serum_production_select_ui
    show screen main_ui
    show screen business_ui
    if _return != "None":
        $mc.business.production.change(_return)
        $renpy.say("", "You change your production line over to %(name)s." % _return)
    else:
        "You decide not to change the way your production line is set up."
    return

label trade_serum_action_description:
    "You step into the stock room to check what you currently have produced."
    hide screen main_ui
    hide screen business_ui
    $ renpy.block_rollback()
    call screen serum_trade_ui(mc.inventory["serum"],mc.business.inventory["stock"]["serum"])
    $ renpy.block_rollback()
    show screen main_ui
    show screen business_ui
    return

label sell_serum_action_description:
    "You look through your stock of serum, marking some to be sold by your marketing team."
    hide screen main_ui
    hide screen business_ui
    $ renpy.block_rollback()
    call screen serum_trade_ui(mc.business.inventory["stock"]["serum"],mc.business.inventory["sale"]["serum"],"Production Stockpile","Sales Stockpile")
    $ renpy.block_rollback()
    show screen main_ui
    show screen business_ui
    return

label set_autosell_action_description:
    $ amount = renpy.input("How many units of %(name)s would you like to keep in stock? Extra will automatically be moved to the sales department." % mc.business.production.serum)
    $ amount = amount.strip()
    while not (amount.isdigit() and int(amount) >= 0):
        $ amount = renpy.input("Please put in positive integer value.")
    $ amount = int(amount)

    $ mc.business.production.auto_sell_threshold = amount
    $ renpy.say("", "Extra doses of the serum %(name)s will be automatically moved to the sales department now." % mc.business.production.serum)
    return


label pick_supply_goal_action_description:
    $ amount = renpy.input("How many units of serum supply would you like your supply procurement team to keep stocked?")
    $ amount = amount.strip()

    while not amount.isdigit():
        $ amount = renpy.input("Please put in an integer value.")

    $ amount = int(amount)
    $ mc.business.supply.goal = amount
    if amount <= 0:
        "You tell your team to keep [amount] units of serum supply stocked. They question your sanity, but otherwise continue with their work. Perhaps you should use a positive number."
    else:
        "You tell your team to keep [amount] units of serum supply stocked."

    return

label move_funds_action_description:
    menu:
        "Move funds from the company to yourself." if mc.business.funds>0:
            $ src = mc.business.funds
            $ tgt = mc.money
        "Move funds from yourself into the company." if mc.money>0:
            $ tgt = mc.business.funds
            $ src = mc.money
        "Do nothing.":
            return
    $ amount = renpy.input("How much would you like to exchange? (You currently have $[mc.money], the company has $[mc.business.funds].)")
    $ amount.strip()
    while (not amount.isdigit() or int(amount) > mc.money):
        $ amount = renpy.input("Please put in a positive value equal to or lower than the current funds in the business account. (Currently has $[mc.money])")
        $ amount.strip()

    $ src += int(amount)
    $ tgt -= int(amount)
    return
label policy_purchase_description:
    call screen policy_selection_screen()
    return
#
#label set_job_opening_description:
#    menu:

label set_uniform_description:
    "Which division do you want to set the uniform for?"
    python:
        tuple_list = [("All", "All")]
        for div in mc.business.division:
            tuple_list.append((div.name, div))

        selected_div = renpy.display_menu(tuple_list,True,"Choice")

    call screen outfit_select_manager(mc.business.get_max_outfits_to_change())

    python:
        if _return != "No Return":
            if selected_div in mc.business.division:
                div.uniform = _return
            else:
                for div in mc.business.division:
                    div.uniform = _return
    return

label set_serum_description:
    "Which divisions would you like to set a daily serum for?"
    python:
        tuple_list = [("All", "All")]
        for div in mc.business.division:
            tuple_list.append((div.name, div))

        selected_div = renpy.display_menu(tuple_list,True,"Choice")
    menu:
        "Pick a new serum.":
            call screen serum_inventory_select_ui(mc.business.inventory["stock"]["serum"])
            $ selected_serum = _return

        "Clear existing serum.":
            $ selected_serum = None

    python:
        if selected_serum != "None": #IF we didn't select an actual serum, just return and don't chagne anything.
            if selected_div in mc.business.division:
                selected_div.serum = selected_serum
            else:
                for div in mc.business.division:
                    div.serum = selected_serum
    return
