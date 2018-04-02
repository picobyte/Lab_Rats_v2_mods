init -14 python:
    # create_random_person is used to generate a NPC object from a list of random or provided stats.
    # use "make_a_person" to properly get premade characters mixed with randoms.
    # note that this only uses the static variables of Person
    def create_random_person(name = None, last_name = None, age = None, body_type = None, face_style = None, tits = None, height = None, hair_colour = None, hair_style = None, skin = None, eyes = None, job = None, personality = None, business = None):

        name = name or renpy.random.choice(Person.list_of_names)
        last_name = last_name or renpy.random.choice(Person.list_of_last_names)
        age = age or renpy.random.randint(21,50)

        body_type = body_type or renpy.random.choice(Person.list_of_body_types)
        tits = tits or renpy.random.choice([tit for cup, weight in Person.list_of_tits for tit in [cup] * weight])
        height = height or 0.9 + (renpy.random.random()/10)

        hair_style = hair_style or renpy.random.choice(Person.hair_styles)
        hair_colour = hair_colour or renpy.random.choice(Person.list_of_hairs)
        skin = skin or renpy.random.choice([it for k, v in Person.list_of_skins for it in [k] * v])
        face_style = face_style or renpy.random.choice(Person.list_of_faces)
        body_images = Person.body_image_for[skin]

        emotion_images = Expression(name+"\'s Expression Set", skin, face_style)

        eyes = eyes or renpy.random.choice(Person.list_of_eyes)
        job = job or renpy.random.choice(Person.list_of_jobs)
        personality = personality or renpy.random.choice(Person.list_of_personalities)

        mods = {"skill_cap": 5, "stat_cap": 5, "suggest": 0,
                  "foreplay_cap": 5, "oral_cap": 5, "vaginal_cap": 5, "anal_cap": 5,
                  "obedience": renpy.random.randint(-10,10), "sluttiness": renpy.random.randint(0,10)}

        if business:
            for pol in business.active_policies:
                if "effect" in pol:
                    for k, v in pol["effect"].iteritems():
                        if k in kwargs:
                            kwargs[k] += v

        return NPC(name,last_name,age,body_type,tits,height,body_images,emotion_images,hair_colour,hair_style,skin,eyes,job,default_wardrobe,personality,mods)


    class NPC(Person): #Everything that needs to be known about a person.

        premade_list = [{"body_type": "Fat", "height": 0.99, "skin": "tan", "tits": "DD","hair_colour": "red","hair_style": Person.hair_styles[0]},
                        {"body_type": "Thin", "height": 1.0, "skin": "white", "tits": "B","hair_colour": "red","hair_style": Person.hair_styles[0]},
                        {"body_type": "Fat", "height": 0.96, "skin": "white", "tits": "DD","hair_colour": "Brown","hair_style": Person.hair_styles[1]}]

        def __init__(self,name,last_name,age,body_type,tits,height,body_images,expression_images,hair_colour,hair_style,skin,eyes,job,wardrobe,personality,mods):

            skill_list = [renpy.random.randint(1,mods["skill_cap"]) for i in range(5)]
            stat_list = [renpy.random.randint(1,mods["stat_cap"]) for i in range(3)]
            sex_list = [renpy.random.randint(0,mods[n]) for n in ["foreplay_cap", "oral_cap", "vaginal_cap", "anal_cap"]]

            super(NPC, self).__init__(name, stat_list,skill_list, sex_list)

            ## Personality stuff, name, ect. Non-physical stuff.
            #TODO: Add ability to "discover" this stuff, you don't know it by default.
            self.last_name = last_name
            self.job = job
            self.personality = personality
            #TODO: Have a "home" variable that tells people where to go at night
            #TODO: Relationship with other people (List of known people plus relationship with them.)

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


            self.salary = self.calculate_base_salary()

            if renpy.random.randint(0,1) == 0:
                self.idle_pose = "stand3"
            else:
                self.idle_pose = "stand2"

            ##Personality Stats##
            #Things like sugestability, that change over the course of the game when the player interacts with the girl
            self.suggestibility = 0 + mods["suggest"] #How much events will influnce this girls stats. 100 means full possible effect, 0 means no long term effect.
            self.happiness = 100 #100 is default max, higher is better.
            self.sluttiness = 0 + mods["sluttiness"] #How slutty the girl is by default. Higher will have her doing more things just because she wants to or you asked.
            self.obedience = 100 + mods["obedience"] #How likely the girl is to listen to commands. Default is 100 (normal person), lower actively resists commands, higher follows them.

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

        def move(self, curr, dest):
            # if this errors, person is not in current. test this before calling!
            if not curr is dest: # Don't bother moving people who are already there.
                dest.people.append(curr.people.pop(curr.people.index(self)))

        def run_move(self,location): #Move to the apporpriate place for the current time unit, ie. where the player should find us.

            #Move the girl the appropriate location on the map. For now this is either a division at work (chunks 1,2,3) or downtown (chunks 0,5). TODO: add personal homes to all girls that you know above a certain amount.

            if time_of_day == 0 or time_of_day == 4: #Home time
                self.move(location, downtown) #Move to downtown as proxy for home.
            else:
                work_destination = mc.business.get_employee_workstation(self)

                if work_destination is not None: #She works for us, move her to her work station,
                    self.move(location, work_destination)
                    if self.should_wear_uniform():
                        self.wear_uniform()
                else: #She does not work for us, scatter her somewhere public on the map.
                    available_locations = [] #Check to see where is public (or where you are white listed) and move to one of those locations randomly
                    for potential_location in list_of_places:
                        if potential_location.public:
                            available_locations.append(potential_location)
                    self.move(location, renpy.random.choice(available_locations))


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
            position = position or self.idle_pose
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

        def call_for_consent(self, by_ref):
            the_position = by_ref[0]

            if self.effective_sluttiness() >= the_position.slut_requirement:
                # The person is slutty enough to want to have sex like this.
                self.call_sex_accept_response()

            elif self.effective_sluttiness() + (self.obedience-100) >= the_position.slut_requirement:
                # The person isn't slutty enough for this. First, try and use obedience.
                self.draw_person(the_position.position_tag, emotion="sad")
                # She looses happiness equal to the difference between her sluttiness and the requirement.
                # ie the amount obedience covered.
                self.call_sex_obedience_accept_response(self.sluttiness - the_position.slut_requirement)

            elif self.effective_sluttiness() >= the_position.slut_requirement/2:
                # No amount of obedience will help here. How badly did you screw up?
                # If you still fail, but by a little, she rebukes you but you keep seducing her. Otherwise, the entire thing ends.
                by_ref[0] = "Try again"
                self.call_sex_gentle_reject()
            else:
                # Your seduction attempt wasn't even close, angry response follows
                self.draw_person(the_position.position_tag,emotion="angry")
                self.change_happiness(-5) #She's pissed you would even try that
                by_ref[0] = "Leave"
                self.call_sex_angry_reject(-5)

        def call_for_arouse(self, mc, the_position):

            # The same calculation but for the guy
            mc.change_arousal(the_position.guy_arousal + (the_position.guy_arousal * self.sex_skills[the_position.skill_tag] * 0.1))
            change_amount = the_position.girl_arousal + (the_position.girl_arousal * mc.sex_skills[the_position.skill_tag] * 0.1)
            renpy.show_screen("float_up_screen", ["+[change_amount] Arousal"], ["float_text_red"])
            self.change_arousal(change_amount) #The girls arousal gain is the base gain + 10% per the characters skill in that category.

            if self.arousal >= 100:
                #She's climaxing.
                self.draw_person(the_position.position_tag,emotion="orgasm")
                renpy.show_screen("float_up_screen", ["+5 Happiness"], ["float_text_yellow"])
                self.change_happiness(5) #Orgasms are good, right?
                renpy.call(self.personality.climax_response_label, self)
            else:
                renpy.call(self.personality.sex_response_label, self)


        def call_sex_accept_response(self):
            self.personality.get_sex_accept_response(self)

        def call_sex_obedience_accept_response(self, amount=None):
            if amount:
                self.change_happiness(amount)
            self.personality.get_sex_obedience_accept_response(self, amount)

        def call_sex_gentle_reject(self):
            self.personality.get_sex_gentle_reject(self)

        def call_sex_angry_reject(self, amount=None):
            if amount:
                self.change_happiness(amount)
            self.personality.get_sex_angry_reject(self, amount)

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

        def has_large_tits(self): #Returns true if the girl has large breasts. "D" cups and up are considered large enough for titfucking, swinging, etc.
            return self.tits[0] in "DEF"

        def effective_sluttiness(self): #Used in sex scenes where the girl will be more aroused, making it easier for her to be seduced.
            return self.sluttiness + (self.arousal/2)

        def calculate_base_salary(self): #returns the default value this person should be worth on a per day basis.
            return (self.int + self.focus + self.charisma)*2 + (self.hr_skill + self.market_skill + self.research_skill + self.production_skill + self.supply_skill)

    def make_person(): #This will generate a person, using a pregen body some of the time if they are available.
        split_proportion = 20 #1/5 characters generated will be a premade character.
        if renpy.random.randint(1,100) < split_proportion and len(NPC.premade_list) > 0:
            character_params = renpy.random.choice(NPC.premade_list) #Get a premade character
            NPC.premade_list.remove(character_params)
            return create_random_person(business=mc.business, **character_params)

        #Either we aren't getting a premade, or we are out of them.
        return create_random_person(business=mc.business)

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

        def get_smaller_tits(self):
            for i in range(len(self.list_of_tits)):
                if tits[i][0] == self.tits:
                    break
            return self.list_of_tits[i-1][0] if i > 0 else self.tits

        def get_larger_tits(current_tits):
            sz = len(self.list_of_tits)
            for i in range(sz):
                if tits[i][0] == self.tits:
                    break
            return self.list_of_tits[i+1][0] if i < sz - 1 else self.tits
