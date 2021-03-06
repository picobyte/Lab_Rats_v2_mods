init python:
    class World(renpy.store.object):
        locations = ({
            "id": "person_home",
            "name": "my house", # from perspective of person, for phone
            "connections": set(["downtown"]),
            "background_image": house_background,
            "scenery": set(),
            "open_time": set([0,4]),
            "actions": (),
            "public": False,
        },{
            "id": "bedroom",
            "connections": set(["hall"]),
            "background_image": house_background,
            "scenery": set(["wall", "floor", "bed", "window"]),
            "actions": (sleep_action,faq_action),
            "public": False,
            "map_pos": (0.1,0.5)
        },{
            "id": "kitchen",
            "connections": set(["hall"]),
            "background_image": house_background,
            "scenery": set(["wall", "floor", "chair"]),
            "actions": (),
            "public": False,
            "map_pos": (0.1,0.7)
        },{
            "id": "hall",
            "name": "house entrance",
            "connections": set(["bedroom", "kitchen", "downtown"]),
            "background_image": house_background,
            "scenery": set(["wall", "floor"]),
            "actions": (),
            "public": False,
            "map_pos": (0.2,0.6)
        },{ ##PC's Work##
            "id": "lobby",
            "connections": set(["downtown", "office", "rd_room", "p_room", "m_room"]),
            "background_image": office_background,
            "scenery": set(["wall", "floor", "chair", "window"]),
            "actions": (),
            "public": False,
            "map_pos": (0.8,0.6)
        },{
            "id": "office",
            "name": "main office",
            "connections": set(["lobby"]),
            "background_image": office_background,
            "scenery": set(["wall", "floor", "chair", "window"]),
            "actions": (policy_purhase_action,hr_work_action,supplies_work_action,interview_action,sell_serum_action,pick_supply_goal_action,move_funds_action,set_uniform_action,set_serum_action),
            "public": False,
            "map_pos": (0.85,0.82)
        },{
            "id": "rd_room",
            "name": "R&D division",
            "connections": set(["lobby"]),
            "background_image": lab_background,
            "scenery": set(["wall", "floor", "chair"]),
            "actions": (research_work_action,design_serum_action,pick_research_action),
            "public": False,
            "map_pos": (0.9,0.67)
        },{
            "id": "p_room",
            "name": "Production division",
            "connections": set(["lobby"]),
            "background_image": office_background,
            "scenery": set(["wall", "floor", "chair"]),
            "actions": (production_work_action,pick_production_action,trade_serum_action,set_autosell_action),
            "public": False,
            "map_pos": (0.9,0.53)
        },{
            "id": "m_room",
            "name": "marketing division",
            "connections": set(["lobby"]),
            "background_image": office_background,
            "scenery": set(["wall", "floor", "chair"]),
            "actions": (market_work_action,),
            "public": False,
            "map_pos": (0.85,0.38)
        },{ ##Connects all Locations##
            "id": "downtown",
            "connections": set(["hall", "lobby", "mall", "person_home"]),
            "background_image": outside_background,
            "scenery": set(["floor"]),
            "space": 20,
            "open_time": set([0, 4]),
            "actions": (),
            "public": True,
            "map_pos": (0.5,0.65)
        },{ ##A mall, for buying things##
            "id": "office_store",
            "name": "office supply store",
            "connections": set(["mall"]),
            "background_image": mall_background,
            "scenery": set(["wall", "floor", "chair"]),
            "actions": (),
            "space": 6,
            "public": True,
            "map_pos": (0.68,0.24)
        },{
            "id": "clothing_store",
            "name": "clothing store",
            "connections": set(["mall"]),
            "background_image": mall_background,
            "scenery": set(["wall", "floor"]),
            "actions": (),
            "space": 6,
            "public": True,
            "map_pos": (0.6,0.15)
        },{
            "id": "sex_store",
            "name": "sex store",
            "connections": set(["mall"]),
            "background_image": mall_background,
            "scenery": set(["wall", "floor"]),
            "actions": (),
            "public": True,
            "map_pos": (0.5,0.13)
        },{
            "id": "home_store",
            "name": "home improvement store",
            "connections": set(["mall"]),
            "background_image": mall_background,
            "scenery": set(["wall", "floor", "chair"]),
            "actions": (),
            "space": 6,
            "public": True,
            "map_pos": (0.4,0.15)
        },{
            "id": "gym",
            "connections": set(["mall"]),
            "background_image": mall_background,
            "scenery": set(["wall", "floor", "chair"]),
            "actions": (),
            "space": 6,
            "open_time": set([0, 4]),
            "public": True,
            "map_pos": (0.32,0.24)
        },{
            "id": "mall",
            "connections": set(["downtown", "office_store", "clothing_store", "sex_store", "home_store", "gym"]),
            "background_image": mall_background,
            "scenery": set(["wall", "floor"]), # dict with string object and counts, traits defined in object_traits
            "space": 20,
            "open_time": set([0, 4]),
            "actions": (), #A list of Action objects
            "public": True, #If True, random people can wander here.
            "map_pos": (0.5,0.3) #A tuple of two float values from 0.0 to 1.0, used to determine where this should be placed on the map dynamically. Not drawn if not set.
        })
        day_names = ("Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday") #Arrays that hold the names of the world.days of the week and times of world.day. Arrays start at 0.
        time_names = ("Early Morning","Morning","Afternoon","Evening","Night")

        def __init__(self, **kwargs):
            self.__dict__.update(**kwargs)

            for loc in World.locations:
                self.__dict__[loc["id"]] = Location(**loc)

            self.lobby.name = persistent.company_name + " " + self.lobby.name

            self.day = 0 ## Game starts on day 0.
            self.time_of_day = 0 ## 0 = Early morning, 1 = Morning, 2 = Afternoon, 3 = Evening, 4 = Night

        def __iter__(self): # when iterating over world you get the world locations
            for loc in World.locations:
                yield self.__dict__[loc["id"]]


        def is_work_time(self): #Checks to see if employees are currently working
            return (self.day % 7) < 6 and 0 < self.time_of_day < 4 # work hours and give people the weekends off.

        def add_time_is_next_day(self):
            self.time_of_day = (self.time_of_day + 1) % 5
            self.day += not self.time_of_day
            return not self.time_of_day

label create_world():
    python:
        world = World()
        mc = MainCharacter(MyCorp())
    return
