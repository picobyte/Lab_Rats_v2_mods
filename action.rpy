init -20 python:
    # Rooms have actions

    class Action(renpy.store.object): #Contains the information about actions that can be taken in a room. Dispayed when you are asked what you want to do somewhere.
        # Also used for crises, those are not related to any partiular room and are not displayed in a list. They are forced upon the player.
        def __init__(self,name,requirement,effect,args=None):
            self.name = name
            self.requirement = requirement #requirement should be a function that has already been defined. Yay functional programming!
            self.effect = effect
            self.args = args or [] #stores any arguments that we want passed to the action or requirement when the action is created. Should be a list of variables.

        def __cmp__(self,other): ##This and __hash__ are defined so that I can use "if Action in List" and have it find identical actions that are different instances.
            if type(other) is Action:
                if self.name == other.name and self.requirement == other.requirement and self.effect == other.effect and self.args == other.args:
                    return 0

            return -1 if self.__hash__() < other.__hash__() else 1 #Use hash values to break ties.

        def __hash__(self):
            return hash((self.name,self.requirement,self.effect,self.args))

        def check_requirement(self): #Calls the function that was passed to the action when it was created. Currently can only use global variables, will change later to take arbitrary list.
            return self.requirement(*self.args)

        def call_action(self): #Can only use global variables. args is a list of elements you want to include as arguments. None is default
            if self.args is None:
                renpy.call(self.effect)
            else:
                renpy.call(* [self.effect] + self.args)
            renpy.return_statement()

    ##Initialization of requirement functions go down here.##
    def sleep_action_requirement():
        return time_of_day == 4

    def faq_action_requirement():
        return True

    def hr_work_action_requirement():
        return time_of_day < 4

    def research_work_action_requirement():
        if time_of_day < 4:
            return mc.business.active_research_design != None
        else:
            return False

    def supplies_work_action_requirement():
        return time_of_day < 4

    def market_work_action_requirement():
        return time_of_day < 4

    def production_work_action_requirement():
        if time_of_day < 4:
            return mc.business.serum_production_target != None
        else:
            return False

    def interview_action_requirement():
        return time_of_day < 4

    def serum_design_action_requirement():
        return time_of_day < 4

    def research_select_action_requirement():
        return True

    def production_select_action_requirement():
        return True

    def trade_serum_action_requirement():
        return True

    ef sell_serum_action_requirement():
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
        return strict_uniform_policy in mc.business.active_policies

    def set_serum_requirement():
        return daily_serum_dosage_policy in mc.business.active_policies

    ##Actions##
    hr_work_action = Action("Spend time orgainizing your business.", "hr_work_action_description", hr_work_action_requirement)
    research_work_action = Action("Spend time researching in the lab.", "research_work_action_description", research_work_action_requirement)
    supplies_work_action = Action("Spend time ordering supplies.", "supplies_work_action_description", supplies_work_action_requirement)
    market_work_action = Action("Spend time shipping doses of serum marked for sale.", "market_work_action_description", market_work_action_requirement)
    production_work_action = Action("Spend time producing serum in the lab.", "production_work_action_description", production_work_action_requirement)

    interview_action = Action("Hire someone new.", "interview_action_description",  interview_action_requirement)
    design_serum_action = Action("Create a new serum design.", "serum_design_action_description",  serum_design_action_requirement)
    pick_research_action = Action("Pick a new research topic.", "research_select_action_description",  research_select_action_requirement)
    pick_production_action = Action("Change production to a new serum.", "production_select_action_description",  production_select_action_requirement)
    pick_supply_goal_action = Action("Set the amount of supply you would like to maintain.", "pick_supply_goal_action_description",  pick_supply_goal_action_requirement)
    move_funds_action = Action("Siphon money into your personal account.", "move_funds_action_description",  move_funds_action_requirement)
    policy_purhase_action = Action("Purchase new business policies.", "policy_purchase_description",  policy_purchase_requirement)

    trade_serum_action = Action("Trade serums between yourself and the business inventory.", "trade_serum_action_description",  trade_serum_action_requirement)
    sell_serum_action = Action("Mark serum to be sold.", "sell_serum_action_description",  sell_serum_action_requirement)
    set_autosell_action = Action("Set autosell threshold.", "set_autosell_action_description",  set_autosell_action_requirement)

    sleep_action = Action("Go to sleep for the night.", "sleep_action_description", sleep_action_requirement)
    faq_action = Action("Check the FAQ.", "faq_action_description", faq_action_requirement)

    set_uniform_action = Action("Set Employee Uniforms", "set_uniform_description", set_uniform_requirement)
    set_serum_action = Action("Set Daily Serum Doses", "set_serum_description", set_serum_requirement)

init:

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
        "Nevermind.":
            pass
    return

label serum_design_action_description:
    $counter = len(list_of_traits)
    hide screen main_ui
    hide screen business_ui
    call screen serum_design_ui(SerumDesign(),[]) #This will return the final serum design, or None if the player backs out.
    show screen main_ui
    show screen business_ui
    if _return != "None":
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
    if _return != "None":
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
    if _return != "None":
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
    python:
        tuple_list = [("All", "All")]
        for div in mc.business.division:
            tuple_list.append((div.name, div))

        selected_div = renpy.display_menu(tuple_list,True,"Choice")

    call screen outfit_select_manager(mc.business.get_max_outfits_to_change())

    python:
        if _return != "No Return":
            if isinstance(selected_div, Division):
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
            call screen serum_inventory_select_ui(mc.business.inventory)
            $ selected_serum = _return

        "Clear existing serum.":
            $ selected_serum = None

    python:
        if selected_serum != "None": #IF we didn't select an actual serum, just return and don't chagne anything.
            if isinstance(selected_div, Division):
                selected_div.serum = selected_serum
            else:
                for div in mc.business.division:
                    div.serum = selected_serum
    return
