init python:
    class MainCharacter(Person):
        points_per_stat = {
            "Main Stats": 3,
            "Work Skills": 2,
            "Sex Skills": 1
        }
        def __init__(self, business):
            super(MainCharacter, self).__init__(**persistent.character)

            self.location = world["bedroom"]
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
            return any(self.location == div.room for div in self.business.division)

        def get_available_positions(self, list_of_positions, other_person):
            tuple_list = []
            for position in list_of_positions:
                if self.location.has_object_with_trait(position.requires_location) and position.check_clothing(other_person):
                    tuple_list.append((position.name,position))
            return tuple_list

label create_test_variables(): #Gets all of the variables ready. TODO: Move some of this stuff to an init block?
    python:
        #By having this in an init block it may be set to null each time the game is reloaded, because the initialization stuff below is only called once.
        world = { k: Room(**v) for k, v in Room.default_locations.iteritems() }
        world["lobby"].name = persistent.company_name + " " + world["lobby"].name

        mc = MainCharacter(MyCorp())

        max_num_of_random = 4 ##Default use to be 4
        for name, place in world.iteritems():
            if place.public:
                random_count = renpy.random.randint(1,max_num_of_random)
                for x in range(0,random_count):
                    place.people.add(create_random_person()) #We are using create_random_person instead of make_person because we want premade character bodies to be hirable instead of being eaten up by towns-folk.

        ##Global Variable Initialization##
        day = 0 ## Game starts on day 0.
        time_of_day = 0 ## 0 = Early morning, 1 = Morning, 2 = Afternoon, 3 = Evening, 4 = Night

    return
