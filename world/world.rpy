init python:
    class World(renpy.store.object):
        locations = {
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
                "actions": (market_work_action,),
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
        day_names = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"] #Arrays that hold the names of the world.days of the week and times of world.day. Arrays start at 0.
        time_names = ["Early Morning","Morning","Afternoon","Evening","Night"]

        def __init__(self, **kwargs):
            self.__dict__.update(**kwargs)

            for k, v in World.locations.iteritems():
                self.__dict__[k] = Room(**v)

            self.lobby.name = persistent.company_name + " " + self.lobby.name

            self.day = 0 ## Game starts on day 0.
            self.time_of_day = 0 ## 0 = Early morning, 1 = Morning, 2 = Afternoon, 3 = Evening, 4 = Night

        @property
        def corp(self):
            return self.mc.business

        @property
        def loc(self):
            return self.mc.location

        def __iter__(self): # when iterating over world you get the world locations
            for k in World.locations.keys():
                yield self.__dict__[k]


        def is_work_time(self): #Checks to see if employees are currently working
            return (self.day % 7) < 6 and 0 < self.time_of_day < 4 # work hours and give people the weekends off.

label create_world():
    python:
        world = World()
        mc = MainCharacter(MyCorp())
    return
