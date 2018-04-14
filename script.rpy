
#How the new position code is set up:
#Each clothing set now has a dictionary of images. The only one that is required is "standing", which is used when you are talking to the person most of the time.
#Each position has a "position_tag". When you start having sex with someone the draw_person code will check it's dictionaryto see if it has a position_tag entry. If yes, it uses that set.
#Otherwise, it uses the default standing images. Right now, this should have changed absolutely nothing about the way the game works.

init -2 python:
    
    import copy
    import math
    import __builtin__
    import pygame
    import re
#    import shader
    
    config.image_cache_size = 12    
    config.layers.insert(1,"Active") ## The "Active" layer is used to display the girls images when you talk to them. The next two lines signal it is to be hidden when you bring up the menu and when you change contexts (like calling a screen)
    config.menu_clear_layers.append("Active")
    config.context_clear_layers.append("Active")
    
    preferences.gl_tearing = True ## Prevents juttery animation with text while using advanced shaders to display images
    pygame.scrap.init()

    def screen_link(r):
        def clicked():
            renpy.exports.launch_editor([r[0]], r[1], transient=1)

        return clicked

    def cursor_pos(st, at):
        return Text("{color=#222}{size=-8}(%d, %d){/size}{/color}"%renpy.get_mouse_pos()), .1

    def copy_cursor_pos():
        pygame.scrap.put(pygame.SCRAP_TEXT, "%d, %d"%renpy.get_mouse_pos())

    class SerumInventory(renpy.store.object): #A bag class that lets businesses and people hold onto different types of serums, and move them around.
        def __init__(self,starting_list):
            self.serums_held = starting_list ##Starting list is a list of tuples, going [SerumDesign,count]. Count should be possitive.
            
        def get_serum_count(self, serum_design):
            for design in self.serums_held:
                if design[0] == serum_design:
                    return design[1]
            return 0
            
        def get_any_serum_count(self):
            count = 0
            for design in self.serums_held:
                count += design[1]
            return count
            
        def change_serum(self, serum_design,change_amount): ##Serum count must be greater than 0. Adds to stockpile of serum_design if it is already there, creates it otherwise.
            found = False
            for design in self.serums_held:
                if design[0] == serum_design and not found:
                    design[1] += int(change_amount)
                    found = True
                    if design[1] <= 0:
                        self.serums_held.remove(design)
                        
            if not found:
                if change_amount > 0:
                    self.serums_held.append([serum_design,int(change_amount)])
                    
                    
        def get_serum_type_list(self): ## returns a list of all the serum types that are in the inventory, without their counts.
            return_values = []
            for design in self.serums_held:
                return_values.append(design[0])
            return return_values



    class Position(renpy.store.object):
        def __init__(self,name,slut_requirement,position_tag,requires_location,requires_clothing,skill_tag,girl_arousal,guy_arousal,connections,intro,scenes,outro,transition_default):
            self.name = name
            self.slut_requirement = slut_requirement #The required slut score of the girl. Obedience will help fill the gap if possible, at a happiness penalty. Value from 0 (almost always possible) to ~100
            self.position_tag = position_tag # The tag used to get the correct position image set
            self.requires_location = requires_location
            self.requires_clothing = requires_clothing
            self.skill_tag = skill_tag #The skill that will provide a bonus to this position.
            self.girl_arousal = girl_arousal # The base arousal the girl recieves from this position.
            self.guy_arousal = guy_arousal # The base arousal the guy recieves from this position.
            self.connections = connections
            self.intro = intro
            self.scenes = scenes
            self.outro = outro
            self.transition_default = transition_default
            self.transitions = []
            
        def link_positions(self,other,transition_label): #This is a one way link!
            self.connections.append(other)
            self.transitions.append([other,transition_label])
            
        def link_positions_two_way(self,other,transition_label_1,transition_label_2): #Link it both ways. Great for adding a modded position without modifying other positions.
            self.link_positions(other,transition_label_1)
            other.link_positions(self,transition_label_2)
            
        def call_intro(self, the_person, the_location, the_object, round):
            renpy.call(self.intro,the_person, the_location, the_object, round)
            
        def call_scene(self, the_person, the_location, the_object, round):
            random_scene = renpy.random.randint(0,len(self.scenes)-1)
            renpy.call(self.scenes[random_scene],the_person, the_location, the_object, round)
            
        def call_outro(self, the_person, the_location, the_object, round):
            renpy.call(self.outro,the_person, the_location, the_object, round)
            
        def call_transition(self,the_position, the_person, the_location, the_object, round):
            if round:
                transition_scene = the_position.transition_default
                for position_tuple in self.transitions:
                    if position_tuple[0] == the_position: ##Does the position match the one we are looking for?
                        transition_scene = position_tuple[1] ##If so, set it's label as the one we are going to change to.
                renpy.call(transition_scene, the_person, the_location, the_object, round)
            else:
                self.call_intro(the_person, the_location, the_object, round)
            
        def check_clothing(self, the_person):
            if self.requires_clothing == "Vagina":
                return the_person.outfit.vagina_available()
            elif self.requires_clothing == "Tits":
                return the_person.outfit.tits_available()
            else:
                return True ##If you don't have one of the requirements listed above just let it happen.


    ##Creator Defined Displayables, used in custom menues throughout the game##

    class Vren_Line(renpy.Displayable):
        def __init__(self, start, end, thickness, color, **kwargs):
            super(Vren_Line,self).__init__(**kwargs)
            ##Base attributes
            self.start = (start[0] * 1920, start[1] * 1080) ## tuple of x,y coords
            self.end = (end[0] * 1920, end[1] * 1080) ## tuple of x,y coords
            self.thickness = thickness
            self.color = color
            
            ##Store normal values for drawing anti-aliased lines
            self.normal_temp = [self.end[0]-self.start[0],self.end[1]-self.start[1]]
            self.normal = [0,0]
            self.normal[0] = -self.normal_temp[1]
            self.normal[1] = self.normal_temp[0]
            self.mag = math.sqrt(math.pow(self.normal[0],2) + math.pow(self.normal[1],2))
            self.normal = [(self.normal[0]*self.thickness)/self.mag,(self.normal[1]*self.thickness)/self.mag]
            
            ##Store point list so we don't have to calculate it each time
            self.start_right = [self.start[0]+self.normal[0],self.start[1]+self.normal[1]]
            self.start_left = [self.start[0]-self.normal[0],self.start[1]-self.normal[1]]
            self.end_left = [self.end[0]+self.normal[0],self.end[1]+self.normal[1]]
            self.end_right = [self.end[0]-self.normal[0],self.end[1]-self.normal[1]]
            
            self.point_list = [self.start_left,self.start_right,self.end_left,self.end_right]
            
        def render(self, width, height, st, at):
            
            render = renpy.Render(1920,1080)
            canvas = render.canvas()
            
            canvas.polygon(self.color,self.point_list,) ##Draw the polygon. It will have jagged edges so we...
            canvas.aalines(self.color,False,self.point_list) ##Also draw a set of antialiased lines around the edge so it doesn't look jagged any more.
            return render
            
        def __eq__(self,other): ## Used to see if two Vren_Line objects are equivelent and thus don't need to be redrawn each time any of the variables is changed.
            if not isinstance(other, Vren_Line):
                return False

            return self.start != other.start or self.end != other.end or self.thickness != other.thickness or self.color != other.color ##ie not the same
            
            
        

init -1:
    python:
        list_of_positions = []
    
    
transform scale_person(scale_factor = 1):
    zoom scale_factor
        
init -2 style textbutton_style: ##The generic style used for text button backgrounds. TODO: Replace this with a pretty background image instead of a flat colour.
    padding [5,5]
    margin [5,5]
    background "#000080"
    insensitive_background "#222222"
    hover_background "#aaaaaa"
    
init -2 style textbutton_text_style: ##The generic style used for the text within buttons
    size 20
    italic True
    bold True
    color "#dddddd"
    outlines [(2,"#222222",0,0)]
    
init -2 style menu_text_style:
    size 18
    italic True
    bold True
    color "#dddddd"
    outlines [(2,"#222222",0,0)]    

init -2 style outfit_style: ##The text style used for text inside of the outfit manager.
    size 16
    italic True
    color "#dddddd"
    outlines [(1,"#666666",0,0)]
    insensitive_color "#222222"
    hover_color "#ffffff"

init -2 python:
    def name_func(name):
        persistent.character["name"] = name

    def b_name_func(name):
        persistent.company_name = name

    def mod_char_param(short, points):
        persistent.character[short] += -1 if points > 0 else 1
        persistent.character_points += points

screen character_create_screen():

    default name_select = 0

    imagebutton auto "/gui/Text_Entry_Bar_%s.png" action SetScreenVariable("name_select",1) pos (320,120) xanchor 0.5 yanchor 0.5
    imagebutton auto "/gui/Text_Entry_Bar_%s.png" action SetScreenVariable("name_select",2) pos (1600,120) xanchor 0.5 yanchor 0.5
    imagebutton auto "/gui/button/choice_%s_background.png" action Return() pos (300,900) xanchor 0.5 yanchor 0.5 sensitive persistent.character_points == 0 and persistent.character["name"][0:11] != "Input Your " and persistent.company_name[0:11] != "Input Your "

    if name_select == 1:
        input default persistent.character["name"] pos(320,120) changed name_func xanchor 0.5 yanchor 0.5 style "menu_text_style" length 25
    else:
        text persistent.character["name"] pos(320,120) xanchor 0.5 yanchor 0.5 style "menu_text_style"

    if name_select == 2:
        input default persistent.company_name pos(1600,120) changed b_name_func xanchor 0.5 yanchor 0.5 style "menu_text_style" length 25
    else:
        text persistent.company_name pos(1600,120) xanchor 0.5 yanchor 0.5 style "menu_text_style"

    if persistent.character_points > 0:
        text "Spend All Character Points to Proceed" style "menu_text_style" anchor(0.5,0.5) pos(300,900)
    elif persistent.character["name"][0:11] == "Input Your ":
        text "Change your name" style "menu_text_style" anchor(0.5,0.5) pos(300,900)
    elif persistent.company_name[0:11] == "Input Your ":
        text "Change your Company Name" style "menu_text_style" anchor(0.5,0.5) pos(300,900)
    else:
        text "Finish Character Creation" style "menu_text_style" anchor(0.5,0.5) pos(300,900)

    text "Character Points Remaining: %d" % persistent.character_points style "menu_text_style" xalign 0.5 yalign 0.1 size 30
    hbox: #Main Stats Section
        yalign 0.7
        xalign 0.5
        xanchor 0.5
        for name, params in Person.stats:
            frame:
                background "#1a45a1aa"
                vbox:
                    xsize 550
                    text "%s (%d points/level)" %(name, MainCharacter.points_per_stat[name]) style "menu_text_style" size 25
                    null height 10
                    for param, short in params:
                        null height 30
                        hbox:
                            text "%s: " % param style "menu_text_style"
                            textbutton "<" action Function(mod_char_param, short, MainCharacter.points_per_stat[name]) sensitive persistent.character[short] > 0 style "textbutton_style" text_style "textbutton_text_style"
                            text "%d" % persistent.character[short] style "textbutton_text_style"
                            textbutton ">" action [Function(mod_char_param, short, -MainCharacter.points_per_stat[name]), SensitiveIf(persistent.character_points >= MainCharacter.points_per_stat[name])] style "textbutton_style" text_style "textbutton_text_style"
                        text "     %s." % Person.stat_desc[param] style "menu_text_style"
            if name != "":
                null width 40

screen main_ui: #The UI that shows most of the important information to the screen.
    frame:
        background "Info_Frame_1.png"
        xsize 600
        ysize 400
        yalign 0.0
        vbox:
            textbutton "Outfit Manager" action ui.callsinnewcontext("outfit_design_loop") style "textbutton_style" text_style "textbutton_text_style"
            textbutton "Check Inventory" action ui.callsinnewcontext("check_inventory_loop") style "textbutton_style" text_style "textbutton_text_style"
            textbutton "Character Sheet" action Show("mc_character_sheet") style "textbutton_style" text_style "textbutton_text_style"
            text "Day: %s(%d)" % (world.day_names[world.day%7], world.day) style "menu_text_style"
            text "Time: %s" % world.time_names[world.time_of_day] style "menu_text_style"
#            text "Energy: %d" % world.mc.energy style "menu_text_style"
            text "Arousal: %d/100" % world.mc.arousal style "menu_text_style"
            text "Cash: $%d" % world.mc.money style "menu_text_style"
            text "Location: %s" % world.mc.location.name.title() style "menu_text_style"
        
screen business_ui: #Shows some information about your business.
    frame:
        background im.Flip("Info_Frame_1.png",vertical=True)
        xsize 600
        ysize 400
        yalign 1.0
        vbox:
            yanchor 1.0
            yalign 1.0
            text "Company Name: " style "menu_text_style"
            text "    %s" % world.mc.business.name style "menu_text_style"
            text "Company Funds: $%d" % world.mc.business.funds style "menu_text_style"
            text "Daily Salary Cost: $%d" % world.mc.business.calculate_salary_cost() style "menu_text_style"
            text "Company Efficency: %d%%" % world.mc.business.team_effectiveness style "menu_text_style"
#            text "Company Marketability: %d" % world.mc.business.marketability style "menu_text_style"
            text "Current Raw Supplies: %d (Target:%d)" % (world.mc.business.supply_count, world.mc.business.supply_goal) style "menu_text_style"
            if world.mc.business.active_research_design:
                text "Current Research: " style "menu_text_style"
                text "    %(name)s (%(research done).1f/%(research required).1f)" % world.mc.business.active_research_design style "menu_text_style"
            else:
                text "Current Research: None!" style "menu_text_style" color "#DD0000"
            if world.mc.business.serum_production_target:
                text "Currently Producing: " style "menu_text_style"
                text "    %s" % world.mc.business.serum_production_target["name"] style "menu_text_style"
            else:
                text "Currently Producing: Nothing!" style "menu_text_style" color "#DD0000"
            textbutton "Review Staff" action Show("employee_overview") style "textbutton_style" text_style "textbutton_text_style"
            textbutton "Check Stock" action ui.callsinnewcontext("check_business_inventory_loop") style "textbutton_style" text_style "textbutton_text_style"
            
screen end_of_day_update():
    add "Paper_Background.png"
    text world.mc.business.name:
        style "textbutton_text_style"
        xanchor 0.5
        xalign 0.5
        yalign 0.1
        size 40
    
    frame:
        background "#1a45a1aa"
        xalign 0.1
        yalign 0.25
        xanchor 0.0
        vbox:
            xsize 1500
            ysize 200
            text "Daily Statistics:" style "textbutton_text_style" size 20
            text "     Current Efficency Modifier: %d" % world.mc.business.team_effectiveness style "textbutton_text_style"
            text "     Production Potential: %d" % world.mc.business.production_potential style "textbutton_text_style"
            text "     Supplies Procured: %d Units" % world.mc.business.supplies_purchased style "textbutton_text_style"
            text "     Production Used: %d" % world.mc.business.production_used style "textbutton_text_style"
            text "     Research Produced: %d" % world.mc.business.research_produced style "textbutton_text_style"
            text "     Sales Made: $%d" % world.mc.business.sales_made style "textbutton_text_style"
            text "     Daily Salary Paid: $%d" % world.mc.business.calculate_salary_cost() style "textbutton_text_style"
    
    frame:
        background "#1a45a1aa"
        xalign 0.1
        yalign 0.45
        xanchor 0.0
        yanchor 0.0
        viewport:
            mousewheel True
            scrollbars "vertical"
            xsize 1500
            ysize 350
            vbox:
                text "Highlights:" style "textbutton_text_style" size 20
                for item, count in world.mc.business.message_list.iteritems():
                    if count > 0:
                        text "     %s x %d" % (item, count) style "textbutton_text_style"
                    elif isinstance(item, basestring):
                        text "     %s" % item style "textbutton_text_style"
                    elif isinstance(item, tuple) and isinstance(item[0], Person):
                        text "     %s (%s) %s" % (item[0].name, item[0].job, item[1]) style "textbutton_text_style"
    
    frame:
        background None
        anchor [0.5,0.5]
        align [0.5,0.9]
        xysize [500,125]
        imagebutton:
            align [0.5,0.5]
            auto "gui/button/choice_%s_background.png"
            focus_mask "gui/button/choice_idle_background.png"
            action Return()
        textbutton "End Day" align [0.5,0.5] style "button_text"
        
screen employee_overview():
    add "Paper_Background.png"
    default div = world.mc.business.r_div
    default sp = max(map(lambda p: len(Person.terse_stat[p])*35 if p in Person.terse_stat else len(p)*35, [x[1] for sk, x in Person.stats if sk != "Sex Skills"]))
    modal True
    hbox:
        yalign 0.05
        xalign 0.05
        textbutton "Research" action SetScreenVariable("div",world.mc.business.r_div) style "textbutton_style" text_style "textbutton_text_style"
        textbutton "Production" action SetScreenVariable("div",world.mc.business.p_div) style "textbutton_style" text_style "textbutton_text_style"
        textbutton "Supply" action SetScreenVariable("div",world.mc.business.s_div) style "textbutton_style" text_style "textbutton_text_style"
        textbutton "Marketing" action SetScreenVariable("div",world.mc.business.m_div) style "textbutton_style" text_style "textbutton_text_style"
        textbutton "Human Resources" action SetScreenVariable("div",world.mc.business.h_div) style "textbutton_style" text_style "textbutton_text_style"

    text "Position: %s" % div.name style "menu_text_style" size 20 yalign 0.12 xalign 0.02 xanchor 0.0
    frame:
        top_margin 0
        yalign 0.15
        xalign 0.5
        yanchor 0.0
        background "#1a45a1aa"
        xsize 1800
        ysize 700
        vpgrid id "Positions_list":
            area (1,1,1800,700)
            #child_size (100, 100)
            draggable True mousewheel True
            cols sum(len(params) for stat_name, params in Person.stats if stat_name != "Sex Skills") + 6
            xspacing sp
            yspacing 35
            #side_yfill True
            rows len(div.people) + 2
            #side_xalign 0.5
            side_yalign 0.0
            scrollbars "vertical"
            yminimum 35
            yalign 0.0

            text "Name" style "menu_text_style"
            text "Salary" style "menu_text_style"
            text "Happiness" style "menu_text_style"
            text "Obedience" style "menu_text_style"
            text "Sluttiness" style "menu_text_style"
            text "Suggest" style "menu_text_style"
            for stat_name, params in Person.stats:
                if stat_name != "Sex Skills":
                    for param, short in params:
                        if param in Person.terse_stat:
                            text Person.terse_stat[param] style "menu_text_style"
                        else:
                            text param style "menu_text_style"

            for person in div.people:
                textbutton person.name + "\n" + person.last_name style "textbutton_style" text_style "menu_text_style" action Show("person_info_detailed",None,person)
#               text person.name + "\n" + person.last_name style "menu_text_style"
                text "$%d/world.day" % person.salary style "menu_text_style"
                text str(int(person.happiness)) style "menu_text_style"
                text str(int(person.obedience)) style "menu_text_style"
                text str(int(person.sluttiness)) style "menu_text_style"
                text str(int(person.suggestibility)) style "menu_text_style"
                for stat_name, params in Person.stats:
                    if stat_name != "Sex Skills":
                        for param, short in params:
                            text str(int(getattr(person, short))) style "menu_text_style"
    frame:
        background None
        anchor [0.5,0.5]
        align [0.5,0.88]
        xysize [500,125]
        imagebutton:
            align [0.5,0.5]
            auto "gui/button/choice_%s_background.png"
            focus_mask "gui/button/choice_idle_background.png"
            action Hide("employee_overview")
        textbutton "Return" align [0.5,0.5] style "return_button_style"
    
            
screen person_info_ui(the_person): #Used to display stats for a person while you're talking to them.
    frame:
        background im.Flip("Info_Frame_1.png",vertical=True)
        xsize 400
        ysize 400
        yalign 1.0
        vbox:
            yalign 1.0
            text "Name: %s" % the_person.name style "menu_text_style"
            if world.mc.business.get_employee_title(the_person) == "None":
                text "Job: Not employed." style "menu_text_style"
            else:
                text "Job: " + world.mc.business.get_employee_title(the_person) style "menu_text_style"
            #text "Height: " + height_to_string(the_person.height) #Showing this here during sex scenes breaks things for some reason, might be use of "height" as a variable name?
            text "Arousal: %d/100" % the_person.arousal style "menu_text_style"
            text "***********" style "menu_text_style"
            text "Happiness: %d" % the_person.happiness style "menu_text_style"
            text "Suggestibility: %d" % the_person.suggestibility style "menu_text_style"
            text "Sluttiness: %d" % the_person.sluttiness style "menu_text_style"
            text "Obedience: %d" % the_person.obedience style "menu_text_style"
            textbutton "Detailed Information" action Show("person_info_detailed",the_person=the_person) style "textbutton_style" text_style "textbutton_text_style"
            
            
screen person_info_detailed(the_person):
    add "Paper_Background.png"
    modal True
    default hr_base = the_person.charisma*3 + the_person.hr_skill*2 + the_person.int + 10
    default market_base = the_person.charisma*3 + the_person.market_skill*2 + the_person.focus + 10
    default research_base = the_person.int*3 + the_person.research_skill*2 + the_person.focus + 10
    default prod_base = the_person.focus*3 + the_person.production_skill*2 + the_person.int + 10
    default supply_base = the_person.focus*3 + the_person.supply_skill*2 + the_person.charisma + 10
    
    hbox:
        xalign 0.1
        yalign 0.1
        vbox:
            xsize 1000
            text "Name: %s %s" % (the_person.name, the_person.last_name) style "menu_text_style" size 25
            text "Height: " + str(height_to_string(the_person.height)) style "menu_text_style" #TODO: Figure out why calling height while in a sex scene breaks everything.
            for stat_name, params in Person.stats:
                if stat_name != "Sex Skills":
                    text "**********" style "menu_text_style"
                    for param, short in params:
                        text "%s: %d" % (param, getattr(the_person, short)) style "menu_text_style"

            null height 200
            if world.mc.business.get_employee_title(the_person) != "None":
                text "Position: " + world.mc.business.get_employee_title(the_person) style "menu_text_style"
                text "Current Salary: $%d" % the_person.salary style "menu_text_style"
                text "Base HR Efficency Production (Cha x 3 + Skill x 2 + Int x 1 + 10): %d" % hr_base style "menu_text_style"
                text "Base Marketing Sales Cap (Cha x 3 + Skill x 2 + Focus x 1 + 10): %d" % market_base style "menu_text_style"
                text "Base Research Generation (Int x 3 + Skill x 2 + Focus x 1 + 10): %d" % research_base style "menu_text_style"
                text "Base Production Generation (Focus x 3 + Skill x 2 + Int x 1 + 10): %d" % prod_base style "menu_text_style"
                text "Base Supply Generation (Focus x 3 + Skill x 2 + Cha x 1 + 10): %d" % supply_base style "menu_text_style"

        vbox:
            xsize 800
            if the_person.serum_effects:
                text "Currently Affected By:" style "menu_text_style"
                for name, serum in map(lambda x: (x["name"], world.mc.business.serum_designs[x["name"]]), the_person.serum_effects):
                    text "%s : %d Turns left" % (name, serum["duration"] - serum["time"]) style "menu_text_style"
                null height 80
            if the_person.status_effects:
                text "Current Status Effects:" style "menu_text_style"
                for effect in set(the_person.status_effects):
                    text effect["name"] style "menu_text_style"

    frame:
        background None
        anchor [0.5,0.5]
        align [0.5,0.88]
        xysize [500,125]
        imagebutton:
            align [0.5,0.5]
            auto "gui/button/choice_%s_background.png"
            focus_mask "gui/button/choice_idle_background.png"
            action Hide("person_info_detailed")
        textbutton "Return" align [0.5,0.5] style "return_button_style"
        
screen mc_character_sheet(): #TODO: Impliment a level up system for the main character
    add "Paper_Background.png"
    modal True
    vbox:
        xalign 0.5
        yalign 0.05
        text world.mc.name style "menu_text_style" size 40 xanchor 0.5 xalign 0.5
        text "Owner of: " + world.mc.business.name style "menu_text_style" size 30 xanchor 0.5 xalign 0.5
        
    hbox:
        xanchor 0.5
        xalign 0.5
        yalign 0.2
        for stat_name, params in Person.stats:
            vbox:
                xsize 600
                text stat_name style "menu_text_style" size 25 xalign 0.5
                for param, short in params:
                    text "%s: %d" % (param, getattr(mc, short)) style "menu_text_style" xalign 0.5

    frame:
        background None
        anchor [0.5,0.5]
        align [0.5,0.88]
        xysize [500,125]
        imagebutton:
            align [0.5,0.5]
            auto "gui/button/choice_%s_background.png"
            focus_mask "gui/button/choice_idle_background.png"
            action Hide("mc_character_sheet")
        textbutton "Return" align [0.5,0.5] text_style "return_button_style"
        
    
    
    
        
screen interview_ui(the_candidates,count):
    default current_selection = 0
    default the_candidate = the_candidates[current_selection]
    hbox:
        vbox:
            xsize 600
            text "Name: %s" % the_candidate.name style "menu_text_style"
            text "Age: %d" % the_candidate.age style "menu_text_style"
            text "Daily Salary: $%d" % the_candidate.salary style "menu_text_style"

        vbox:
            xsize 600
            for stat_name, params in Person.stats:
                if stat_name != "Sex Skills":
                    for param, short in params:
                        text "%s: %d" % (param, getattr(the_candidate, short)) style "menu_text_style"
                    if stat_name != "Work Skills":
                        text "*******" style "menu_text_style"

    hbox:
        xalign 0.0
        yalign 1.0
        vbox:
            textbutton "Hire " action Return(the_candidate) style "textbutton_style" text_style "textbutton_text_style"
            textbutton "Next Candidate" action [SetScreenVariable("current_selection",current_selection+1),
                SetScreenVariable("the_candidate",the_candidates[current_selection+1]),
                Function(show_candidate,the_candidates[current_selection+1])] sensitive current_selection < count-1 selected False style "textbutton_style" text_style "textbutton_text_style"
            
            
            textbutton "Previous Candidate" action [SetScreenVariable("current_selection",current_selection-1),
                SetScreenVariable("the_candidate",the_candidates[current_selection-1]),
                Function(show_candidate,the_candidates[current_selection-1])] sensitive current_selection > 0 selected False style "textbutton_style" text_style "textbutton_text_style"
            
            textbutton "Hire Nobody" action Return("None") style "textbutton_style" text_style "textbutton_text_style"
         
init -2 python: # Some functions used only within screens for modifying variables
    def show_candidate(the_candidate):
        renpy.scene("Active")
        the_candidate.draw_person("stand1")

    def add_trait_to_serum(name, trait, serum, add=True):
        if add: # trait["name"] != name
            serum["traits"].add(name)
        else:
            serum["traits"].remove(name)

        for t in ["trait", "effect"]:
            for k, v in trait[t].iteritems():
                serum[k] += v if add else -v

screen show_serum_inventory(the_inventory):
    add "Science_Menu_Background.png"
    vbox:
        xalign 0.02
        yalign 0.02
        text "Serums in Inventory" style "menu_text_style" size 25
        for design in the_inventory.serums_held:
            textbutton design[0].name + ": " + str(design[1]) style "textbutton_style" text_style "textbutton_text_style" action NullAction() sensitive True hovered Show("serum_tooltip",None,design[0]) unhovered Hide("serum_tooltip")

        textbutton "Return" action Return() style "textbutton_style" text_style "textbutton_text_style"

screen serum_design_ui():
    add "Science_Menu_Background.png"
    default serum = {"charisma": 0, "cupsize": 0, "duration": 1, "focus": 0, "happiness": 0, "int": 0, "obedience": 0, "production": 10, "sluttiness": 0, "suggest": 10, "value": 10, "research required": 50, "research done": 0, "traits": set()}
    hbox:
        xalign 0.01
        ysize 400
        vbox:
            xsize 600
            text "Add a new trait" style "menu_text_style"
            for name, trait in world.mc.business.serum_traits.iteritems():
                if name not in serum["traits"] and trait["research done"] >= trait["research required"]:
                    textbutton "Add %s" % trait["name"] action [Hide("trait_tooltip"),Function(add_trait_to_serum,name, trait, serum)] style "textbutton_style" text_style "textbutton_text_style" hovered Show("trait_tooltip",None,trait,0.3,0.6) unhovered Hide("trait_tooltip")

        vbox:
            xsize 600
            text "Remove a trait" style "menu_text_style"
            for name in serum["traits"]:
                textbutton "Remove %s" % name action Function(add_trait_to_serum, name, world.mc.business.serum_traits[name], serum, False) style "textbutton_style" text_style "textbutton_text_style"

        vbox:
            xsize 600
            text "Current Traits:" style "menu_text_style"
            for name in serum["traits"]:
                text "Trait: %s" % name style "menu_text_style"
                text "*******" style "outfit_style"
                text "Description: %s" % world.mc.business.serum_traits[name]["desc"] style "menu_text_style"
                text " " style "ouftit_style"

    hbox:
        ysize 300
        yalign 0.6
        xalign 0.01
        vbox:
            text "Current Serum Statistics:" style "menu_text_style"
            text "Research Required: %d" % serum["research required"] style "menu_text_style"
            text "Production Cost: %d" % serum["production"] style "menu_text_style"
            text "Value: %d" % serum["value"] style "menu_text_style"
            text "Duration (Time Segments): %d" % serum["duration"] style "menu_text_style"
            text "Suggestion: %d" % serum["suggest"] style "menu_text_style"
            text "Happiness: %d" % serum["happiness"] style "menu_text_style"
            text "Sluttiness: %d" % serum["sluttiness"] style "menu_text_style"
            text "Obedience: %d" % serum["obedience"] style "menu_text_style"
            text "Charisma Boost: %d" % serum["charisma"] style "menu_text_style"
            text "Intelligence Boost: %d" % serum["int"] style "menu_text_style"
            text "Focus Boost: %d" % serum["focus"] style "menu_text_style"

    hbox:
        yalign 0.9
        xalign 0.01
        vbox:
            textbutton "Create serum design." action Return(serum) style "textbutton_style" text_style "textbutton_text_style"
            textbutton "Quit." action Return("None") style "textbutton_style" text_style "textbutton_text_style"

screen serum_tooltip(serum):
    vbox:
        xalign 0.9
        yalign 0.0
        xsize 500
        text "Research Required: %d" % serum["research required"] style "menu_text_style"
        text "Production Cost: %d" % serum["production"] style "menu_text_style"
        text "Value: %d" % serum["value"] style "menu_text_style"
        text "Duration (Time Segments): %d" % serum["duration"] style "menu_text_style"
        text "Suggestion: %d" % serum["suggest"] style "menu_text_style"
        text "Happiness: %d" % serum["happiness"] style "menu_text_style"
        text "Sluttiness: %d" % serum["sluttiness"] style "menu_text_style"
        text "Obedience: %d" % serum["obedience"] style "menu_text_style"
        text "Charisma Boost: %d" % serum["charisma"] style "menu_text_style"
        text "Intelligence Boost: %d" % serum["int"] style "menu_text_style"
        text "Focus Boost: %d" % serum["focus"] style "menu_text_style"
        text ""
        if serum["value"] > 10:
            text "*********\n" style "menu_text_style"
        for name in serum["traits"]:
            text "Trait: " + name style "menu_text_style"
            text world.mc.business.serum_traits[name]["desc"] style "menu_text_style"
            text "\n*********\n" style "menu_text_style"
            
screen trait_tooltip(the_trait,given_xalign=0.9,given_yalign=0.0):
    vbox:
        xalign given_xalign
        yalign given_yalign
        xsize 500
        text the_trait["name"] style "menu_text_style"
        text "\n*********\n" style "menu_text_style"
        text "Research Required: %d" % the_trait["research required"] style "menu_text_style"
        text the_trait["desc"] style "menu_text_style"
            
            
screen serum_trade_ui(inventory_1,inventory_2,name_1="Player",name_2="Business"): #Lets you trade serums back and forth between two different inventories. Inventory 1 is assumed to be the players.
    add "Science_Menu_Background.png"
    vbox:
        xalign 0.02
        yalign 0.02
        text "Trade Serums Between Inventories." style "menu_text_style" size 25
        for serum in set(inventory_1.get_serum_type_list()) | set(inventory_2.get_serum_type_list()): #Gets a unique entry for each serum design that shows up in either list. Doesn't duplicate if it's in both.
            # has a few things. 1) name of serum design. 2) count of first inventory, 3) arrows for transfering, 4) count of second inventory.
            vbox:
                textbutton serum.name + ": " style "textbutton_style" text_style "menu_text_style" action NullAction() hovered Show("serum_tooltip",None,serum) unhovered Hide("serum_tooltip") #displays the name of this particular serum
                hbox:
                    null width 40
                    text name_1 + " has: " + str(inventory_1.get_serum_count(serum)) style "menu_text_style"#The players current inventory count. 0 if there is nothing in their inventory
                    textbutton "#<#" action [Function(inventory_1.change_serum,serum,1),Function(inventory_2.change_serum,serum,-1)] sensitive (inventory_2.get_serum_count(serum) > 0) style "textbutton_style" text_style "textbutton_text_style"
                    #When pressed, moves 1 serum from the business inventory to the player. Not active if the business has nothing in it.
                    null width 40
                    textbutton "#>#" action [Function(inventory_2.change_serum,serum,1),Function(inventory_1.change_serum,serum,-1)] sensitive (inventory_1.get_serum_count(serum) > 0) style "textbutton_style" text_style "textbutton_text_style"
                    text name_2 + " has: " + str(inventory_2.get_serum_count(serum)) style "menu_text_style"
        textbutton "Finished." action Return() style "textbutton_style" text_style "textbutton_text_style"
                
                
screen serum_select_ui: #How you select serum and trait research
    add "Science_Menu_Background.png"
    vbox:
        if world.mc.business.active_research_design != None:
            text "Current Research: %(name)s (%(research done).1f/%(research required).1f)" % world.mc.business.active_research_design style "menu_text_style"
        else:
            text "Current Research: None!" style "menu_text_style"
        
        hbox:
            vbox:
                text "Serum Designs:" style "menu_text_style"
                for serum in world.mc.business.serum_designs:
                    if serum["research done"] < serum["research required"]:
                        textbutton "Research %(name)s (%(research done)d/%(research required)d)" % serum action [Hide("serum_tooltip"),Return(serum)] style "textbutton_style" text_style "textbutton_text_style" hovered Show("serum_tooltip",None,serum) unhovered Hide("serum_tooltip")
             
            null width 40
            
        vbox:
            text "New Traits:" style "menu_text_style"
            for name, trait in world.mc.business.serum_traits.iteritems():
                if not trait["research done"] >= trait["research required"] and all(t["research done"] >= t["research required"] for t in map(lambda x: world.mc.business.serum_traits[x], trait["requires"])):
                    textbutton "%(name)s (%(research done)d/%(research required)d)" % trait action [Hide("trait_tooltip"),Return(trait)] style "textbutton_style" text_style "textbutton_text_style" hovered Show("trait_tooltip",None,trait) unhovered Hide("trait_tooltip")
                    
    textbutton "Do not change research." action Return("None") style "textbutton_style" text_style "textbutton_text_style" yalign 0.995
        
screen serum_production_select_ui:
    add "Science_Menu_Background.png"
    vbox:
        xalign 0.1
        xsize 1200
        null height 40 
        if world.mc.business.serum_production_target != None:
            text "Currently Producing: %(name)s - $%(value)d/dose (Current Progress: %(research done).1f/%(research required).1f)" % world.mc.business.serum_production_target style "menu_text_style" size 25
        else:
            text "Currently Producing: Nothing!" style "menu_text_style"
        
        null height 40
        text "Change Production To:" style "menu_text_style" size 20
        vbox:
            xsize 1000
            xalign 0.2
            for serum in world.mc.business.serum_designs:
                if serum["research done"] < serum["research required"]:
                    textbutton "Produce %(name)s (Requires %(production)d production points per dose. Worth $%(value)d/dose)" % serum action [Hide("serum_tooltip"),Return(serum)] style "textbutton_style" text_style "textbutton_text_style" hovered Show("serum_tooltip",None,serum) unhovered Hide("serum_tooltip")
        textbutton "Do not change production." action Return("None") style "textbutton_style" text_style "textbutton_text_style"
        
screen serum_inventory_select_ui(the_inventory): #Used to let the player select a serum from an inventory.
    add "Science_Menu_Background.png"
    vbox:
        for serum, count in the_inventory.serums_held.iteritems():
            textbutton "%s (%d)" % (serum, count) action [Hide("serum_tooltip"),Return(serum[0])] style "textbutton_style" text_style "textbutton_text_style" hovered Show("serum_tooltip",None,serum[0]) unhovered Hide("serum_tooltip")
        textbutton "Return" action Return("None") style "textbutton_style" text_style "textbutton_text_style"
            
        
screen outfit_creator(starting_outfit): ##Pass a completely blank outfit instance for a new outfit, or an already existing instance to load an old one.\
    add "Paper_Background.png"
    default panties_label = "None"
    default bra_label = "None"
    default pants_label = "None"
    default skirts_label = "None"
    default dress_label = "None"
    default shirts_label = "None"
    default socks_label = "None"
    default shoes_label = "None"
    default demo_outfit = copy.deepcopy(starting_outfit)
    #Each catagory below has a click to enable button. If it's false, we don't show anything for it.
    hbox:
        vbox:
            xsize 400
            spacing -20
            text "Add Clothing" style "menu_text_style"
            null height 50
            
            textbutton "Panties" action ToggleScreenVariable("panties_label","Panties","None") style "textbutton_style" text_style "textbutton_text_style"
            null height 30
            if panties_label == "Panties":
                for cloth in panties_list:
                    textbutton "    " + cloth.name:
                        action Function(starting_outfit.add_lower, cloth) sensitive starting_outfit.can_add_lower(cloth) text_style "outfit_style" hovered Function(demo_outfit.add_lower, cloth) unhovered Function(demo_outfit.remove_clothing, cloth)
            null height 30
            
            textbutton "Bras" action ToggleScreenVariable("bra_label","Bras","None") style "textbutton_style" text_style "textbutton_text_style"
            null height 30
            if bra_label == "Bras":
                for cloth in bra_list:
                    textbutton "    " + cloth.name action Function(starting_outfit.add_upper, cloth) sensitive starting_outfit.can_add_upper(cloth) text_style "outfit_style" hovered Function(demo_outfit.add_upper, cloth) unhovered Function(demo_outfit.remove_clothing, cloth)
            null height 30
            
            textbutton "Pants" action ToggleScreenVariable("pants_label","Pants","None") style "textbutton_style" text_style "textbutton_text_style"
            null height 30
            if pants_label == "Pants":
                for cloth in pants_list:
                    textbutton "    " + cloth.name action Function(starting_outfit.add_lower, cloth) sensitive starting_outfit.can_add_lower(cloth) text_style "outfit_style" hovered Function(demo_outfit.add_lower, cloth) unhovered Function(demo_outfit.remove_clothing, cloth)
            null height 30
            
            textbutton "Skirts" action ToggleScreenVariable("skirts_label","Skirts","None") style "textbutton_style" text_style "textbutton_text_style"
            null height 30
            if skirts_label == "Skirts":
                for cloth in skirts_list:
                    textbutton "    " + cloth.name action Function(starting_outfit.add_lower, cloth) sensitive starting_outfit.can_add_lower(cloth) text_style "outfit_style" hovered Function(demo_outfit.add_lower, cloth) unhovered Function(demo_outfit.remove_clothing, cloth)
            null height 30
            
            textbutton "Dresses" action ToggleScreenVariable("dress_label","Dress","None") style "textbutton_style" text_style "textbutton_text_style"
            null height 30
            if dress_label == "Dress":
                for cloth in dress_list:
                    textbutton "    " + cloth.name action Function(starting_outfit.add_dress, cloth) sensitive starting_outfit.can_add_dress(cloth) text_style "outfit_style" hovered Function(demo_outfit.add_dress, cloth) unhovered Function(demo_outfit.remove_clothing, cloth)
            null height 30
             
            textbutton "Shirts" action ToggleScreenVariable("shirts_label","Shirts","None") style "textbutton_style" text_style "textbutton_text_style"
            null height 30
            if shirts_label == "Shirts":
                for cloth in shirts_list:
                    textbutton "    " + cloth.name action Function(starting_outfit.add_upper, cloth) sensitive starting_outfit.can_add_upper(cloth) text_style "outfit_style" hovered Function(demo_outfit.add_upper, cloth) unhovered Function(demo_outfit.remove_clothing, cloth)
            null height 30
            
            textbutton "Socks" action ToggleScreenVariable("socks_label","Socks","None") style "textbutton_style" text_style "textbutton_text_style"
            null height 30
            if socks_label == "Socks":
                for cloth in socks_list:
                    textbutton "    " + cloth.name action Function(starting_outfit.add_feet, cloth) sensitive starting_outfit.can_add_feet(cloth) text_style "outfit_style" hovered Function(demo_outfit.add_feet, cloth) unhovered Function(demo_outfit.remove_clothing, cloth)
            null height 30
                
            textbutton "Shoes" action ToggleScreenVariable("shoes_label","Shoes","None") style "textbutton_style" text_style "textbutton_text_style"
            null height 30
            if shoes_label == "Shoes":
                for cloth in shoes_list:
                    textbutton "    " + cloth.name action Function(starting_outfit.add_feet, cloth) sensitive starting_outfit.can_add_feet(cloth) text_style "outfit_style" hovered Function(demo_outfit.add_feet, cloth) unhovered Function(demo_outfit.remove_clothing, cloth)
            null height 30
        
        null width 80 height 100 ## Adds an empty space
        
        vbox:
            text "Remove Clothing" style "menu_text_style"
            for cloth in starting_outfit.upper_body:
                if not cloth.is_extension: #Don't list extensions for removal.
                    textbutton cloth.name action [Function(starting_outfit.remove_clothing, cloth),Function(demo_outfit.remove_clothing, cloth)] text_style "outfit_style"
                
            for cloth in starting_outfit.lower_body:
                if not cloth.is_extension:
                    textbutton cloth.name action [Function(starting_outfit.remove_clothing, cloth),Function(demo_outfit.remove_clothing, cloth)] text_style "outfit_style"
                
            for cloth in starting_outfit.feet:
                if not cloth.is_extension:
                    textbutton cloth.name action [Function(starting_outfit.remove_clothing, cloth),Function(demo_outfit.remove_clothing, cloth)] text_style "outfit_style"
                
            for cloth in starting_outfit.accessories:
                if not cloth.is_extension:
                    textbutton cloth.name action [Function(starting_outfit.remove_clothing, cloth),Function(demo_outfit.remove_clothing, cloth)] text_style "outfit_style"
                
        null width  80 height 100 ## More whitespace
        
        vbox:
            text "Outfit Stats" style "menu_text_style"
            text "Sluttiness Required: %d" % demo_outfit.slut_requirement style "menu_text_style"
            text "Tits Visible: " + str(demo_outfit.tits_visible()) style "menu_text_style"
            text "Tits Usable: " + str(demo_outfit.tits_available()) style "menu_text_style"
            text "Wearing a Bra: " + str(demo_outfit.wearing_bra()) style "menu_text_style"
            text "Bra Covered: " + str(demo_outfit.bra_covered()) style "menu_text_style"
            text "Pussy Visible: " + str(demo_outfit.vagina_visible()) style "menu_text_style"
            text "Pussy Usable: " + str(demo_outfit.vagina_available()) style "menu_text_style"
            text "Wearing Panties: " + str(demo_outfit.wearing_panties()) style "menu_text_style"
            text "Panties Covered: " + str(demo_outfit.panties_covered()) style "menu_text_style"
        
        null width  80 height 100 ## More whitespace
        
        vbox:
            textbutton "Save Outfit" pos (0,0) action Return(copy.deepcopy(starting_outfit)) style "textbutton_style" text_style "textbutton_text_style"
            
        null width  80 height 100
            
        vbox:
            textbutton "Leave Without Saving" pos (0,0) action Return("Not_New") style "textbutton_style" text_style "textbutton_text_style"
        
    fixed: #TODO: Move this to it's own screen so it can be shown anywhere
        pos (1500,0)
        
        add mannequin_average
        for cloth in sorted(demo_outfit.feet+demo_outfit.lower_body+demo_outfit.upper_body, key=lambda clothing: clothing.layer):
            if not cloth.is_extension:
                if cloth.draws_breasts:
                    $ coloured_image = im.Recolor(cloth.position_sets.get("stand1").images["Average_D"].filename,int(cloth.colour[0]*255),int(cloth.colour[1]*255),int(cloth.colour[2]*255),int(cloth.colour[3]*255))
                    add coloured_image
                    #add ShaderDisplayable(shader.MODE_2D, cloth.position_sets.get("stand1").images["Average_D"].filename, shader.VS_2D,PS_COLOUR_SUB_LR2,{},uniforms={"colour_levels":cloth.colour})
                else:
                    $ coloured_image = im.Recolor(cloth.position_sets.get("stand1").images["Average_AA"].filename,int(cloth.colour[0]*255),int(cloth.colour[1]*255),int(cloth.colour[2]*255),int(cloth.colour[3]*255))
                    add coloured_image
                    #add ShaderDisplayable(shader.MODE_2D, cloth.position_sets.get("stand1").images["Average_AA"].filename, shader.VS_2D,PS_COLOUR_SUB_LR2,{},uniforms={"colour_levels":cloth.colour})
                
screen outfit_delete_manager(the_wardrobe): ##Allows removal of outfits from players saved outfits. TODO: Expand this to general manager.
    add "Paper_Background.png"
    default preview_outfit = None
    vbox:
        for outfit in the_wardrobe.get_outfit_list():
            textbutton "Delete %s (Sluttiness %d)" % (outfit.name, outfit.slut_requirement) action Function(the_wardrobe.remove_outfit,outfit) hovered SetScreenVariable("preview_outfit", copy.deepcopy(outfit)) unhovered SetScreenVariable("preview_outfit", None) style "textbutton_style" text_style "textbutton_text_style"
        
        textbutton "Return" action Return() style "textbutton_style" text_style "textbutton_text_style"
        
    fixed:
        pos (1500,0)
        add mannequin_average
        if preview_outfit:
            for cloth in sorted(preview_outfit.feet+preview_outfit.lower_body+preview_outfit.upper_body, key=lambda clothing: clothing.layer):
                if not cloth.is_extension:
                    if cloth.draws_breasts:
                        $ coloured_image = im.Recolor(cloth.position_sets.get("stand1").images["Average_D"].filename,int(cloth.colour[0]*255),int(cloth.colour[1]*255),int(cloth.colour[2]*255),int(cloth.colour[3]*255))
                        add coloured_image
                        #add ShaderDisplayable(shader.MODE_2D, cloth.position_sets.get("stand1").images["Average_D"].filename, shader.VS_2D,PS_COLOUR_SUB_LR2,{},uniforms={"colour_levels":cloth.colour})
                    else:
                        $ coloured_image = im.Recolor(cloth.position_sets.get("stand1").images["Average_AA"].filename,int(cloth.colour[0]*255),int(cloth.colour[1]*255),int(cloth.colour[2]*255),int(cloth.colour[3]*255))
                        add coloured_image
                        #add ShaderDisplayable(shader.MODE_2D, cloth.position_sets.get("stand1").images["Average_AA"].filename, shader.VS_2D,PS_COLOUR_SUB_LR2,{},uniforms={"colour_levels":cloth.colour})
                    
screen outfit_select_manager(slut_limit = 999): ##Brings up a list of the players current saved outfits, returns the selected outfit or None.
    #If sluttiness_limit is passed, you cannot exit the creator until the proposed outfit has a sluttiness below it.
    add "Paper_Background.png"
    
    default preview_outfit = None
    vbox:
        for outfit in world.mc.designed_wardrobe.get_outfit_list():
            textbutton "Load %s (Sluttiness %d)" % (outfit.name, outfit.slut_requirement) action Return(copy.deepcopy(outfit)) sensitive (outfit.slut_requirement <= slut_limit) hovered SetScreenVariable("preview_outfit", copy.deepcopy(outfit)) unhovered SetScreenVariable("preview_outfit", None) style "textbutton_style" text_style "textbutton_text_style"
            
        textbutton "Return" action Return("No Return") style "textbutton_style" text_style "textbutton_text_style"
        
    fixed:
        pos (1500,0)
        add mannequin_average
        if preview_outfit:
            for cloth in sorted(preview_outfit.feet+preview_outfit.lower_body+preview_outfit.upper_body, key=lambda clothing: clothing.layer):
                if not cloth.is_extension:
                    if cloth.draws_breasts:
                        $ coloured_image = im.Recolor(cloth.position_sets.get("stand1").images["Average_D"].filename,int(cloth.colour[0]*255),int(cloth.colour[1]*255),int(cloth.colour[2]*255),int(cloth.colour[3]*255))
                        add coloured_image
                        #add ShaderDisplayable(shader.MODE_2D, cloth.position_sets.get("stand1").images["Average_D"].filename, shader.VS_2D,PS_COLOUR_SUB_LR2,{},uniforms={"colour_levels":cloth.colour})
                    else:
                        $ coloured_image = im.Recolor(cloth.position_sets.get("stand1").images["Average_AA"].filename,int(cloth.colour[0]*255),int(cloth.colour[1]*255),int(cloth.colour[2]*255),int(cloth.colour[3]*255))
                        add coloured_image
                        #add ShaderDisplayable(shader.MODE_2D, cloth.position_sets.get("stand1").images["Average_AA"].filename, shader.VS_2D,PS_COLOUR_SUB_LR2,{},uniforms={"colour_levels":cloth.colour})
                        
screen girl_outfit_select_manager(the_wardrobe): ##Brings up a list of outfits currently in a girls wardrobe.
    add "Paper_Background.png"
    default preview_outfit = None
    vbox:
        for outfit in the_wardrobe.get_outfit_list():
            textbutton "Wear %s (Sluttiness %d)" % (outfit.name, outfit.slut_requirement) action Return(outfit) hovered SetScreenVariable("preview_outfit", copy.deepcopy(outfit)) unhovered SetScreenVariable("preview_outfit", None) style "textbutton_style" text_style "textbutton_text_style"
        
        textbutton "Return" action Return("None") style "textbutton_style" text_style "textbutton_text_style"
        
    fixed:
        pos (1500,0)
        add mannequin_average
        if preview_outfit:
            for cloth in sorted(preview_outfit.feet+preview_outfit.lower_body+preview_outfit.upper_body, key=lambda clothing: clothing.layer):
                if not cloth.is_extension:
                    if cloth.draws_breasts:
                        $ coloured_image = im.Recolor(cloth.position_sets.get("stand1").images["Average_D"].filename,int(cloth.colour[0]*255),int(cloth.colour[1]*255),int(cloth.colour[2]*255),int(cloth.colour[3]*255))
                        add coloured_image
                        #add ShaderDisplayable(shader.MODE_2D, cloth.position_sets.get("stand1").images["Average_D"].filename, shader.VS_2D,PS_COLOUR_SUB_LR2,{},uniforms={"colour_levels":cloth.colour})
                    else:
                        $ coloured_image = im.Recolor(cloth.position_sets.get("stand1").images["Average_AA"].filename,int(cloth.colour[0]*255),int(cloth.colour[1]*255),int(cloth.colour[2]*255),int(cloth.colour[3]*255))
                        add coloured_image
                        #add ShaderDisplayable(shader.MODE_2D, cloth.position_sets.get("stand1").images["Average_AA"].filename, shader.VS_2D,PS_COLOUR_SUB_LR2,{},uniforms={"colour_levels":cloth.colour})


screen map_manager():
    add "Paper_Background.png"
    for place in world: #Draw the background
        for connected in map(lambda c: World.locations[c]["map_pos"], place.connections):
            add Vren_Line(place.map_pos, connected, 4,"#117bff") #Draw a white line between each location 
    for place in world: #Draw the text buttons over the background
        if world.mc.location != place:
            frame:
                background None
                xysize [171,150] 
                anchor [0.0,0.0]
                align place.map_pos
                imagebutton:
                    anchor [0.5,0.5]
                    auto "gui/LR2_Hex_Button_%s.png"
                    focus_mask "gui/LR2_Hex_Button_idle.png"
                    action setVariable(world.mc.location, place)
                    sensitive True #TODO: replace once we want limited travel again with: place in world.mc.location.connections
                text "%s\n(%d)" % (place.name.title(), len(place.people)) anchor [0.5,0.5] style "map_text_style"

        else:
            frame:
                background None
                xysize [171,150]
                anchor [0.0,0.0]
                align place.map_pos
                imagebutton:

                    anchor [0.5,0.5]
                    idle "gui/LR2_Hex_Button_Alt_idle.png"
                    focus_mask "gui/LR2_Hex_Button_Alt_idle.png"
                    action setVariable(world.mc.location, place)
                    sensitive False
                text "%s\n(%d)" % (place.name.title(), len(place.people)) anchor [0.5,0.5] style "map_text_style"

    frame:
        background None
        anchor [0.5,0.5]
        align [0.5,0.88]
        xysize [500,125]
        imagebutton:
            align [0.5,0.5]
            auto "gui/button/choice_%s_background.png"
            focus_mask "gui/button/choice_idle_background.png"
            action Return(world.mc.location)
        textbutton "Return" align [0.5,0.5] text_style "return_button_style"

init -2 screen policy_selection_screen():
    add "Paper_Background.png"
    modal True
    $ tooltip = GetTooltip()
    vbox:
        xalign 0.1
        yalign 0.1
        for name, policy in sorted(policies.iteritems(), key=lambda(k, policy): policy["cost"]):
            if name in world.mc.business.active_policies:
                textbutton "%s - $%d" % (name, policy["cost"]):
                    tooltip policy["desc"]
                    action NullAction()
                    style "textbutton_style"
                    text_style "textbutton_text_style"
                    background "#59853f"
                    hover_background "#78b156"
                    sensitive True
            elif policy["req"].issubset(world.mc.business.active_policies) and world.mc.business.funds > policy["cost"]:
                textbutton "%s - $%d" % (name, policy["cost"]):
                    tooltip policy["desc"]
                    style "textbutton_style"
                    text_style "textbutton_text_style"
                    action AddToSet(world.mc.business.active_policies, name)
                    sensitive policy["req"].issubset(world.mc.business.active_policies) and world.mc.business.funds > policy["cost"]
            elif policy["req"].issubset(world.mc.business.active_policies):
                textbutton "%s - $%d" % (name, policy["cost"]):
                    tooltip policy["desc"]
                    style "textbutton_style"
                    text_style "textbutton_text_style"
                    background "#666666"
                    action NullAction()
                    sensitive True
            elif all(policies[p]["req"].issubset(world.mc.business.active_policies) for p in policy["req"]):
                textbutton "%s - $%d" % (name, policy["cost"]):
                    tooltip policy["desc"]
                    style "textbutton_style"
                    text_style "textbutton_text_style"
                    background "#222"
                    action NullAction()
                    sensitive True
                

    if tooltip:
        frame:
            background None
            anchor [1.0,0.0]
            align [0.9,0.1]
            xysize [500,500]
            text tooltip style "menu_text_style"
            
    frame:
        background None
        anchor [0.5,0.5]
        align [0.5,0.88]
        xysize [500,125]
        imagebutton:
            align [0.5,0.5]
            auto "gui/button/choice_%s_background.png"
            focus_mask "gui/button/choice_idle_background.png"
            action Return()
        textbutton "Return" align [0.5,0.5] text_style "return_button_style"
    
        
init -2 style return_button_style:
    text_align 0.5
    size 30
    italic True
    bold True
    color "#dddddd"
    outlines [(2,"#222222",0,0)]
        
init -2 style map_text_style:
    text_align 0.5
    size 14
    italic True
    bold True
    color "#dddddd"
    outlines [(2,"#222222",0,0)]
    
init -2 style map_frame_style:
    background "#094691"
    
init -2 style map_frame_blue_style:
    background "#5fa7ff"
    
init -2 style map_frame_grey_style:
    background "#222222"
    
transform float_up:
    xalign 0.92
    yalign 1.0
    alpha 1.0
    ease 1.0 yalign 0.4
    linear 2.0 alpha 0.0
    
style float_text:
    size 30
    italic True
    bold True
    outlines [(2,"#222222",0,0)] 
    
style float_text_pink is float_text:
    color "#FFB6C1"
    
style float_text_red is float_text:
    color "B22222"
    
style float_text_grey is float_text:
    color "696969"
    
style float_text_green is float_text:
    color "228B22"
    
style float_text_yellow is float_text:
    color "D2691E"
    
style float_text_blue is float_text:
    color "483D8B"
    
screen float_up_screen (text_array, style_array): #text_array is a list of the text to be displayed on each line, style_array is the list of corisponding styles to be used for that text.
    vbox at float_up:
        xanchor 0.5
        for index, update_text in enumerate(text_array):
            text update_text style style_array[index]
    timer 3.0 action Hide("float_up_screen") #Hide this screen after 3 seconds, so it can be called again by something else.

label start:
    scene bg paper_menu_background with fade
    if preferences.show_adult_content is False:
        "Lab Rats 2 contains adult content. If you are not over 18 or your contries equivalent age you should not view this content."
        menu:
            "I am over 18.":
                "Excellent, let's continue then."

            "I am not over 18.":
                $renpy.full_restart()

            "I am over 18 and never ask again!":
                $ preferences.show_adult_content = True

    "Vren" "v0.3 represents an early iteration of Lab Rats 2. Expect to run into limited content, unexplained features, and unbalanced game mechanics."
    if preferences.show_faq is True:
        "Vren" "Would you like to view the FAQ?"
        menu:
            "View the FAQ.":
                call faq_loop from _call_faq_loop

            "Get on with the game!":
                "You can access the FAQ from your bedroom at any time."

            "Get on with the game and don't ask again!":
                $ preferences.show_faq = False

    $ renpy.block_rollback() 
    call screen character_create_screen()
    $ renpy.block_rollback()
    $ return_arrays = _return #These are the stat, skill, and sex arrays returned from the character creator.
    call create_world() from _call_create_world
            
    "You have recently graduated from university, after completing your degree in chemical engineering. You've moved away from home, closer to the industrial district of the city to be close to any potential engineering jobs."
    "While the job search didn't turn up any paying positions, it did lead you to a bank posting for an old pharmaceutical lab. The bank must have needed money quick, because they were practically giving it away."
    "Without any time to consider the consequences you bought the lab. It came stocked with all of the standard equipment you would expect, and after a few world.days of cleaning you're ready to get to work."
    "A lab is nothing without it's product though, and you have just the thing in mind. You still remember the basics for the mind altering serum you produced in university."
    "With a little work in your new research and development lab you think you could recreate the formula completely, or even improve on it. Hiring some help would improve your research and production speeds."
    "You yawn and stretch as you greet the dawn early in the morning. Today feels like the start of a brand new chapter in your life!"
    ## For now, this ensures reloadin the game doesn't reset any of the variables.
    $ renpy.show
    show screen main_ui
    show screen business_ui
    $ renpy.show(world.mc.location.name,what=world.mc.location.background_image) #show the bedroom background as our starting point.
    call examine_room(world.mc.location) from _call_examine_room
    jump game_loop
    
label faq_loop:
    menu:
        "Gameplay Basics.":
            menu:
                "Making Serum.":
                    "Vren" "Making serum in your lab is the most important task for success in Lab Rats 2. You begin the game with a fully equipt lab."
                    "Vren" "The first step to make a serum is to design it in your lab. The most basic serum design can be made without any additions, but most will be made by adding serum traits."
                    "Vren" "Serum traits modify the effects of a serum. The effects can be simple - increasing duration or Suggestion increase - or it may be much more complicated."
                    "Vren" "Once you have decided on the traits you wish to include in your serum you will have to spend time in the lab researching it. Place it in the research queue and spend a few hours working in the lab."
                    "Vren" "More complicated serums will take more time to research. Once the serum is completely researched it can be produced by your production division. Move over their and slot it into the current production queue."
                    "Vren" "Before you can produce the serum you will need raw supplies. One unit of supply is needed for every production point the serum requires. You can order supply from your main office."
                    "Vren" "Once you have supplies you can spend time in your production lab. After some number of hours you will find a dose, or several, in your companies inventory!"
                    "Vren" "You can either take this serum for your own personal use, or you can head to the main office and mark it for sale. Once a serum is marked for sale you can spend time in your marketting division to find a buyer."
                    "Vren" "Your research and development lab can also spend time researching new traits for serum instead of producing new serum designs. You slot these into your research queue in the same way you do a new serum design."
                    
                "Hiring Staff.":
                    "Vren" "While you can do all the necessary tasks for your company yourself, that isn't how you're going to make it big. Hiring employees will let you spend you grow your business and pull in more and more money."
                    "Vren" "To hire someone, head over to your main office. From there you can request a trio of resumes to choose from, for a small cost. The stats of the three candidates will be chosen, and you can choose who to hire."
                    "Vren" "The three primary stats - Charisma, Intelligence, and Focus - are the most important traits for a character. Each affects the jobs in your company differently."
                    "Vren" "Charisma is the primary stat for marketing and human resources, as well as being a secondary stat for purchasing supplies."
                    "Vren" "Intelligence is the primary stat for research, as well as a secondary stat for human resources and production."
                    "Vren" "Focus is the primary stat for supply procurement and production, as well as a secondary stat for research."
                    "Vren" "Each character will also have an expected salary, to be paid each world.day. Higher stats will result in a more expensive employee, so consider hiring specialists rather than generalists."
                    "Vren" "Your staff will come into work each morning and perform their appropriate tasks, freeing up your time for other pursuits..."
                    
                "Corrupting People.":
                    "Vren" "You may be wondering what you can do with all this serum you produce. The main use of serum is to increase the Suggestability statistic of another character."
                    "Vren" "While a character has a Suggestability value of 0 nothing you do will have a long lasting effect on their personality. Once Suggestability is raised, their personality will change in response to your actions."
                    "Vren" "Interacting with a character may change their Obedience or Sluttiness. The most direct way to do that is to have sex with them. As a characters Sluttiness score increases the farther she will be willing to go with you."
                    "Vren" "When you finish having sex with a girl you will change her Sluttiness, modified by her current Suggestability. The higher her arousal, the larger the change in Sluttiness."
                    "Vren" "As Sluttiness increases a character will also be more willing to wear revealing clothing, or nothing at all. Design an outfit using the outfit manager in the top left, then interact with the character and ask them to wear it."
                                        
        "Development Questions.":
            menu:
                "Are the Lab Rats 1 Characters in the game?":
                    "Vren" "Not yet, but they will be added. As the options available to me in the character creator improve they will be added, and their personality will be written into the game."
                    "Vren" "Lab Rats 2 assumes an imperfect end to it's prequel, where the main character realises the potential of the serum but fails to take advantage of it over the summer."
                    "Vren" "There will also be the option to import a saved game from Lab Rats 1, letting you start off with familiar characters that have higher Sluttiness or Obedience stats."
                    
                "Will there be more character poses?":
                    "Vren" "Absolutely! The current standing poses proved that the rendering workflow for the game is valid, which means I will be able to introduce character poses for different sex positions."
                    "Vren" "Doggy style is currently the only sex position with a unique character pose associated with it, it gives a good taste of what will be possible in the future."
                    
                "Will there be animation?":
                    "Vren" "No, there will not be full animation in the game. There may be small sprite based animations added later, but this will require more experimentation by me before I can commit to it."
                    
                "Why are their holes in some pieces of clothing?":
                    "Vren" "Some character positions cause portions of the character model to poke out of their clothing when I am rendering them."
                    "Vren" "I will be adjusting my render settings and rerendering any clothing items that need it as we go forward."
                    
                "Why do all of the characters have the same face?":
                    "Vren" "All of the current character faces use the same base render, which means they all end up looking the same."
                    "Vren" "I have finished improvements to my rendering automation which will let me generate a different set of faces; expect to see more variation in future versions."
                    
                "Why do names repeat so often?":
                    "Vren" "Patrons have the ability to suggest new names for the name pool each month. This process has just started, so there are only a small collection of names in the game for now."
                 
        "Done.":
            return
    call faq_loop from _call_faq_loop_1
    return
    
label check_inventory_loop:
    call screen show_serum_inventory(world.mc.inventory)
    return
    
label check_business_inventory_loop:
    call screen show_serum_inventory(world.mc.business.inventory)
    return
    
label outfit_design_loop:
    if world.mc.designed_wardrobe.get_count() == 0:
        call create_outfit(None) from _call_create_outfit
    else:
        menu:
            "Create a new outfit.":
                call create_outfit(None) from _call_create_outfit_1

            "Load an old outfit.":
                call screen outfit_select_manager()
                if _return != "No Return":
                    call create_outfit(_return) from _call_create_outfit_2

            "Delete an old outfit.":
                call screen outfit_delete_manager(world.mc.designed_wardrobe)
    return
            
    
label create_outfit(the_outfit):
    if the_outfit is None:
        call screen outfit_creator(Outfit("New Outfit"))
    else:
        call screen outfit_creator(the_outfit)
    $ new_outfit = _return
    if new_outfit != "Not_New": ##Only try and save the outfit if there was actually a new outfit made
        $ new_outfit_name = renpy.input ("Please name this outfit.")
        while new_outfit_name is None:
            $ new_outfit_name = renpy.input ("Please name this outfit.")
        if world.mc.designed_wardrobe.has_outfit_with_name(new_outfit_name):
            "An outfit with this name already exists. Would you like to overwrite it?"
            menu:
                "Overwrite existing outfit.":
                    $ world.mc.designed_wardrobe.remove_outfit(world.mc.designed_wardrobe.get_outfit_with_name(new_outfit_name))
                    $ world.mc.save_design(new_outfit, new_outfit_name)
                    
                "Rename outfit.":
                    $ new_outfit_name = renpy.input ("Please input a new name.")
                    while world.mc.designed_wardrobe.has_outfit_with_name(new_outfit_name):
                        $ new_outfit_name = renpy.input ("That name already exists. Please input a new name.")
                    $ world.mc.save_design(new_outfit, new_outfit_name)
        else:
            $ world.mc.save_design(new_outfit, new_outfit_name)
    return
    
label game_loop: ##THIS IS THE IMPORTANT SECTION WHERE YOU DECIDE WHAT ACTIONS YOU TAKE
    #"Now, what would you like to do? You can talk to someone, go somewhere else, perform an action, or reexamine the room."
    python:
        tuple_list = [("Go somewhere else.", "Go somewhere else."), ("Examine the area.", "Examine the area.")]
        act_ct = world.mc.location.valid_actions()
        if act_ct < 5:
            for act in world.mc.location.actions:
                if act.check_requirement():
                    tuple_list.append((act.name,act))
        else:
            tuple_list.append(("Do something.", "Do something."))

        pers_ct = len(world.mc.location.people)
        if pers_ct < 5:
            for people in world.mc.location.people:
                tuple_list.append(("Talk to " + people.name + " " + people.last_name[0] + ".",people))
        else:
            tuple_list.append(("Talk to someone.", "Talk to someone."))

        choice = renpy.display_menu(tuple_list,True,"Choice")

    if isinstance(choice, basestring):
        if choice == "Go somewhere else.":
            call screen map_manager
            call change_location(_return) from _call_change_location #_return is the location returned from the map manager.

        elif choice == "Examine the area.":
            call examine_room(world.mc.location) from _call_examine_room_1

        elif choice == "Do something.":
            python:
                i = 0
                while not isinstance(choice, Action) and choice != "Back":
                    tuple_list = [(act.name,act) for act in world.mc.location.actions[i:i+9]]
                    if act_ct > i+10:
                        tuple_list.append(("Something else", "Something else"))
                        i += 9
                    elif act_ct == i+10:
                        act = world.mc.location.actions[i+9]
                        tuple_list.append((act.name,act))
                    tuple_list.append(("Back", "Back"))
                    choice = renpy.display_menu(tuple_list,True, "Choice")

        elif choice == "Talk to someone.":
            python:
                i = 0
                people = list(world.mc.location.people)
                while not isinstance(choice, NPC) and choice != "Back":
                    tuple_list = [(p.name + " " + p.last_name[0] + ".", p) for p in people[i:i+9]]
                    if pers_ct > i+10:
                        tuple_list.append(("Someone else", "Someone else"))
                        i += 9
                    elif pers_ct == i+10:
                        p = world.mc.location.people[i+9]
                        tuple_list.append((p.name + " " + p.last_name[0] + ".",p))
                    tuple_list.append(("Back", "Back"))
                    choice = renpy.display_menu(tuple_list,True, "Choice")

    if isinstance(choice, NPC):
        "You approach [choice.name] and chat for a little bit."
        $ choice.call_greeting()
        call talk_person(choice) from _call_talk_person

    elif isinstance(choice, Action):
        $ choice.call_action()

    jump game_loop
    

        
label change_location(the_place):
    $ renpy.scene()
    $ renpy.show(the_place.name,what=the_place.background_image)
#    "You spend some time travelling to %s." % the_place.name #TODO: Only show this when there is a significant time use? Otherwise takes up too much time changing between locations.
    return

label talk_person(the_person, repeat_choice = None):
    $the_person.draw_person()
    show screen person_info_ui(the_person)
    hide screen business_ui

    menu:
        "Finish talking.":
            $ repeat_choice = None
            "Eventually you're done say goodbye to each other."
        "Repeat" if repeat_choice:
            # print the repeat choice and then replace characters so it can be called as a label
            "You [repeat_choice]"
            $ renpy.call(re.sub(' ', '_', repeat_choice))

        "Chat about something.":
            $ repeat_choice = None
            $ is_employee = world.mc.business.is_employee(the_person)
            menu:
                "Compliment her outfit.":
                    $ repeat_choice = "compliment her outfit"
                    call compliment_her_outfit from chat_compliment_outfit
                "Flirt with her.":
                    $ repeat_choice = "flirt with her"
                    call flirt_with_her  from chat_flirt
                "Compliment her recent work." if is_employee:
                    $ repeat_choice = "compliment her recent work"
                    call compliment_her_recent_work  from chat_compliment_work
                "Insult her recent work." if is_employee:
                    $ repeat_choice = "insult her recent work"
                    call insult_her_recent_work  from chat_insult

                "Offer a cash bonus." if is_employee and 0 < world.time_of_day < 4:
                    world.mc.name "So [the_person.name], you've been putting in a lot of good work at the lab lately and I wanted to make sure you were rewarded properly for that."
                    "You pull out your wallet and start to pull out a few bills."
                    $weeks_wages = the_person.salary*5
                    $months_wages = the_person.salary*20
                    $raise_amount = int(the_person.salary*0.1)
                    menu:
                        "Give her a pat on the back.":
                            world.mc.name "And I'll absolutely reward you once the next major deal goes through."
                            $ the_person.draw_person(emotion = "sad")
                            $ change_amount = 5-world.mc.charisma
                            show screen float_up_screen(["-%d Happiness" % change_amount],["float_text_yellow"])
                            $the_person.change_happiness(-change_amount)
                            "[the_person.name] looks visibly disapointed."
                            the_person.name "Right, of course."

                        "Give her a world.days wages. -$[the_person.salary]" if world.mc.money >= the_person.salary:
                            world.mc.name "Here you go, treat yourself to something nice tonight."
                            $ the_person.draw_person(emotion = "happy")
                            $ change_amount = 1+world.mc.charisma
                            show screen float_up_screen(["+%d Happiness" % change_amount],["float_text_yellow"])
                            $ the_person.change_happiness(change_amount)
                            $ world.mc.money -= the_person.salary
                            "[the_person.name] takes the bills from you and smiles."
                            the_person.name "Thank you sir."

                        "Give her a weeks wages. -$[weeks_wages]" if world.mc.money >= weeks_wages:
                            world.mc.name "Here you go, don't spend it all in once place."
                            $ the_person.draw_person(emotion = "happy")
                            $ change_amount = 1+world.mc.charisma
                            $ change_amount_happiness = 5+world.mc.charisma
                            $ the_person.change_happiness(change_amount_happiness)
                            $ the_person.change_obedience_modified(change_amount)
                            $ world.mc.money -= weeks_wages
                            show screen float_up_screen(["+%d Happiness" % change_amount,"+%d Obedience" % change_amount],["float_text_yellow","float_text_grey"])
                            "[the_person.name] takes the bills, then smiles broadly at you."
                            the_person.name "That's very generous of you sir, thank you."

                        "Give her a months wages. -$[months_wages]" if world.mc.money >= months_wages:
                            world.mc.name "Here, you're a key part of the team and you deserved to be rewarded as such."
                            $ the_person.draw_person(emotion = "happy")
                            $ change_amount = 5+world.mc.charisma
                            $ change_amount_happiness = 10+world.mc.charisma
                            $ world.mc.money -= months_wages
                            $the_person.change_happiness(change_amount_happiness)
                            $the_person.change_obedience_modified(change_amount)
                            "[the_person.name] takes the bills, momentarily stunned by the amount."
                            show screen float_up_screen(["+%d Happiness" % change_amount,"+%d Obedience" % change_amount],["float_text_yellow","float_text_grey"])
                            if the_person.sluttiness > 40 and the_person.happiness > 100:
                                the_person.name "Wow... this is amazing sir. I'm sure there's something I can do to pay you back, right?"
                                "She steps close to you and runs a finger down your chest."
                                call fuck_person(the_person) from _call_fuck_person_3  #TODO: add a temporary obedience and sluttiness modifier to the function to allow for modifiers during situations like this (and firing her)
                                #Now that you've had sex, we calculate the change to her stats and move on.
                                $ change_amount = the_person.change_slut_modified(the_person.arousal) #Change her slut score by her final arousal. This should be _about_ 100 if she climaxed, but you may keep fucking her silly if you can overcome the arousal loss.
                                show screen float_up_screen(["+%d Sluttiness" % change_amount],["float_text_pink"])
                                $ the_person.reset_arousal()
                                $ the_person.review_outfit()
                            else:
                                the_person.name "Wow... this is amazing sir. I'll do everything I can for you and the company!"

                        "Give her a permanent 10%% Raise ($[raise_amount]/world.day)":
                            world.mc.name "[the_person.name], it's criminal that I pay you as little as I do. I'm going to mark you down for a 10%% raise, effective by the end of today."
                            $ change_amount = 5+world.mc.charisma
                            $ change_amount_happiness = 10+world.mc.charisma
                            $ the_person.change_happiness(change_amount_happiness)
                            $ change_amount_obedience = the_person.change_obedience_modified(change_amount)
                            show screen float_up_screen(["+$%d/world.day Salary" % raise_amount,"+%d Happiness" % change_amount,"+%d Obedience" % change_amount_obedience],["float_text_green","float_text_yellow","float_text_grey"])
                            $ the_person.salary += raise_amount
                            the_person.name "Thank you sir, that's very generous of you!"

                    call talk_person(the_person) from _call_talk_person_4

        "Modify her wardrobe." if the_person.obedience >= 120:
            $ repeat_choice = None
            menu:
                "Add an outfit.":
                    world.mc.name "[the_person.name], I've got something I'd like you to wear for me." ## Do we want a completely silent protag? Speaks only through menu input maybe?
                    hide screen main_ui
                    $ renpy.scene("Active")
                    call screen outfit_select_manager()
                    show screen main_ui
                    $ the_person.draw_person()
                    if _return != "No Return":
                        $ new_outfit = _return
                        if new_outfit.slut_requirement > the_person.sluttiness:
                            $ the_person.call_clothing_reject()
                        else:
                            $ the_person.add_outfit(new_outfit)
                            $ the_person.call_clothing_accept()
                            the_person.name "Would you like me to wear it now?" ##TODO: Only have them ask this question if their devotion is a certain level
                            menu:
                                "Yes, wear it now.":
                                    $ the_person.set_outfit(new_outfit)
                                    $ renpy.scene("Active") ## Clear the persons image
                                    $ the_person.draw_person() ## And redraw it now that they're in a new outfit
                                "No, save it for some other time.":
                                    pass
                    else:
                        world.mc.name "On second thought, nevermind."
                        
                "Delete an outfit.":
                    world.mc.name "[the_person.name], lets have a talk about what you've been wearing."
                    hide screen main_ui
                    $ renpy.scene("Active")
                    call screen outfit_delete_manager(the_person.wardrobe)
                    show screen main_ui
                    $ the_person.draw_person()
                    #TODO: Figure out what happens when someone doesn't have anything in their wardrobe.
                
                "Wear an outfit right now.":
                    world.mc.name "[the_person.name], I want you to get changed for me."
                    hide screen main_ui
                    $ renpy.scene("Active")
                    call screen girl_outfit_select_manager(the_person.wardrobe)
                    if _return != "None":
                        $ the_person.set_outfit(_return)
                    
                    $ the_person.draw_person()
                    show screen main_ui
                    the_person.name "Is this better?"
            call talk_person(the_person) from _call_talk_person_1
            
        "Move her to a new division." if world.mc.business.get_employee_title(the_person) != "None" and 0 < world.time_of_day < 4:
            $ repeat_choice = None
            the_person.name "Where would you like me then?"
            $ selected_div = renpy.display_menu([(div.name, div) for div in world.mc.business.division], True, "Choice")
            if the_person.job not in selected_div.jobs:
                $ world.mc.business.remove_employee(the_person)
                $ world.mc.business.add_employee(the_person, selected_div)
                the_person.name "I'll get started right away!"
            else:
                $ the_person.change_happiness(-1) # for desinterest
                show screen float_up_screen(["-1 Happiness"],["float_text_yellow"])
                the_person.name "Actually I am already working there."

        "Fire them!" if world.mc.business.get_employee_title(the_person) != "None" and 0 < world.time_of_day < 4:
            $ repeat_choice = None
            "You tell [the_person.name] to collect their things and leave the building."
            $ world.mc.business.remove_employee(the_person) #TODO: check if we should actually be physically removing the person from the location without putting them somewhere else (person leak?)

        "Take a closer look at [the_person.name].":
            $ repeat_choice = None
            call examine_person(the_person) from _call_examine_person
            call talk_person(the_person) from _call_talk_person_2
        "Give her a dose of serum." if world.mc.inventory.get_any_serum_count() > 0 and "Mandatory Serum Testing" in world.mc.business.active_policies:
            $ repeat_choice = "give her a dose of serum"
            call give_her_a_dose_of_serum
        "Seduce her.":
            $ repeat_choice = None
            call seduce_her from chat_seduce
    if repeat_choice:
        call talk_person(the_person, repeat_choice) from _call_talk_person_3
    hide screen person_info_ui
    show screen business_ui
    $renpy.scene("Active")
    return

label compliment_her_outfit:
    world.mc.name "Hey [the_person.name], I just wanted to say that you look great today. That style really suits you." #TODO: Add more context aware dialogue.
    $ slut_difference = int(the_person.sluttiness - the_person.outfit.slut_requirement) #Negative if their outfit is sluttier than what they would normally wear.
    # Note: The largest effect should occure when the outfit is just barely in line with her sluttiness. Too high or too low and it will have no effect.

    $ sweet_spot_range = 10
    if slut_difference < -sweet_spot_range : #Outfit is too slutty, she will never get use to wearing it.
        $ the_person.draw_person(emotion = "default")
        the_person.name "Really? It's just so revealing, what do people think of me when they see me? I don't think I'll ever get use to wearing this."

    elif slut_difference > sweet_spot_range:  #Outfit is conservative, no increase.
        $ the_person.draw_person(emotion = "default")
        the_person.name "Really? I think it looks too bland, showing a little more skin would be nice."

    else: #We are within the sweet_spot_range with the outfit.
        $ slut_difference = math.fabs(slut_difference)
        if slut_difference > sweet_spot_range:
            $ slut_difference = sweet_spot_range
        $ slut_difference = sweet_spot_range - slut_difference #invert the value so we now have 10 - 10 at both extreme ends, 10 - 0 at the middle where it will have the most effect.
        $ change_amount = the_person.change_slut_modified(world.mc.charisma + 1 + slut_difference) #Increase their sluttiness if they are suggestable right now.
        show screen float_up_screen(["+%d Sluttiness" % change_amount],["float_text_pink"])
        the_person.name "Glad you think so, I was on the fence, but it's nice to know that somebody likes it!"
    return

label flirt_with_her:
    world.mc.name "Hey [the_person.name], you're looking particularly good today. I wish I got to see a little bit more of that fabulous body."
    $ change_amount = the_person.change_slut_modified(world.mc.charisma + 1)
    show screen float_up_screen(["+%d Sluttiness" % change_amount],["float_text_pink"])
    $the_person.call_flirt_response()
    return

label compliment_her_recent_work:
    world.mc.name "[the_person.name], I wanted to tell you that you've been doing a great job lately. Keep it up, you're one of hte most important players in this whole operation."
    $ change_amount = world.mc.charisma + 1
    $ change_amount_obedience = the_person.change_obedience_modified(-change_amount)
    $ the_person.change_happiness(change_amount)
    $ the_person.draw_person(emotion = "happy")
    show screen float_up_screen(["+%d Happiness" % change_amount,"%d Obedience" % change_amount_obedience],["float_text_yellow","float_text_grey"])
    the_person.name "Thanks [world.mc.name], it means a lot to hear that from you. I'll just keep doing what I'm doing I guess."
    return

label insult_her_recent_work:
    world.mc.name "[the_person.name], I have to say I've been disappointed in your work for a little while now. Try to shape up, or we'll have to have a more offical talk about it."
    $ change_amount = world.mc.charisma*2 + 1
    $ change_amount_happiness = 5-world.mc.charisma
    $ change_amount= the_person.change_obedience_modified(change_amount)
    $ the_person.change_happiness(-change_amount_happiness)
    $ the_person.draw_person(emotion = "sad")
    show screen float_up_screen(["-%d Happiness" % change_amount_happiness,"+%d Obedience" % change_amount],["float_text_yellow","float_text_grey"])
    the_person.name "Oh... I didn't know there was an issue. I'll try follow your instructions closer then."
    return

label give_her_a_dose_of_serum:
    $renpy.scene("Active")
    call give_serum(the_person) from _call_give_serum
    return

label seduce_her:
    "You step close to [the_person.name] and hold her hand."
    $ the_person.call_seduction_response()
    call fuck_person(the_person) from _call_fuck_person
    #Now that you've had sex, we calculate the change to her stats and move on.
    $ change_amount = the_person.change_slut_modified(the_person.arousal) #Change her slut score by her final arousal. This should be _about_ 100 if she climaxed, but you may keep fucking her silly if you can overcome the arousal loss.
    show screen float_up_screen(["+%d Sluttiness" % change_amount],["float_text_pink"])
    $ the_person.reset_arousal()
    $ the_person.review_outfit()
    return

label fuck_person(the_person): #TODO: Add a conditional obedience and sluttiness increase for situations like blackmail or getting drunk
    python:
        available_positions = world.mc.get_available_positions(list_of_positions, the_person)

        alt_options = [("Strip her down.","Strip"), ("Leave","Leave")]

        position_choice = "Try again"
        round = 0

    while position_choice != "Leave":
        python:
            # ask what position you want
            position_choice = renpy.display_menu(available_positions + alt_options, True, "Choice")
            # position_choice needs to be modifyable by reference in call_for_consent() below.
            by_ref = [position_choice]
            if isinstance(position_choice, Position):
                the_person.draw_person(position_choice.position_tag)
                if round == 0 or position_choice != the_position: #We are changing to a new position.
                    sites = [("do it on the " + obj, obj) for obj in world.mc.location.objects_with_trait(position_choice.requires_location)]
                    if len(sites) > 1:
                       renpy.say("", "Where do you do it?")

                    the_object = renpy.display_menu(sites, True, "Choice")
                    the_person.call_for_consent(by_ref) # in list so it's can be modified (by reference)
        $ position_choice = by_ref[0]

        # keep going as long as it is a position
        while isinstance(position_choice, Position):

            $ the_position = position_choice
            $ the_position.call_transition(the_position, the_person, world.mc.location, the_object, round)
            $ the_position.call_scene(the_person, world.mc.location, the_object, round)
            $ the_person.call_for_arouse(mc, the_position)

            python:
                ##Ask how you want to keep fucking her##
                if (world.mc.arousal >= 100):
                    "You're past your limit, you have no choice but to cum!"
                    position_choice = "Finish"
                else:
                    tuple_list = [("Keep going some more.",the_position), ("Back off and change positions.","Pull Out")]
                    if (world.mc.arousal > 80): #Only let you finish if you've got a high enough arousal score. #TODO: Add stat that controls how much control you have over this.
                        tuple_list.append(("Cum!","Finish"))
                    for pos_name in the_position.connections:
                        position = getattr(world, pos_name)
                        if position.requires_location in the_object and position.check_clothing(the_person):
                            tuple_list.append(("Change to " + position.name + ".", position))
                    position_choice = renpy.display_menu(tuple_list + alt_options, True,"Choice")
                    round += 1
        if position_choice == "Finish":
            python:
                world.mc.reset_arousal()
                position_choice = "Leave"
                the_position.call_outro(the_person, world.mc.location, the_object, round)
                # TODO: have you finishing bump her arousal up so you might both cum at once.

        elif position_choice == "Strip":
            call strip_menu(the_person) from _call_strip_menu
            python:
                if the_person.outfit.is_nude():
                    alt_options = [("Leave","Leave")]
                available_positions = world.mc.get_available_positions(list_of_positions, the_person)
    return

label strip_menu(the_person):
    python:
        strip_options = [("Take off " + cloth.name + ".",cloth) for cloth in the_person.outfit.get_unanchored() if not cloth.is_extension]
        cloth = renpy.display_menu(strip_options + [("Go back to fucking her.","Finish")], True, "Choice")
        while cloth != "Finish":

            test_outfit = copy.deepcopy(the_person.outfit)
            test_outfit.remove_clothing(cloth)
            if the_person.judge_outfit(test_outfit):
                the_person.outfit.remove_clothing(cloth)
                the_person.draw_person()
                renpy.say("", "You pull her " + cloth.name + " off, dropping it to the ground.")
                strip_options = [("Take off " + cloth.name + ".",cloth) for cloth in the_person.outfit.get_unanchored() if not cloth.is_extension]
            else:
                renpy.say("", "You start to pull off " + the_person.name + "'s " + cloth.name + " when she grabs your hand and stops you.")
                the_person.call_strip_reject()

            cloth = renpy.display_menu(strip_options + [("Go back to fucking her.","Finish")], True, "Choice")
    return

    
label examine_room(the_room):
    python:
        desc = "You are at the %s. " % the_room.name

        people_here = the_room.people #Format the names of people in the room with you so it looks nice.
        pers_ct = len(people_here)
        if pers_ct == 1:
            desc += people_here[0].name + " is here. "
        elif pers_ct > 0:
            if pers_ct < 6:
                desc = "You see "
                if pers_ct > 2:
                    for person in people_here[0:pers_ct-3]:
                        desc += person.name
                        desc += ", "
                desc += people_here[pers_ct-2].name + "and " + people_here[pers_ct-1].name + " here. "
            else:
                desc += "It is filled with people here. "

        connections_here = the_room.connections # Now we format the output for the connections so that it is readable.
        conn_ct = len(connections_here)
        if conn_ct == 0:
            desc += "There are no exits from here. You're trapped! " #Shouldn't ever happen, hopefully."
        else:
            connections_here = [getattr(world, n) for n in connections_here]
            desc += "From here you can head to "
            if conn_ct == 2:
                desc += "either the " + connections_here[0].name + " or "
            elif conn_ct > 2:
                for place in connections_here[0:conn_ct-2]:
                    desc += "the " + place.name + ", the "
                desc += connections_here[conn_ct-2].name + " or "
            desc += "the " + connections_here[conn_ct-1].name +". "
        #desc += "That's all there is to see nearby." # don't state the obvious
        renpy.say("",desc) ##This is the actual print statement!!
    return
    
label examine_person(the_person):
    #Take a close look and figure out their physical attributes (tit size, ass size?, hair colour, hair style)
    
    python:
        string = "She has " + the_person.skin + " coloured skin, along with " + the_person.hair_colour + " coloured hair and pretty " + the_person.eyes + " coloured eyes. She stands " + height_to_string(the_person.height) + " tall."
        renpy.say("",string)
        
        outfit_top = the_person.outfit.get_upper_visible()
        outfit_bottom = the_person.outfit.get_lower_visible()
        string = ""
        
        if len(outfit_top) == 0: ##ie. is naked
            string += "She's wearing nothing at all on top, with her nice " + the_person.tits + " sized tits on display for you."
        elif len(outfit_top) == 1:
            string += "She's wearing a " + outfit_top[0].name + " with her nice " + the_person.tits + " sized tits underneath."
        elif len(outfit_top) == 2:
            string += "She's wearing a " + outfit_top[1].name + " with a " + outfit_top[0].name + " underneath. Her tits look like they're " + the_person.tits + "'s."
        elif len(outfit_top) == 3:
            string += "She's wearing a " + outfit_top[2].name + " with a " + outfit_top[1].name + " and " + outfit_top[0].name + " underneath. Her tits look like they're " + the_person.tits + "'s."
        renpy.say("",string)
        
        string = ""
        if len(outfit_bottom) == 0: #naked
            string += "Her legs are completely bare, and you have a clear view of her pussy."
        elif len(outfit_bottom) == 1:
            string += "She's also wearing " + outfit_bottom[0].name + " below."
            if not outfit_bottom[0].hide_below:
                string += " You can see her pussy underneath."
        elif len(outfit_bottom) == 2:
            string += "She's also wearing " + outfit_bottom[0].name + " below, with " + outfit_bottom[1].name +  " visible below."
            if not outfit_bottom[1].hide_below:
                string += " You can see her pussy underneath."
        renpy.say("",string)
        for div in world.mc.business.division:
            if the_person in div.people:
                renpy.say("", "%s currently works in your %s department." % (the_person.name, div.name.lower()) )
                break
        else:
            renpy.say("", the_person.name + " does not currently work for you.")
    
    return
    
label give_serum(the_person):
    call screen serum_inventory_select_ui(world.mc.inventory)
    if _return != "None":
        $ the_serum = _return
        "You decide to give [the_person.name] a dose of [the_serum.name]."
        $ world.mc.inventory.change_serum(the_serum,-1)
        $ the_person.give_serum(copy.copy(the_serum)) #use a copy rather than the main class, so we can modify and delete the effects without changing anything else.
    else:
        "You decide not to give [the_person.name] anything right now."
    return
label advance_time:
    # 1) Turns are processed _before_ the time is advanced.
    # 1a) crises are processed if they are triggered.
    # 2) Time is advanced, world.day is advanced if required.
    # 3) People go to their next intended location.
    # Note: This will require breaking people's turns into movement and actions.
    # Then: Add research crisis when serum is finished, requiring additional input from the player and giving the chance to test a serum on the R&D staff.

    python: 
        people_to_process = [] #This is a master list of turns of need to process, stored as tuples [character,location]. Used to avoid modifying a list while we iterate over it, and to avoid repeat movements.
        for place in world:
            for people in place.people:
                people_to_process.append([people,place])
                
    python:
        for (people,place) in people_to_process: #Run the results of people spending their turn in their current location.
            people.run_turn()
        world.mc.business.run_turn()
        
    $ count = 0
    $ maximum = len(world.mc.business.mandatory_crises_list)
    $ clear_list = []
    while count < maximum: #We need to keep this in a renpy loop, because a return call will always return to the end of an entire python block.
        $crisis = world.mc.business.mandatory_crises_list[count]
        if crisis.check_requirement():
            $ crisis.call_action()
            $ renpy.scene("Active")
            $ renpy.show(world.mc.location.name,what=world.mc.location.background_image) #Make sure we're showing the correct background for our location, which might have been temporarily changed by a crisis.
            $ clear_list.append(crisis)
        $ count += 1
            
    
    python: #Needs to be a different python block, otherwise the rest of the block is not called when the action returns.
        for crisis in clear_list:
            world.mc.business.mandatory_crises_list.remove(crisis) #Clean up the list.
    
    if renpy.random.randint(0,100) < 10: #ie. run a crisis 25% of the time. TODO: modify this.
        python:
            possible_crisis_list = []
            for crisis in crisis_list:
                if crisis[0].check_requirement(): #Get the first element of the weighted tuple, the action.
                    possible_crisis_list.append(crisis) #Build a list of valid crises from ones that pass their requirement.
                    
        $ the_crisis = renpy.random.choice([it for k, v in possible_crisis_list for it in [k] * v])
        if the_crisis:
            $ the_crisis.call_action()
    
    $ renpy.scene("Active")
    $ renpy.show(world.mc.location.name,what=world.mc.location.background_image) #Make sure we're showing the correct background for our location, which might have been temporarily changed by a crisis.
    hide screen person_info_ui
    show screen business_ui
    
    if world.time_of_day == 4: ##First, determine /if we're going into the next chunk of time. If we are, advance the world.day and run all of the end of world.day code.
        $ world.time_of_day = 0
        $ world.day += 1
        python:
            for (people,place) in people_to_process:
                people.run_day()
        $ world.mc.business.run_day()
        
        if world.mc.business.funds < 0:
            $ world.mc.business.bankrupt_days += 1
            if world.mc.business.bankrupt_days == world.mc.business.max_bankrupt_days:
                $ renpy.say("","With no funds to pay your creditors you are forced to close your business and auction off all of your materials at a fraction of their value. Your story ends here.")
                $ renpy.full_restart()
            else:
                $ world.days_remaining = world.mc.business.max_bankrupt_days-world.mc.business.bankrupt_days
                $ renpy.say("","Warning! Your company is losing money and unable to pay salaries or purchase necessary supplies! You have %d world.days to restore yourself to positive funds or you will be foreclosed upon!" % world.days_remaining)
        else:
            $ world.mc.business.bankrupt_days = 0
            
        call screen end_of_day_update() # We have to keep this outside of a python block, because the renpy.call_screen function does not properly fade out the text bar.
        $ world.mc.business.clear_messages()

    else:
        $ world.time_of_day += 1 ##Otherwise, just run the end of world.day code.
        
    if world.time_of_day == 1 and "Daily Serum Dosage" in world.mc.business.active_policies: #It is the start of the work world.day, give everyone their daily dose of serum
        $ world.mc.business.give_daily_serum()
        
    python:    
        for (people,place) in people_to_process: #Now move everyone to where the should be in the next time chunk. That may be home, work, etc.
            people.run_move(place)
        
    return

