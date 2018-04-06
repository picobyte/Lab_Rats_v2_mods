init -22 python:
    class Hair_Style(renpy.store.object):
        def __init__(self, name, filename):
            self.name = name
            self.filename = filename
            self.black = {"stand1":Image(filename+"_black_stand1.png"),"stand2":Image(filename+"_black_stand2.png"),"stand3":Image(filename+"_black_stand3.png"),"doggy":Image(filename+"_black_doggy.png")}
            self.brown = {"stand1":Image(filename+"_brown_stand1.png"),"stand2":Image(filename+"_brown_stand2.png"),"stand3":Image(filename+"_brown_stand3.png"),"doggy":Image(filename+"_brown_doggy.png")}
            self.blond = {"stand1":Image(filename+"_blond_stand1.png"),"stand2":Image(filename+"_blond_stand2.png"),"stand3":Image(filename+"_blond_stand3.png"),"doggy":Image(filename+"_blond_doggy.png")}
            self.red = {"stand1":Image(filename+"_red_stand1.png"),"stand2":Image(filename+"_red_stand2.png"),"stand3":Image(filename+"_red_stand3.png"),"doggy":Image(filename+"_red_doggy.png")}

        def draw_item(self,colour,height,position = "stand1"): #colour = black,brown,blond, or red right now
            if colour == "black":
                image_set = self.black.get(position) #Backup in case a position is missing a correct image set tag.
                if image_set == None:
                    image_set = self.black["stand1"] #Default case is stand 1. TODO: put the default in a global location that everything refers to.
            elif colour == "brown":
                image_set = self.brown.get(position)
                if image_set == None:
                    image_set = self.brown.get["stand1"]
            elif colour == "blond":
                image_set = self.blond.get(position)
                if image_set == None:
                    image_set = self.blond["stand1"]
            else: #colour == "red"
                image_set = self.red.get(position)
                if image_set == None:
                    image_set = self.red["stand1"]

            shader_image = im.Recolor(image_set.filename,255,255,255,255)
            #shader_image = ShaderDisplayable(shader.MODE_2D, image_set.filename, shader.VS_2D,PS_COLOUR_SUB_LR2,{},uniforms={"colour_levels":[1,1,1,1]}) #TODO: This should take a colour parameter and colour the hair in game.
            renpy.show(self.name,at_list=[right,scale_person(height)],layer="Active",what=shader_image,tag=self.name)
