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
        def __init__(self, roomnr, people=4):
            self._roomnr = roomnr
            self.people = set(create_random_person() for _ in range(renpy.random.randint(0, people))) if self.public else set()

        def __getattr__(self, name):
            i = self.__dict__["_roomnr"]
            if name in World.locations[i]:
                return World.locations[i][name]
            raise AttributeError

        def objects_with_trait(self, trait):
            return [_ for _ in self.scenery if trait in self.object_traits[_]]

        def has_object_with_trait(self,trait):
            return trait == "None" or any(trait in self.object_traits[_] for _ in self.scenery)

        def valid_actions(self):
            return sum(1 for _ in self.actions if _.check_requirement())

