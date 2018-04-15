init -25:
    define house_background = Image("Home_Background.png")
    define mall_background = Image("Mall_Background.png")
    define lab_background = Image("Lab_Background.png")
    define office_background = Image("Office_Background.png")
    define outside_background = Image("Outside_Background.png")

    image bg science_menu_background = Image("Science_Menu_Background.png")
    image bg paper_menu_background = Image("Paper_Background.png")

init -25 python:
    import collections
    def default_to_zero():
        return collections.defaultdict(int)

    class Location(renpy.store.object): #Contains people, scenery(fixed in place) and objects(portable).
        object_traits = {
            "wall": set(["Lean"]),
            "window": set(["Lean"]),
            "bed": set(["Sit","Lay","Low"]),
            "floor": set(["Lay","Kneel","Stand"]),
            "grass": set(["Lay","Kneel","Stand"]),
            "chair": set(["Sit","Low"]) # can be inventory
        }
        def __init__(self, name=None, inventory=None, space=4, **room):
            self.items = collections.defaultdict(default_to_zero, inventory or {})
            self.__dict__.update(**room)
            self.name = name or self.id
            self.space = space
            self.people = set(create_random_person() for _ in range(renpy.random.randint(space/2, space))) if self.public else set()

        def objects_with_trait(self, trait):
            return [_ for _ in self.scenery if trait in self.object_traits[_]]

        def has_object_with_trait(self,trait):
            return trait == "None" or any(trait in self.object_traits[_] for _ in self.scenery)

        def valid_actions(self):
            return sum(1 for _ in self.actions if _.check_requirement())

