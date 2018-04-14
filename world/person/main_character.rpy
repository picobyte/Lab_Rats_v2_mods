init -4 python:
    class MainCharacter(Person):
        points_per_stat = {
            "Main Stats": 3,
            "Work Skills": 2,
            "Sex Skills": 1
        }
        def __init__(self, business):
            super(MainCharacter, self).__init__(**persistent.character)

            self.location = world.bedroom
            self.energy = 50 #FIXME: not in use
            self.designed_wardrobe = Wardrobe("Designed Wardrobe", [])
            self.money = 100 ## Personal money that can be spent however you wish. Company funds are seperate (but can be manipulated in your favour)
            self.business = business
            self.inventory = SerumInventory([])

        def use_energy(self,amount):
            self.energy = max(self.energy - amount, 0)

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
