init python:
    class MainCharacter(Person):
        def __init__(self, location, name, business, stat_array, skill_array, sex_array):
            super(MainCharacter, self).__init__(name, stat_array, skill_array, sex_array)

            self.location = location
            self.energy = 50
            self.designed_wardrobe = Wardrobe("Designed Wardrobe", [])
            self.money = 100 ## Personal money that can be spent however you wish. Company funds are seperate (but can be manipulated in your favour)
            self.business = business
            self.inventory = SerumInventory([])

        def change_location(self,new_location):
            self.location = new_location

        def use_energy(self,amount):
            self.energy = self.energy - amount
            if self.energy < 0:
                self.energy = 0

        def save_design(self,the_outfit,new_name):
            the_outfit.name = new_name
            self.designed_wardrobe.add_outfit(the_outfit)

        def is_at_work(self): #Checks to see if the main character is at work, generally used in crisis checks.
            if self.location == self.business.m_div.room or self.location == self.business.p_div.room or self.location == self.business.r_div.room or self.location == self.business.s_div.room or self.location == self.business.h_div.room:
                return True
            else:
                return False

        def get_available_positions(self, list_of_positions, other_person):
            tuple_list = []
            for position in list_of_positions:
                if self.location.has_object_with_trait(position.requires_location) and position.check_clothing(other_person):
                    tuple_list.append((position.name,position))
            return tuple_list

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

        ##PC starts in his bedroom##
        main_business = Business(business_name, m_room, p_room, rd_room, office, office, lobby)
        mc = MainCharacter(bedroom,character_name,main_business,stat_array,skill_array,_sex_array)

        list_of_places = [] #By having this in an init block it may be set to null each time the game is reloaded, because the initialization stuff below is only called once.

        ##Keep a list of all the places##
        list_of_places.append(bedroom)
        list_of_places.append(kitchen)
        list_of_places.append(hall)

        list_of_places.append(lobby)
        list_of_places.append(office)
        list_of_places.append(rd_room)
        list_of_places.append(p_room)
        list_of_places.append(m_room)

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
        lobby.link_locations_two_way(rd_room)
        lobby.link_locations_two_way(m_room)
        lobby.link_locations_two_way(p_room)

        mall.link_locations_two_way(office_store)
        mall.link_locations_two_way(clothing_store)
        mall.link_locations_two_way(sex_store)
        mall.link_locations_two_way(home_store)
        mall.link_locations_two_way(gym)

        bedroom.add_object(["wall", "floor", "bed", "window"])
        kitchen.add_object(["wall", "floor", "chair"])
        hall.add_object(["wall", "floor"])

        lobby.add_object(["wall", "floor", "chair", "window"])
        office.add_object(["wall", "floor", "chair", "window"])
        rd_room.add_object(["wall", "floor", "chair"])
        m_room.add_object(["wall", "floor", "chair"])
        p_room.add_object(["wall", "floor", "chair"])

        downtown.add_object(["floor"])
        office.add_object(["wall", "floor", "chair"])
        clothing_store.add_object(["wall", "floor"])
        sex_store.add_object(["wall", "floor"])
        home_store.add_object(["wall", "floor", "chair"])
        mall.add_object(["wall", "floor"])

        max_num_of_random = 4 ##Default use to be 4
        for place in list_of_places:
            if place.public:
                random_count = renpy.random.randint(1,max_num_of_random)
                for x in range(0,random_count):
                    place.people.append(create_random_person()) #We are using create_random_person instead of make_person because we want premade character bodies to be hirable instead of being eaten up by towns-folk.

        ##Global Variable Initialization##
        day = 0 ## Game starts on day 0.
        time_of_day = 0 ## 0 = Early morning, 1 = Morning, 2 = Afternoon, 3 = Evening, 4 = Night

    return
