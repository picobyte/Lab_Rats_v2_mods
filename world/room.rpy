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

        default_locations = {
            "bedroom": {
                "name": "bedroom",
                "connections": set(["hall"]),
                "background_image": house_background,
                "scenery": set(["wall", "floor", "bed", "window"]),
                "actions": (sleep_action,faq_action),
                "public": False,
                "map_pos": (0.1,0.5)
            },
            "kitchen": {
                "name": "kitchen",
                "connections": set(["hall"]),
                "background_image": house_background,
                "scenery": set(["wall", "floor", "chair"]),
                "actions": (),
                "public": False,
                "map_pos": (0.1,0.7)
            },
            "hall": {
                "name": "house entrance",
                "connections": set(["bedroom", "kitchen", "downtown"]),
                "background_image": house_background,
                "scenery": set(["wall", "floor"]),
                "actions": (),
                "public": False,
                "map_pos": (0.2,0.6)
            },
        ##PC's Work##
            "lobby": {
                "name": "lobby",
                "connections": set(["downtown", "office", "rd_room", "p_room", "m_room"]),
                "background_image": office_background,
                "scenery": set(["wall", "floor", "chair", "window"]),
                "actions": (),
                "public": False,
                "map_pos": (0.8,0.6)
            },
            "office": {
                "name": "main office",
                "connections": set(["lobby"]),
                "background_image": office_background,
                "scenery": set(["wall", "floor", "chair", "window"]),
                "actions": (policy_purhase_action,hr_work_action,supplies_work_action,interview_action,sell_serum_action,pick_supply_goal_action,move_funds_action,set_uniform_action,set_serum_action),
                "public": False,
                "map_pos": (0.85,0.82)
            },
            "rd_room": {
                "name": "R&D division",
                "connections": set(["lobby"]),
                "background_image": lab_background,
                "scenery": set(["wall", "floor", "chair"]),
                "actions": (research_work_action,design_serum_action,pick_research_action),
                "public": False,
                "map_pos": (0.9,0.67)
            },
            "p_room": {
                "name": "Production division",
                "connections": set(["lobby"]),
                "background_image": office_background,
                "scenery": set(["wall", "floor", "chair"]),
                "actions": (production_work_action,pick_production_action,trade_serum_action,set_autosell_action),
                "public": False,
                "map_pos": (0.9,0.53)
            },
            "m_room": {
                "name": "marketing division",
                "connections": set(["lobby"]),
                "background_image": office_background,
                "scenery": set(["wall", "floor", "chair"]),
                "actions": (market_work_action),
                "public": False,
                "map_pos": (0.85,0.38)
            },
        ##Connects all Locations##
            "downtown": {
                "name": "downtown",
                "connections": set(["hall", "lobby", "mall"]),
                "background_image": outside_background,
                "scenery": set(["floor"]),
                "actions": (),
                "public": True,
                "map_pos": (0.5,0.65)
            },
        ##A mall, for buying things##
            "office_store": {
                "name": "office supply store",
                "connections": set(["mall"]),
                "background_image": mall_background,
                "scenery": set(["wall", "floor", "chair"]),
                "actions": (),
                "public": True,
                "map_pos": (0.68,0.24)
            },
            "clothing_store": {
                "name": "clothing store",
                "connections": set(["mall"]),
                "background_image": mall_background,
                "scenery": set(["wall", "floor"]),
                "actions": (),
                "public": True,
                "map_pos": (0.6,0.15)
            },
            "sex_store": {
                "name": "sex store",
                "connections": set(["mall"]),
                "background_image": mall_background,
                "scenery": set(["wall", "floor"]),
                "actions": (),
                "public": True,
                "map_pos": (0.5,0.13)
            },
            "home_store": {
                "name": "home improvement store",
                "connections": set(["mall"]),
                "background_image": mall_background,
                "scenery": set(["wall", "floor", "chair"]),
                "actions": (),
                "public": True,
                "map_pos": (0.4,0.15)
            },
            "gym": {
                "name": "gym",
                "connections": set(["mall"]),
                "background_image": mall_background,
                "scenery": set(["wall", "floor", "chair"]),
                "actions": (),
                "public": True,
                "map_pos": (0.32,0.24)
            },
            "mall": {
                "name": "mall",
                "connections": set(["downtown", "office_store", "clothing_store", "sex_store", "home_store", "gym"]),
                "background_image": mall_background,
                "scenery": set(["wall", "floor"]), # dict with string object and counts, traits defined in object_traits
                "actions": (), #A list of Action objects
                "public": True, #If True, random people can wander here.
                "map_pos": (0.5,0.3) #A tuple of two float values from 0.0 to 1.0, used to determine where this should be placed on the map dynamically.
            }
        }

        def __init__(self, name, people=None, **kwargs):
            self.name = name
            self.people = people or set()
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
            count = 0
            for act in self.actions:
                if act.check_requirement():
                    count += 1
            return count

