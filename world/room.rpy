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
        def __init__(self,name,formalName,connections,background_image,objects,people,actions,public,map_pos):
            self.name = name
            self.formalName = formalName
            self.connections = connections
            self.background_image = background_image
            self.objects = objects # dict with string object and counts, traits defined in object_traits
            self.people = people
            self.actions = actions #A list of Action objects
            self.public = public #If True, random people can wander here. TODO: Update rooms to include this value.
            self.map_pos = map_pos #A tuple of two float values from 0.0 to 1.0, used to determine where this should be placed on the map dynamically.
            super(Room, self).__init__(name, people)

        def link_locations(self,other): #This is a one way connection!
            self.connections.append(other)

        def link_locations_two_way(self,other): #Link it both ways. Great for adding locations after the fact, when you don't want to modify existing locations.
            self.link_locations(other)
            other.link_locations(self)

        def add_object(self, names):
            for n in names:
                self.objects[n] = self.objects[n] + 1 if n in self.objects else 1

        def objects_with_trait(self, the_trait):
            return [objname for objname in self.objects.keys() if the_trait in self.object_traits[objname]]

        def has_object_with_trait(self,the_trait):
            if the_trait == "None":
                return True
            for objname in self.objects.keys():
                if the_trait in self.object_traits[objname]:
                    return True
            return False

        def valid_actions(self):
            count = 0
            for act in self.actions:
                if act.check_requirement():
                    count += 1
            return count


    ##PC's Home##
    bedroom = Room("bedroom","Bedroom",[],house_background,{},[],[sleep_action,faq_action],False,[0.1,0.5])
    kitchen = Room("kitchen", "Kitchen",[],house_background,{},[],[],False,[0.1,0.7])
    hall = Room("house entrance","House Entrance",[],house_background,{},[],[],False,[0.2,0.6])

    ##PC's Work##
    lobby = Room("lobby","Lobby",[],office_background,{},[],[],False,[0.8,0.6])
    office = Room("main office","Main Office",[],office_background,{},[],[policy_purhase_action,hr_work_action,supplies_work_action,interview_action,sell_serum_action,pick_supply_goal_action,move_funds_action,set_uniform_action,set_serum_action],False,[0.85,0.82])
    rd_room = Room("R&D division","R&D Division",[],lab_background,{},[],[research_work_action,design_serum_action,pick_research_action],False,[0.9,0.67])
    p_room = Room("Production division", "Production Division",[],office_background,{},[],[production_work_action,pick_production_action,trade_serum_action,set_autosell_action],False,[0.9,0.53])
    m_room = Room("marketing division","Marketing Division",[],office_background,{},[],[market_work_action],False,[0.85,0.38])

    ##Connects all Locations##
    downtown = Room("downtown","Downtown",[],outside_background,{},[],[],True,[0.5,0.65])

    ##A mall, for buying things##
    office_store = Room("office supply store","Office Supply Store",[],mall_background,{},[],[],True,[0.68,0.24])
    clothing_store = Room("clothing store","Clothing Store",[],mall_background,{},[],[],True,[0.6,0.15])
    sex_store = Room("sex store","Sex Store",[],mall_background,{},[],[],True,[0.5,0.13])
    home_store = Room("home improvement store","Home Improvement Store",[],mall_background,{},[],[],True,[0.4,0.15])
    gym = Room("gym","Gym",[],mall_background,{},[],[],True,[0.32,0.24])
    mall = Room("mall","Mall",[],mall_background,{},[],[],True,[0.5,0.3])
