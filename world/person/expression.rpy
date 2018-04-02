init -18 python:
    class Expression(renpy.store.object):
        def __init__(self,name,skin_colour,facial_style):
            self.name = name
            self.skin_colour = skin_colour
            self.facial_style = facial_style #The style of face the person has, currently creatively named "Face_1", "Face_2", and "Face_3".
            self.emotion_set = ["default","happy","sad","angry","orgasm"]
            self.positions_set = ["stand1","stand2","stand3"] #The set of images we are going to draw emotions for. These are positions that look towards the camera
            self.ignore_position_set = ["doggy"] #The set of positions that we are not goign to draw emotions for. These look away from the camera TODO: This should reference the Position class somehow.
            self.position_dict = {}
            for position in self.positions_set+self.ignore_position_set:
                self.position_dict[position] = {}

            for position in self.positions_set:
                for emotion in self.emotion_set:
                    self.position_dict[position][emotion] = Image(emotion + "_" + facial_style + "_" + skin_colour + "_" + position + ".png")

            for position in self.ignore_position_set:
                for emotion in self.emotion_set:
                    self.position_dict[position][emotion] = Image("empty_holder.png") ##An empty image to be drawn when we don't want to draw any emotion, because the character's face is turned away.

        def draw_emotion(self,position,emotion,height):
            if not position in self.positions_set+self.ignore_position_set:
                position = "stand1"
            if not emotion in self.emotion_set:
                emotion = "default"
            renpy.show(self.name+position+emotion+self.facial_style,at_list=[right,scale_person(height)],layer="Active",what=self.position_dict[position][emotion],tag=self.name+position+emotion)


    class Object(renpy.store.object): #Contains a list of traits for the object which decides how it can be used.
        def __init__(self,name,traits):
            self.traits = traits
            self.name = name

        def has_trait(self,the_trait):
            for trait in self.traits:
                if trait == the_trait:
                    return True
            return False
