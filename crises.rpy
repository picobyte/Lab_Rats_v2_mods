## This file holds all of the descriptions for the crises that can (and will) arise during play.
## They are instances of the Action class and hold:
## 1) A name and/or short description. Unlikely to ever be publically shown for these events
## 2) A requirement function. Used to determine if the crisis is possible.
## 3) An effect label. Points towards a label that will run the actual event, compute final effects, and take input from the player.


#Key things to to keep in mind right now: TODO: Remove this list once we're done implimenting stuff
## Potential new crises ##
# Girl is seen not wearing uniform - Leads to potential for punishment (level of punishment might depeond on other corporate policies)
# Serum flaw is discovered (TODO: introduce serum flaw traits that are sometimes randomly added!)
# High volume buyer comes by and wants to be impressed.


## Potential Policies ##
# Optional in house serum testing - Gives the ability to give girls serum, for a cash reward.
# Business size policies - Increase the total number of employees you can have working for you at once.
# Efficency policies - Lets you increase the general efficency of your company, making HR even more useful.
# R&D connections - Unlocks certain key traits for R&D (ie. game is gated behind earning money).
# Discount suppliers - Decreases price paid for serum supplies.


## Crises are stored in a weighted list, to be polled each turn to see if something triggers (and if so, what).

init 1 python:
    crisis_list = [] #To be filled with tuples of [Action, weight]. Weights are relative to other entries in the list.
    
    def in_research_with_other(): #A common requirement check, the PC is in the office (not nessesarily the lab), during work hours, with at least one other person.
        if world.is_work_time(): #Only trigger if people are in the office.
            if mc.is_at_work(): #Check to see if the main character is at work
                if len(mc.business.r_div.people) > 0: #Check to see if there's at least one person in the research team team at work and that something is being researched.
                        return True
        return False
            
    def in_production_with_other():
        if world.is_work_time(): #Only trigger if people are in the office.
            if mc.is_at_work(): #Check to see if the main character is at work
                if len(mc.business.p_div.people) > 0: #Check to see if there's at least one person in the research team team at work and that something is being researched.
                        return True
        return False
        
    def anyone_else_in_office(): #Returns true if there is anyone else at work with the mc.
        if world.is_work_time():
            if mc.is_at_work():
                if mc.business.get_employee_count() > 0:
                    return True
        return False

    def mc_asleep(): #Returns true if the main character is at home and in bed.
        return world.time_of_day == 4 and mc.location == world.bedroom #It has to be after work, right when you've gone to bed.


    #Defining the requirement to be tested.
    def broken_AC_crisis_requirement():
        if world.is_work_time(): #Only trigger if people are in the office.
            if mc.is_at_work(): #Check to see if the main character is at work
                if len(mc.business.p_div.people) > 0: #Check to see if there's at least one person in the production team at work.
                    return True
        return False
            
    broken_AC_crisis = Action("Crisis Test",broken_AC_crisis_requirement,"broken_AC_crisis_label")
    crisis_list.append([broken_AC_crisis,5])
    
    
    
label broken_AC_crisis_label:
    $ temp_sluttiness_increase = 20 #This is a bonus to sluttiness when stripping down because of the heat.
    
    "There is a sudden bang in the office, followed by a strange silence. A quick check reveals the air conditioning has died!"
    "The machines running at full speed in the production department kick out a significant amount of heat. Without air condition the temperature quickly rises to uncomfortable levels."
    $ renpy.show(mc.business.p_div.name,what=mc.business.p_div.background_image) #Just in case another crisis had interupted us being here.
    "The air conditioner was under warranty, and a quick call has one of their repair men over in a couple of hours. Until then, the production staff want to know what to do."
    menu:
        "Take a break.":
            "You tell everyone in the production lab to take a break for a few hours while the air conditioning is repaired."
            "The unexpected break raises moral and makes the production staff feel more independent."
            python:
                for person in mc.business.p_div.people:
                    person.happiness += 5
                    person.change_obedience_modified(-5)
            "The repair man shows up early and it turns out to be an easy fix. The lab is soon back up and running."
            
        "It's not that hot, get back to work!":
            "Nobody's happy working in the heat, but exercising your authority will make your production staff more likely to obey in the future."
            python:    
                for person in mc.business.p_div.people:
                    person.change_happiness(-5)
                    person.change_obedience_modified(5)
            "The repair man shows up early and it turns out to be an easy fix. The lab is soon back up and running."    
                
        "Tell everyonyone to strip down and keep working.":
            if len(mc.business.p_div.people) > 1: #We have more than one person, do a group strip scene.
                mc.name "I know it's uncomfortable in here right now, but we're just going to have to make due."
                mc.name "If anyone feels the need to take something off to get comfortable, I'm lifting the dress code until the air conditioning is fixed."
                #We're going to use the most slutty girl of the group lead the pack. She'll be the one we pay attention to.
                python:
                    the_person = None
                    for girl in mc.business.p_div.people:
                        if not the_person:
                            the_person = girl
                        else:
                            if girl.sluttiness > the_person.sluttiness:
                                the_person = girl
                
                $ the_person.draw_person()                
                if the_person.sluttiness < 20: #TODO: Link this to personalities somehow.
                    the_person.name "He's got a point girls. Come on, we're all adults here."
                elif the_person.sluttiness < 60:
                    the_person.name "He's got a point girls. I'm sure we've all shown a little bit of skin before anyways, right?"
                else:
                    the_person.name "Let's do it girls! I can't be the only one who loves an excuse to flash her tits, right?"
                
            else: #There's just one person here, have them strip down.
                $ the_person = mc.business.p_div.people[0] #Get the one person, the crisis requires we have at least 1 person in here so this should always be true.
                $ the_person.draw_person()
                mc.name "[the_person.name], I know it's uncomfortable in here right now, but we're going to have to make due."
                mc.name "If you feel like it would help to take something off, I'm lifting the dress code until the air condition is fixed."
                if the_person.sluttiness < 20:
                    the_person.name "Taking some of this off would be a lot more comfortable..."
                else:
                    the_person.name "I might as well, a little skin never hurt anyone, right?"
                
            #First, we'll get a copy of the lead girls outfit to use as a tester.
            $ test_outfit = copy.deepcopy(the_person.outfit) #We take a deep copy so we don't change the original she's currently wearing.
            #Next, we start by trying to remove her outermost top layer.
            
            #The following section is kind of a mess. We are keeping two outfits that should, if everything is done correctly, mirror eachother.
            #test_outfit_top and _bottom are lists of the top and bottom items being worn. They are removed one at a time from the test_outfit.
            #That is then used to judge if the girl thinks the outfit is too slutty or not.
            #Because we are editing these outfits as we go, we want to get the -2 index of _top and _bottom, but only remove the top piece of clothing from the list.
            #Note: might break if they aren't wearin anything already.
            
            $ test_outfit_top = test_outfit.get_upper_ordered()
            $ test_outfit_bottom = test_outfit.get_lower_ordered()
            $ removed_something = False
            if len(test_outfit_top) > 0:
                $ the_clothing = test_outfit_top[-1]
                $ test_outfit.remove_clothing(the_clothing)
                if the_person.judge_outfit(test_outfit,temp_sluttiness_increase): #Judge her outfit without a top with bonus sluttiness modifier for the heat.
                    $ the_person.outfit.remove_clothing(the_person.outfit.get_upper_ordered()[-1])
                    "[the_person.name] pulls off her [the_clothing.name] and hangs it over her chair."
                    $ removed_something = True
                    $ the_person.draw_person()
            
            if len(test_outfit_bottom) > 0 and len(the_person.outfit.get_lower_ordered()) > 0:
                $ the_clothing = test_outfit_bottom[-1]
                $ test_outfit.remove_clothing(the_clothing)
                if the_person.judge_outfit(test_outfit,temp_sluttiness_increase):
                    $ the_person.outfit.remove_clothing(the_person.outfit.get_lower_ordered()[-1])
                    if removed_something:
                        "Then she pulls off her [the_clothing.name] and adds it to the pile."
                    else:
                        "[the_person.name] pulls off her [the_clothing.name] and hangs it over her chair."
                    $ removed_something = True
                    $ the_person.draw_person()
            
            #Now we see if she'll pull off one more layer, which is usually her underwear. After all this we'll do a state check on her and narrate a little bit.
            if len(test_outfit_top) > 1:
                $ the_clothing = test_outfit_top[-2]
                $ test_outfit.remove_clothing(the_clothing)
                if the_person.judge_outfit(test_outfit,temp_sluttiness_increase): #Judge her outfit without a top with bonus sluttiness modifier for the heat.
                    $ the_person.outfit.remove_clothing(the_person.outfit.get_upper_ordered()[-1])
                    "[the_person.name] doesn't stop there. Next she takes off her [the_clothing.name]."
                    $ removed_something = True
                    $ the_person.draw_person()
                    
            if len(test_outfit_bottom) > 1 and len(the_person.outfit.get_lower_ordered()) > 0:
                $ the_clothing = test_outfit_bottom[-2]
                $ test_outfit.remove_clothing(the_clothing)
                if the_person.judge_outfit(test_outfit,temp_sluttiness_increase):
                    $ the_person.outfit.remove_clothing(the_person.outfit.get_lower_ordered()[-1])
                    "Finally she slips off her [the_clothing.name] and puts it with the rest of her outfit."
                    $ removed_something = True
                    $ the_person.draw_person()
            
            if removed_something:
                if the_person.outfit.tits_visible() and the_person.outfit.vagina_visible():
                    "Once she's done stripping [the_person.name] is practically naked."
                elif the_person.outfit.tits_visible():
                    "Once she's done stripping [the_person.name] has her nice [the_person.tits] tits out on display."
                elif the_person.outfit.vagina_visible():
                    "Once she's done stripping [the_person.name] has her pretty little pussy out on display for everyone."
                else:
                    "[the_person.name] finishes stripping and looks back at you."
                the_person.name "Ahh, that's a lot better."
            else:
                "[the_person.name] fiddles with some of her clothing, then shrugs."
                the_person.name "I'm not sure I'm comfortable taking any of this off... I'm sure I'll be fine in the heat for a little bit."
            
            if len(mc.business.p_div.people) > 1:
                if removed_something:
                    "The rest of the department follows the lead of [the_person.name], stripping off various amounts of clothing."
                    "The girls laugh and tease each other as they strip down, and they all seem to be more comfortable less clothed."
                    "The repair man shows up early, and you lead him directly to the the AC unit. The problem turns out to be a quick fix, and production is back to a comfortable temperature within a couple of hours."
                else:
                    "The other girls exchange glances, and everyone seems decides it's best not to take this too far."
                    "They get back to work fully dressed, and soon the repair man has shown up. The problem turns out to be a quick fix, and production is back to a comfortable temperature within a couple of hours."
            else:
                if removed_something:
                    "[the_person.name] gets back to work. Working in her stripped down attire seems to make her more comfortable with the idea in general."
                    "The repair man shows up early, and you lead him directly to the AC unit. The problem turns out to be a quick fix, and production is back to a comfortable temperature within a couple of hours."
                else:
                    "[the_person.name] gets back to work, still fully clothed."
                    "The repair man shows up early, and you lead him directly to the the AC unit. The problem turns out to be a quick fix, and production is back to a comfortable temperature within a couple of hours."
                    
            if removed_something:
                python:
                    for person in mc.business.p_div.people:
                        person.change_slut_modified(10)
    $renpy.scene("Active")
    return
    
init 1 python:
    def special_training_requirement():
        if mc.business.get_employee_count() > 0: #As long as you have at least one person working for you.
            if world.is_work_time(): # Only triggers during the world.day when people are working.
                return True
    
    special_training_crisis = Action("Special Training Crisis",special_training_requirement,"special_training_crisis_label")
    crisis_list.append([special_training_crisis,5])
    
label special_training_crisis_label():
    if not mc.business.get_employee_count() > 0:
        return #We must have had someone quit or be fired, so we no longer can get a random person.
        
    $ the_person = renpy.random.choice(mc.business.get_employee_list())
    show screen person_info_ui(the_person)
    hide screen business_ui
    "You get an email from [the_person.name]."
    the_person.name "[mc.name], I've just gotten word about a training seminar going on right now a few blocks away. I would love to take a trip over and see if there is anything I could learn."
    the_person.name "There's a sign up fee of $500. If you can cover that, I'll head over right away."
    menu:
        "Send [the_person.name] to the Seminar. -$500" if mc.business.funds >= 500:
            $ mc.business.funds += -500
            "You type up a response."
            mc.name "That sounds like a great idea. I'll call and sort out the fee, you start heading over."
            the_person.name "Understood, thank you sir! What would you like me to focus on?"
            menu:
                "Improve HR Skill (Current [the_person.hr_skill])":
                    $ the_person.hr_skill += 2
                    show screen float_up_screen(["+2 HR Skill"],["float_text_grey"])
                    "[the_person.name] leaves work for a few hours to attend the training seminar. When she comes back she has learned several useful business structuring techniques."
                                        
                "Improve Marketing Skill (Current [the_person.market_skill])":
                    $ the_person.market_skill += 2
                    show screen float_up_screen(["+2 Marketing Skill"],["float_text_grey"])
                    "[the_person.name] leaves work for a few hours to attend the training seminar. When she comes back she is far more familiar with local market demands."
                                        
                "Improve Researching Skill (Current [the_person.research_skill])":
                    $ the_person.research_skill += 2
                    show screen float_up_screen(["+2 Researching Skill"],["float_text_grey"])
                    "[the_person.name] leaves work for a few hours to attend the training seminar. When she comes back she has several interesting new researching technqiues to test."
                                        
                "Improve Production Skill (Current [the_person.production_skill])":
                    $ the_person.production_skill += 2
                    show screen float_up_screen(["+2 Production Skill"],["float_text_grey"])
                    "[the_person.name] leaves work for a few hours to attend the training seminar. When she comes back she has a few new ideas for streamlining production."
                                    
                "Improve Supply Skill (Current [the_person.supply_skill])":
                    $ the_person.supply_skill += 2
                    show screen float_up_screen(["+2 Supply Skill"],["float_text_grey"])
                    "[the_person.name] leaves work for a few hours to attend the training seminar. When she comes back she is far more familiar with local suppliers and their goods."
                    
            
        "Tell her to stay at work.":
            "You type up a response."
            mc.name "I'm sorry [the_person.name], but there aren't any extra funds in the budget right now."
            the_person.name "Noted, maybe some other time then."
            
    return
    
init 1 python:
    def lab_accident_requirement():
        if in_research_with_other():
            if mc.business.active_research_design and "value" in mc.business.active_research_design:
                return True
        return False
        
    lab_accident_crisis = Action("Lab Accident Crisis",lab_accident_requirement,"lab_accident_crisis_label")
    crisis_list.append([lab_accident_crisis,5])
    
label lab_accident_crisis_label():
    ## Some quick checks to make sure the crisis is still valid (for example, a serum being finished before this event can trigger)
    if not (mc.business.active_research_design and mc.business.is_reasearching_drug()):
        return

    $ the_serum = mc.business.active_research_design
    $ the_person = renpy.random.sample(mc.business.r_div.people, 1)[0]
    
    if mc.location == world.rd_room:
        call change_location(world.rd_room) from _call_lab_accident_1
        "There's a sudden crash and sharp yell of suprise as you're working in the lab."
        $the_person.call_suprised_exclaim()
        the_person.name "[mc.name], I think I need you for a moment."
        
        
    else:
        "Your phone buzzes - it's a text from [the_person.name] on your research team."
        the_person.name "There's been a small accident, can I see you in the lab?"
        "You hurry over to your research and development lab to see what the problem is."
        call change_location(world.rd_room) from _call_lab_accident_2
    
    
    $ the_person.draw_person(emotion = "sad")
    show screen person_info_ui(the_person)
    hide screen business_ui
    "You get to [the_person.name]'s lab bench. There's a shattered test tube still on it and a pool of coloured liquid."
    mc.name "What happened?"
    $ techno = renpy.random.choice(Person.technobabble_list)
    the_person.name "I was trying to [techno] and went to move the sample. It slipped out of my hand and when I tried to grab it..."
    "She turns her palm up to you. It's covered in the same coloured liquid, and there's a small cut."
    the_person.name "I'm not sure what the uptake is like with this new design. I think everything will be fine, but would you mind hanging around for a few minutes?."
    $the_person.give_serum(copy.copy(the_serum))
    call talk_person(the_person) from _call_talk_person_5
    "It doesn't seem like [the_person] is having any unexpected affects from the dose of serum, so you return to your work."
    return
    
init 1 python:
    def production_accident_requirement():
        if in_production_with_other():
            if mc.business.serum_production_target: #Check to see if there's at least one person in the production department and that we're serum right now.
                return True
        return False
        
    production_accident_crisis = Action("Production Accident Crisis",production_accident_requirement,"production_accident_crisis_label")
    crisis_list.append([production_accident_crisis,5])
        
        
label production_accident_crisis_label():
    ## Some quick checks to make sure the crisis is still valid (for example, a serum being finished before this event can trigger)
    if not mc.business.serum_production_target:
        return
        
    $ the_serum = mc.business.serum_production_target
    $ the_person = renpy.random.sample(mc.business.p_div.people, 1)[0]
    
    if mc.location == world.p_room:
        call change_location(world.p_room) from _call_production_accident_1
        "There's a sudden crash and sharp yell of suprise as you're working in the lab."
        $the_person.call_suprised_exclaim()
        the_person.name "[mc.name], I think I need you for a moment."
        
        
    else:
        "Your phone buzzes - it's a text from [the_person.name] on your production team."
        the_person.name "There's been a small accident, can I see you in the lab?"
        "You hurry over to the production lab to see what the problem is."
        call change_location(world.p_room) from _call_production_accident_2
    
    
    $ the_person.draw_person(emotion = "sad")
    show screen person_info_ui(the_person)
    hide screen business_ui
    "You get to [the_person.name]'s lab bench. There's a collection of shattered test tubes still on it and a pool of coloured liquid."
    mc.name "What happened?"
    $ techno = renpy.random.choice(Person.technobabble_list)
    the_person.name "I was trying to [techno]like I normally do and went to move the batch. It slipped out of my hand and when I tried to grab it..."
    "She turns her palm up to you. It's covered in the same coloured liquid, and there's a small cut."
    the_person.name "I'm not sure what the uptake is like with this new design. I think everything will be fine, but would you mind hanging around for a few minutes?."
    $the_person.give_serum(copy.copy(the_serum))
    call talk_person(the_person) from _call_talk_person_6
    "It doesn't seem like [the_person.name] is having any unexpected affects from the dose of serum, so you return to your work."
    return
    
init 1 python:
    def water_spill_crisis_requirement():
        return anyone_else_in_office()
    
    water_spill_crisis = Action("Water Spill Crisis",water_spill_crisis_requirement,"water_spill_crisis_label")
    crisis_list.append([water_spill_crisis,5]) 
    
        
label water_spill_crisis_label():
    $ the_person = renpy.random.choice(mc.business.get_employee_list())
    $ ordered_top = the_person.outfit.get_upper_ordered()
    if len(ordered_top) == 0:
        return #She's not wearing a top, we can't exactly spill water on nothing!
    else:
        $ the_clothing = the_person.outfit.get_upper_ordered()[-1] #Get the very top item of clothing.
        
    
    "You're hard at work when [the_person.name] comes up to you. She's got her phone clutched in one hand, a water bottle in the other."
    $ the_person.draw_person()
    show screen person_info_ui(the_person)
    hide screen business_ui
    $ the_person.call_greeting()
    mc.name "Hey [the_person.name], how can I help you?"
    the_person.name "I had a few questions about how my taxes were going to be calculated this year, and I was hoping you could answer some of them."
    "You listen as [the_person.name] dives into her tax situation. You aren't paying a terrible amount of attention until she goes to take a drink from her water bottle and dumps it down her front!"
    $ dry_colour = the_clothing.colour
    $ wet_colour = copy.copy(dry_colour)
    
    $ wet_colour[3] = 0.93 * wet_colour[3]
    $ the_clothing.colour = wet_colour
    $ the_person.draw_person(emotion="angry")
    $ the_person.call_suprised_exclaim()
    "She tries to wipe the water off, but not before it's soaked through the front of her [the_clothing.name]."
    $ test_outfit = copy.deepcopy(the_person.outfit) #Make a copy, we'll try removing the wet item and reevaluating.
    $ test_outfit.remove_clothing(the_clothing)
    $ thinks_appropriate = the_person.judge_outfit(test_outfit,15) #Does she think it's appropriate to strip off her top when it's wet?
    if not thinks_appropriate:
        the_person.name "I'm so sorry about this [mc.name], I just... I just need to go and dry this off!"
        $ renpy.scene("Active")
        "[the_person.name] runs off towards the bathroom."
        $ the_clothing.colour = dry_colour
        "After a few minutes she's back, with her [the_clothing.name] dried off and no longer transparent."
        $ the_person.draw_person()
        $ change_amount = the_person.change_slut(1)
        show screen float_up_screen(["+1 Sluttiness"],["float_text_pink"])
        the_person.name "Ugh, that was so embarrasing. Lets just forget about that, okay?"
        mc.name "Of course, back to your taxes then, right?"
        "You help [the_person.name] sort out their tax issues, then get back to work."
    else:
        $ thinks_appropriate = the_person.judge_outfit(test_outfit) #Does she think it's appropriate to just strip it off all of the time?
        if not thinks_appropriate:
            the_person.name "I'm so sorry about this [mc.name]. Let me just take this off, you keep talking."
            $ the_person.outfit.remove_clothing(the_clothing)
            $ the_person.draw_person()
            if the_person.outfit.tits_visible():
                "[the_person.name] strips off her [the_clothing.name], letting you get a nice good look at her [the_person.tits] sized tits."
            else:
                "[the_person.name] strips off her [the_clothing.name] and puts it to the side, then turns her attention back to you."
            mc.name "Right, your taxes..."
            "You help [the_person.name] with her tax questions. Once you're done talking she dries her top off and gets back to work."
            $ the_clothing.colour = dry_colour
            $ the_person.outfit.add_upper(the_clothing)
            
        else:
            the_person.name "I'm so sorry about this [mc.name], should I go dry this off first?"
            menu:
                "Dry it off now.":
                    mc.name "You go dry it off, I'll wait here for you."
                    the_person.name "I'll be back as soon as I can."
                    $ renpy.scene("Active")
                    "[the_person.name] runs off towards the bathroom."
                    $ the_clothing.colour = dry_colour
                    "After a few minutes she's back, with her [the_clothing.name] dried off and no longer transparent."
                    $ the_person.draw_person()
                    $ the_person.change_slut(1)
                    show screen float_up_screen(["+1 Sluttiness"],["float_text_pink"])
                    the_person.name "Ugh, that was so embarrasing. Lets just forget about that, okay?"
                    mc.name "Of course, back to your taxes then, right?"
                    "You help [the_person.name] sort out their tax issues, then get back to work."
                    
                "Leave it alone.":
                    mc.name "I'd like to get back to work as quickly as possible, just leave it for now and you can dry it off later."
                    if test_outfit.tits_visible():
                        "[the_person.name] looks down at her transparent top, then nods and continues on about her taxes. Getting a good look at her tits makes the boring topic much more interesting."
                    else:
                        "[the_person.name] looks down at her top, then nods and continues. At least the transparent clothing helps make the boring topic more interesting."
                    $ the_person.change_obedience(1)
                    $ the_person.change_slut(1)
                    show screen float_up_screen(["+1 Sluttiness","+1 Obedience"],["float_text_pink", "float_text_grey"])
                    "After a few minutes you've answered all of [the_person.name]'s questions, and she heads off to dry her [the_clothing.name] off."
                    $ the_clothing.colour = dry_colour
                    
                "Take it off.":
                    mc.name "I'm really quite busy right now, just take it off now and you can dry it off later."
                    the_person.name "I... Okay, fine. I really need your help on this."
                    $ the_person.outfit.remove_clothing(the_clothing)
                    $ the_person.draw_person()                    
                    $ the_person.change_happiness(-5)
                    $ the_person.change_slut(2)
                    $ the_person.change_obedience(2)
                    show screen float_up_screen(["-5 Happiness","+2 Sluttiness","+2 Obedience"],["float_text_yellow","float_text_pink","float_text_grey"])
                    "[the_person.name] clearly isn't happy, but she takes off her [the_clothing.name] and resumes talking about her taxes."
                    if test_outfit.tits_visible():
                        "Getting a good look at her tits makes the boring topic much more interesting. After a few minutes you've sorted out her problems. She goes to dry her top while you get back to work."
                    else:
                        "You spend a few minutes and sort out all of her problems. When you're done she goes off to dry her top while you get back to work."
                    $ the_clothing.colour = dry_colour
                    $ the_person.outfit.add_upper(the_clothing)
    
    $ renpy.scene("Active")
    return
    
init 1 python:
    def home_fuck_crisis_requirement():
        if mc_asleep():
            if mc.business.get_max_employee_slut()>=15: #We need them to start with at least sluttiness 15 so a bonus and some foreplay will get you up to sex range.
                return True
        return False
        
    home_fuck_crisis = Action("Home Fuck Crisis",home_fuck_crisis_requirement,"home_fuck_crisis_label")
    crisis_list.append([home_fuck_crisis,5]) 
        
label home_fuck_crisis_label():
    ## A horny employee comes to your house at night and wants you to fuck them. They're drunk, with bonus sluttiness, and will tkae a pay cut if you make them cum.
    $ meets_sluttiness_list = []
    python:
        for person in mc.business.get_employee_list():
            if person.sluttiness >= 15:
                meets_sluttiness_list.append(person)
    $ the_person = renpy.random.choice(meets_sluttiness_list)
    
    "Some time late in the night, you're awoken by the buzz of your phone getting a text. You roll over and ignore it."
    "A few minutes later your doorbell goes off several times in quick succession."
    "You finally drag yourself out of bed and peek out a window to see who's at your door."   
    $ the_person.draw_person(emotion = "happy") #TODO: Create a set of late night outfits that she can be wearing.
    $ the_person.sluttiness += 20
    show screen person_info_ui(the_person)
    hide screen business_ui
    "You see [the_person.name] standing outside. She buzzes your door bell again, then checks her phone. You open up the door."
    mc.name "[the_person.name], what are you doing here? It's the middle of the night."
    "[the_person.name] takes a step towards you, running a hand down your chest."
    the_person.name "Oh [mc.name], I just had the worst night and I need you to help me!"
    "You can smell alcohol on her breath."
    the_person.name "I was out with some friends, and I got talking with this guy..."
    "She steps fully into your house and drops her purse at the side of the door." #TODO: Have girls have relationships like married, mother, etc. This event should "respect" marriages.
    the_person.name "We were getting along so well, so I went home with him. Well, we get to his place and make out in his car for a while..."
    "You stay silent, listening to [the_person.name]'s rambling story."
    $ the_person.draw_person(emotion = "angry")
    the_person.name "Then he tells me he's married and his wife is home! So he calls me a cab and leaves me all alone! Worst of all, he left me so fucking horny!"
    "[the_person.name] takes a not very subtle look at your crotch."
    the_person.name "So I though, who do I know who could help me out here? Your name was the first on the list."
    $ the_person.draw_person(emotion = "happy")
    "She places her hands on your hips and steps close."
    the_person.name "Can you help me? I need you to make me cum so fucking badly right now..."
    menu:
        "Fuck her.":
            call fuck_person(the_person) from _call_fuck_person_4
            #Now that you've had sex, we calculate the change to her stats and move on.
            $ change_amount = the_person.change_slut_modified(the_person.arousal) #Change her slut score by her final arousal. This should be _about_ 100 if she climaxed, but you may keep fucking her silly if you can overcome the arousal loss.
            show screen float_up_screen(["+[change_amount] Sluttiness"],["float_text_pink"])
            if the_person.arousal > 100:
                $ the_person.change_obedience(1)
                show screen float_up_screen(["+1 Obedience"],["float_text_grey"])
                the_person.name "Mmm, that was just what I needed [mc.name]. Ah..."
                "You and [the_person.name] lounge around for a few minutes until she has completely recovered."
                the_person.name "I had a great time [mc.name], but I should be getting home. Could you call me a cab?"
                
            else:
                $ the_person.change_obedience(-2)
                $ the_person.change_happiness(-5)
                show screen float_up_screen(["-2 Obedience","-2 Happiness"],["float_text_grey","float_text_yellow"])
                the_person.name "Ugh, fuck! This is worse than it was before! Screw it, I'll take care of this at home. Call me a cab, please."
            
            $ the_person.reset_arousal()
            $ renpy.scene("Active")
            "A few minutes later [the_person.name] is gone, and you're able to get back to bed."
            
        "Ask her to leave.":
            mc.name "[the_person.name], you're drunk and not thinking straight. I'll call you a cab to get you home, in the morning this will all seem like a bad idea."
            $ the_person.draw_person(emotion = "sad")
            the_person.name "Really? Oh come on, I need you so badly though..."
            "You place your hands on [the_person.name]'s shoulders and keep her at arms length."
            mc.name "Trust me, it's for the best."
            $ the_person.change_obedience(1)
            show screen float_up_screen(["+1 Obedience"],["float_text_grey"])
            "You call a cab for [the_person.name] and get her sent home. She might not thank you for it, but she'll be more likely to listen to you from now on."
    
    
    $ the_person.sluttiness += -20
    return
    
init 1 python:
    def quiting_crisis_requirement(): #We are only going to look at quitting actions if it is in the middle of the world.day when people are at work.
        if world.time_of_day == 1 or world.time_of_day == 2 or world.time_of_day==3:
            return True
        else:
            return False
            
label quitting_crisis_label(the_person): #The person tries to quit, you have a chance to keep her around for a hefty raise (Or by fucking her, if her sluttiness is high enough).
    if not mc.business.is_employee(the_person):
        return #They're already not employed now, just return and go about your business.
    
    if the_person.get_job_happiness_score() >= 0:
        return #They've become happy with their job, so just clear this from the list and move on. They don't actually quit.
    
    "Your phone buzzes, grabbing your attention. It's an email from [the_person.name], marked \"Urgent, need to talk\"."
    "You open up the email and read through the body."
    the_person.name "[mc.name], there's something important I need to talk to you about. When can we have a meeting?"
    if mc.location == world.office: #If you're arleady in your office just kick back and relax.
        call change_location(world.office) from _call_quitting_crisis_1 #Just in case another crisis had interupted us being here.
        "You type up a response."
        mc.name "I'm in my office right now, come over whenever you would like."
        "You organize the papers on your desk while you wait for [the_person.name]. After a few minutes she comes in and closes the door behind her."
    else:
        "You type up a response."
        mc.name "I'm out of the office right now, but if it's important I can be back in a few minutes."
        the_person.name "It is. See you at your office."
        call change_location(world.office) from _call_quitting_crisis_2 #Just in case another crisis had interupted us being here.
        "You travel back to your office. You're just in the door when [the_person.name] comes in and closes the door behind her."
    
    $the_person.draw_person()
    show screen person_info_ui(the_person)
    hide screen business_ui
    the_person.name "Thank you for meeting with me on such short notice. I thought about sending you an email but I think this should be said in person."
    "[the_person.name] takes a deep breath then continues."
    if the_person.happiness < 100:
        the_person.name "I've been doing my best to keep my head up lately, but honestly I just have been hating working here. I've decided that today is going to be my last world.day."
    elif the_person.salary < the_person.calculate_base_salary():
        the_person.name "I've been looking into other positions, and the pay I'm recieving here just isn't high enough. I've decided to accept another offer; today will be my last world.day."
    else:
        the_person.name "I've been looking for a change in my life, and I feel like this job is holding me back. I've decided that today is going to be my last world.day."
    
    $ raise_amount = int(the_person.salary*0.1)
    menu:
        "Offer a 10%% raise. (+$[raise_amount]/world.day)":
            mc.name "I'm very sorry to hear that [the_person.name], I understand that your job can be difficult at times."
            "You pull out [the_person.name]'s employee records and look them over."
            mc.name "In fact, the fact that you're being paid as little as you are is criminal. If I promised you a 10%% raise, effective immediately, would you consider staying on board?"
            $ the_person.salary += raise_amount
            "[the_person.name] takes a long moment before responding."
            if the_person.get_job_happiness_score() >= 0: #The raise has made them happy with the job.
                the_person.name "I think that would be enough to convince me to stay."
                show screen float_up_screen(["+$[raise_amount]/world.day Salary"],["float_text_green"])
                mc.name "Excellent, I'll have it on the books by the end of the world.day. Thank you for all your hard work [the_person.name]."
                "[the_person.name] lets herself out of your office, and you're able to go back to what you were doing."
            else:
                the_person.name "I'm sorry, but I just don't think it's going to be possible. I'm going to go and start clearing out my desk."
                "[the_person.name] lets herself out of your office. You put away her files and get back to what you were doing."
                $ mc.business.remove_employee(the_person)
                
            
        "Make her cum to convince her to stay." if the_person.effective_sluttiness() > 60:
            "You stand up from your desk and walk over to [the_person.name]."
            mc.name "[the_person.name], you've always been a good employee of mine."
            if the_person.outfit.vagina_available():
                "You reach a hand down between [the_person.name]'s legs and run a finger over her pussy."
            elif the_person.outfit.tits_available():
                "You cup one of [the_person.name]'s breasts and squeeze it lightly."
            else:
                "You reach around and grab [the_person.name]'s ass with one hand, squeezing it gently."
            mc.name "Let me show you the perks of working around here, if you still want to quit after then I won't stop you."
            "[the_person.name] thinks for a moment, then nods."
            call fuck_person(the_person) from _call_fuck_person_5
            $ change_amount = the_person.change_slut_modified(the_person.arousal) #Change her slut score by her final arousal. This should be _about_ 100 if she climaxed, but you may keep fucking her silly if you can overcome the arousal loss.
            show screen float_up_screen(["+[change_amount] Sluttiness"],["float_text_pink"])
            if the_person.arousal > 100: #If you made them cum, they'll stay on for a little while.
                the_person.name "Ah... Ah..."
                mc.name "Well [the_person.name], are you still thinking of leaving?"
                "[the_person.name] pants slowly and shakes her head."
                the_person.name "I don't think I will be, sir. Sorry to have wasted your time."
                mc.name "It was my pleasure."
                "[the_person.name] takes a moment to put herself back together, then steps out of your office."
            
            else: #If you fail to make them cum first they quit and leave.
                the_person.name "I'm sorry [mc.name], but I haven't changed my mind. I'll clear out my desk and be gone by the end of the world.day."
                "[the_person.name] takes a moment to put herself back together, then steps out of your office."
                $ mc.business.remove_employee(the_person)
            $ the_person.reset_arousal()
            

        
        "Let them go.":
            mc.name "I'm sorry to hear that [mc.name], but if that's the way you feel then it's probably for the best."
            the_person.name "I'm glad you understand. I'll clear out my desk and be gone by the end of the world.day."
            "[the_person.name] leaves, and you return to what you were doing."
            $ mc.business.remove_employee(the_person)
    
    $renpy.scene("Active")
    hide screen person_info_ui
    show screen business_ui 
    return
    
init 1 python:
    def serum_creation_crisis_requirement():
        return True #Always true, this will always happen right after a serum is created, regardless of the time.
    
label serum_creation_crisis_label(the_serum): # Called every time a new serum is created, test it on a R&D member.
    $ rd_staff = renpy.random.sample(mc.business.r_div.people, 1)[0] #Get a random researcher from the R&D department. TODO: Repalce this with the head researcher position.
    if rd_staff is not None:
        if mc.location == world.rd_room: # The MC is in the lab, just physically get them.
            call change_location(world.rd_room) from _call_serum_creation_1 #Just in case another crisis had interupted us being here.
            "There's a tap on your shoulder. You turn and see [rd_staff.name], looking obviously excited."
            $ rd_staff.draw_person(emotion="happy")
            $ renpy.say(rd_staff.name, "%s, I'm sorry to bother you but I've had a breakthrough! The first test dose of serum \"%s\" is coming out right now!" % (mc.name, the_serum["name"]))
            rd_staff.name "Would you like to come and oversee final testing?"
            menu:
                "Oversee final testing of the new serum.":
                    mc.name "I think I would. Show me what you've done."
                    #Fall through to the next section.
                    
                "Leave it to your R&D crew.":
                    mc.name "Thank you for letting me know [rd_staff.name], but I'm currently busy. I'm sure you're capable of running whatever tests seem necessary."
                    rd_staff.name "Of course. If nothing else comes up we will send the designs to production. You can have the production line changed over whenever you wish."
                    $renpy.scene("Active")
                    return
                
        else: # The MC is somewhere else, bring them to the lab for this.
            "Your phone buzzes, grabbing your attention. It's a call from the R&D section of your buisness."
            "As soon as you answer you hear the voice of [rd_staff.name]."
            $ renpy.say(rd_staff.name, "%s, I've had a breakthrough! The first test dose of serum \"%s\" is coming out right now!" % (mc.name, the_serum["name"]))
            rd_staff.name "Will you be able to come down and take a look?"
            menu:
                "Visit the lab and test the new serum.":
                    mc.name "I think that would be a good idea. I'll be over in a moment."
                    "You hang up and travel over to the lab. You're greeted by [rd_staff.name] as soon as you're in the door."
                    call change_location(world.rd_room) from _call_serum_creation_2
                    $ rd_staff.draw_person(emotion="happy")
                    $ rd_staff.call_greeting()
                    mc.name "We're set up over here. come this way."
                    #Fall through to the next section.
                    
                "Leave the R&D crew to test the new serum.":
                    mc.name "Thank you for letting me know [rd_staff.name], but I'm currently busy. I'm sure you're capable of running whatever tests seem necessary."
                    rd_staff.name "Of course. If nothing else comes up we will send the designs to production. You can have the production line changed over whenever you wish."
                    "[rd_staff.name] hangs up."
                    $renpy.scene("Active")
                    return
                    
        ## Test the serum out on someone.
        "[rd_staff.name] brings you to her work bench, where a centrifuge is spinning down."
        $ technobabble = renpy.random.choice(Person.technobabble_list)
        rd_staff.name "Perfect, it's just finishing now. I had this flash of inspiration and realised all I needed to do was [technobabble]."
        "[rd_staff.name] opens the centrifuge lid and takes out a small glass vial. She holds it up to the light and nods approvingly, then hands it to you."
        rd_staff.name "We should test it before sending the design off to production, don't you think?"
        menu:
            "Give the serum back for final testing.":
                mc.name "It seems like you have everything under control here [rd_staff.name], I'm going to leave that testing your capable hands."
                $ rd_staff.happiness += 5
                $ change_amount= rd_staff.change_obedience_modified(5)
                show screen float_up_screen(["+5 Happiness","+[change_amount] Obedience"],["float_text_yellow","float_text_grey"])
                
                rd_staff.name "I'll do my best sir, thank you!"
                if rd_staff.sluttiness < 10:
                    mc.name "I'm sure you will. Keep up the good work."
                elif rd_staff.sluttiness < 30:
                    "You give [rd_staff.name] a pat on the back."
                    mc.name "I'm sure you will. Keep up the good work."
                elif rd_staff.sluttiness < 80:
                    "You give [rd_staff.name] a quick slap on the ass. She gasps softly in suprise."
                    mc.name "I'm sure you will. Keep up the good work."
                else:
                    "You grab [rd_staff.name]'s ass and squeeze it hard. She gasps in suprise, then moans softly."
                    mc.name "I'm sure you will. Keep up the good work."
                    
                "You leave [rd_staff.name] to to her work in the lab and return to what you were doing."
                $renpy.scene("Active")
                return
                
            "Test the serum on [rd_staff.name].":
                mc.name "How confident in your work are you [rd_staff.name]? We could fast track this over to production if you're willing to take this test dose right now."
                if rd_staff.obedience < 80:
                    $ rd_staff.draw_person(emotion="angry")
                    show screen float_up_screen(["-10 Happiness","-5 Obedience"],["float_text_yellow","float_text_grey"])
                    $ rd_staff.change_happiness(-10)
                    $ rd_staff.obedience(-5)
                    rd_staff.name "Really? I'm just suppose to take a completely untested drug because it might make you more money? That's fucking ridiculous and we both know it."
                    "[rd_staff.name] puts the serum down on the lab bench and crosses her arms."
                    rd_staff.name "Just get out of here and I'll finish the initial testing in a safe enviroment."
                    mc.name "Fine, just make sure you get it done."
                    rd_staff.name "That's what I'm paid for, isn't it?"
                    "You leave [rd_staff.name] to her to work in the lab and return to what you were doing."
                    $renpy.scene("Active")
                    return                    
                 
                elif rd_staff.obedience < 110:
                    "[rd_staff.name] pauses for a moment before responding."
                    rd_staff.name "That's a big risk you know. If I'm going to do something like that, I think I deserve a raise."
                    $ raise_amount = int(rd_staff.salary*0.1)
                    menu:
                        "Give [rd_staff.name] a %%10 raise. (+$[raise_amount]/world.day)":
                            show screen float_up_screen(["+$[raise_amount]/world.day Salary"],["float_text_green"])
                            mc.name "Alright, you've got yourself a deal. I'll have the books updated by the end of the world.day."
                            $ rd_staff.salary += raise_amount
                            rd_staff.name "Good to hear it. Let's get right to it then."
                            $ rd_staff.give_serum(copy.copy(the_serum))
                            
                        "Refuse.":
                            mc.name "I'm sorry but that just isn't in the budget right now."
                            rd_staff.name "Fine, then I'll just have to put this new design through the normal safety tests. I'll have the results for you as soon as possible."
                            mc.name "Fine, just make sure you get it done."
                            "[rd_staff.name] nods. You leave her to work in the lab and return to what you were doing."
                            $renpy.scene("Active")
                            return
                            
                else:
                    "[rd_staff.name] pauses for a moment, then nods."
                    rd_staff.name "Okay sir, if you think it will help the business."
                    $ rd_staff.give_serum(copy.copy(the_serum))
                    
                        
        "[rd_staff.name] drinks down the contents of the vial and places it to the side."
        rd_staff.name "Okay, lets see what the effects are. Talk to me for a while and see if there's anything different."
        call talk_person(rd_staff) from _call_talk_person_7
        $ rd_staff.draw_person()
        rd_staff.name "From a safety perspective everything seems fine. I don't see any problem sending this design to production."
        mc.name "Thank you for the help [rd_staff.name]."
        "You leave [rd_staff.name] to get back to her work and return to what you were doing."
        $ change_amount = rd_staff.change_obedience_modified(5)
        show screen float_up_screen(["+[change_amount] Obedience"],["float_text_grey"])             
        $renpy.scene("Active")
        return
                                                                                                                                                                                               
    else: #There's nobody else in the lab, guess you've done all the hard work yourself!
        $renpy.say("", "You finish work on your new serum design, dubbing it \"%s\". The lab is empty, so you celebrate by yourself." % the_serum["name"])
        return
    return #We should always have returned by this point anyways, but just in case we'll catch it here.
