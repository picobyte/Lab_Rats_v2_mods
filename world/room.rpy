init -25:
    define house_background = Image("Home_Background.png")
    define mall_background = Image("Mall_Background.png")
    define lab_background = Image("Lab_Background.png")
    define office_background = Image("Office_Background.png")
    define outside_background = Image("Outside_Background.png")

    image bg science_menu_background = Image("Science_Menu_Background.png")
    image bg paper_menu_background = Image("Paper_Background.png")

init -25 python:
    class Room(renpy.store.object): #Contains people and objects.
        object_traits = {
            "wall": set(["Lean"]),
            "window": set(["Lean"]),
            "chair": set(["Sit","Low"]),
            "bed": set(["Sit","Lay","Low"]),
            "floor": set(["Lay","Kneel","Stand"]),
            "grass": set(["Lay","Kneel","Stand"]),
            "wall": set(["Lean"]),
            "window": set(["Lean"]),
            "chair": set(["Sit","Low"])
        }
        def __init__(self, public, people=None, **kwargs):
            self.people = set(create_random_person() for x in range(people if people else 4)) if public else set()
            self.__dict__.update(**kwargs)

        def objects_with_trait(self, the_trait):
            return [objname for objname in self.scenery.keys() if the_trait in self.object_traits[objname]]

        def has_object_with_trait(self,the_trait):
            if the_trait == "None":
                return True
            for objname in self.scenery.keys():
                if the_trait in self.object_traits[objname]:
                    return True
            return False

        def valid_actions(self):
            return sum(1 for _ in self.actions if _.check_requirement())

