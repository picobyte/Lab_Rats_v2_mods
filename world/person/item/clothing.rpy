init -24 python:
    class Clothing(renpy.store.object):
        #Slots are

        ##Feet##
        #Layer 1: Socks
        #Layer 2: Shoes

        ##Lower Body##
        #Layer 1: Panties
        #Layer 2: Pantyhose
        #Layer 3: Pants/Skirt

        ##Upper Body##
        #Layer 1: Bra
        #Layer 2: Shirt
        #Layer 3: Jacket

        ##Accessories##
        #TODO

        def __init__(self, name, layer, hide_below, anchor_below, proper_name, position_sets, draws_breasts, underwear, slut_value, has_extension = None, is_extension = False, colour = None):
            self.name = name
            self.hide_below = hide_below #If true, it hides the clothing beneath so you can't tell what's on.
            self.anchor_below = anchor_below #If true, you must take this off before you can take off anything of a lower layer.
            self.layer = layer #A list of the slots above that this should take up or otherwise prevent from being filled. Slots are a list of the slot and the layer.
            self.position_sets = {set: Clothing_Images(proper_name,set,draws_breasts) for set in position_sets} #A list of position set names. When the clothing is created it will make a dict containing these names and image sets for them.
            self.draws_breasts = draws_breasts
            self.underwear = underwear #True if the item of clothing satisfies the desire for underwear for upper or lower (bra or panties), false if it can pass as outerwear. Underwear on outside of outfit gives higher slut requirement.
            self.slut_value = slut_value #The amount of sluttiness that this piece of clothing adds to an outfit.
            self.has_extension = has_extension #If the item of clothing spans two zones (say, lower and feet or upper and lower body) has_extension points towards the placeholder item that fills the other part.
            self.is_extension = is_extension #If this is true the clothing item exists only as a placeholder. It will draw nothing and not be removed unless the main piece is removed.
            self.colour = colour or [1,1,1,1]

        def __cmp__(self,other):
            if type(self) is type(other):
                if self.name == other.name and self.hide_below == other.hide_below and self.layer == other.layer:
                    return 0

            return -1 if self.__hash__() < other.__hash__() else 1

        def __hash__(self):
            return hash((self.name,self.hide_below,self.anchor_below,self.layer,self.draws_breasts,self.underwear,self.slut_value))

        def get_layer(self,body_type,tit_size):
            return self.layer

        def draw_item(self,body_type,height,tit_size,position):
            if not self.is_extension: #We don't draw extension items, because the image is taken care of in the main object.
                #The character you are currently interacting with is listed under the "Active" layer, so you can clear them without clearing the rest of the scene and having to redraw it.
                body_name = "" + self.name + " body" #Used so the different sprites will be placed on different levels instead of overwritting iteslf repeatedly.
                tit_name = "" + self.name + " tit"

                # If no image set is found with that name in the dict, use the default standing one instead. Standing should always exist.
                image_set = self.position_sets.get(position,  self.position_sets["stand1"])

                the_image = image_set.images[body_type+"_"+(tit_size if self.draws_breasts else "AA")] #We get the image set with mutliple breast sizes or none if not needed

                shader_image = im.Recolor(the_image.filename,int(self.colour[0]*255),int(self.colour[1]*255),int(self.colour[2]*255),int(self.colour[3]*255))
                # shader_image = ShaderDisplayable(shader.MODE_2D, the_image.filename, shader.VS_2D,PS_COLOUR_SUB_LR2,{},uniforms={"colour_levels":self.colour})
                renpy.show(body_name + tit_name,at_list=[right,scale_person(height)],layer="Active",what=shader_image,tag=body_name+tit_name)

    class Clothing_Images(renpy.store.object): # Stores a set of images for a single piece of cloting in a single position. The position is stored when it is put into the clothing object dict.
        def __init__(self,clothing_name,position_name,is_top):

            self.images = {}
            self.body_types = ["Average","Thin","Fat"]
            self.breast_sizes = ["AA","A","B","C","D","DD","DDD","E","F","FF"] if is_top else ["AA"]

            for body in self.body_types:
                for breast in self.breast_sizes:
                    self.images[body+"_"+breast] = Image(clothing_name+"_"+position_name+"_"+body+"_"+breast+".png")

    class Outfit(renpy.store.object): #A bunch of clothing added together, without slot conflicts.
        def __init__(self,name):
            self.name = name
            self.upper_body = []
            self.lower_body = []
            self.feet = []
            self.accessories = [] #Extra stuff that doesn't fit anywhere else. Hats, glasses, ect.
            self.slut_requirement = 0 #The slut score requirement for this outfit.
            self.update_slut_requirement()

        def draw_outfit(self, body_type, height, tit_size,position):
            #Sort each catagory by layer, then send a draw request to the clothing. This will build up the person piece by piece.
            #Draw back to front, so that layer 0 (underwear) always shows up under jackets, shirts, etc.

            for cloth in sorted(self.feet+self.lower_body+self.upper_body, key=lambda clothing: clothing.layer):
                cloth.draw_item(body_type, height, tit_size, position)

        def can_add_dress(self, new_clothing):
            return self.can_add_upper(new_clothing) and self.can_add_lower(new_clothing.has_extension)

        def add_dress(self, new_clothing):
            if self.can_add_dress(new_clothing):
                self.upper_body.append(new_clothing)
                self.lower_body.append(new_clothing.has_extension)
                self.update_slut_requirement()

        def can_add_upper(self, new_clothing):
            return not any(cloth.layer == new_clothing.layer for cloth in self.upper_body)

        def add_upper(self, new_clothing):
            if self.can_add_upper(new_clothing): ##Always check to make sure the clothing is valid before you add it.
                self.upper_body.append(new_clothing)
                self.update_slut_requirement()

        def can_add_lower(self,new_clothing):
            return not any(cloth.layer == new_clothing.layer for cloth in self.lower_body)

        def add_lower(self, new_clothing):
            if self.can_add_lower(new_clothing):
                self.lower_body.append(new_clothing)
                self.update_slut_requirement()

        def can_add_feet(self, new_clothing):
            return not any(cloth.layer == new_clothing.layer for cloth in self.feet)

        def add_feet(self, new_clothing):
            if self.can_add_feet(new_clothing):
                self.feet.append(new_clothing)
                self.update_slut_requirement()

        def remove_clothing(self, old_clothing):
            if old_clothing.has_extension:
                self.remove_clothing(old_clothing.has_extension)

            if old_clothing in self.upper_body: #Can't use elif because there might be multi-slot items
                self.upper_body.remove(old_clothing)
            elif old_clothing in self.lower_body:
                self.lower_body.remove(old_clothing)
            elif old_clothing in self.feet:
                self.feet.remove(old_clothing)
            elif old_clothing in self.accessories:
                self.accessories.remove(old_clothing)

            self.update_slut_requirement()

        def get_upper_ordered(self): #Returns a list of pieces from bottom to top, on the upper body. Other functions do similar things, but to lower and feet.
            return sorted(self.upper_body, key=lambda clothing: clothing.layer)

        def get_lower_ordered(self):
            return sorted(self.lower_body, key=lambda clothing: clothing.layer)

        def get_feet_ordered(self):
            return sorted(self.feet, key=lambda clothing: clothing.layer)


        def get_toplayer_for_condition(self, list_attr, cond_attr):
            ret = sorted(getattr(self, list_attr), key=lambda c: c.layer, reverse=True)
            i = next((i+1 for i, c in enumerate(ret) if not getattr(c, cond_attr)), len(list_attr))
            return ret[:i] # slice up to index after first anchoring item

        def get_upper_visible(self):
            return self.get_toplayer_for_condition("upper_body", "hide_below")

        def get_lower_visible(self):
            return self.get_toplayer_for_condition("lower_body", "hide_below")

        def get_feet_visible(self):
            return self.get_toplayer_for_condition("feet", "hide_below")

        def get_unanchored(self): #Returns a list of the pieces of clothing that can be removed.
            return [x for attr in ["upper_body", "lower_body", "feet"] for x in self.get_toplayer_for_condition(attr, "anchor_below")]

        def vagina_available(self): ## Doubles for asshole for anal.
            return not any(cloth.anchor_below for cloth in self.lower_body)

        def vagina_visible(self):
            return not any(cloth.hide_below for cloth in self.lower_body)

        def tits_available(self):
            return not any(cloth.anchor_below for cloth in self.upper_body)

        def tits_visible(self):
            return not any(cloth.hide_below for cloth in self.upper_body)

        def wearing_bra(self):
            return any(cloth.underwear for cloth in self.upper_body)

        def wearing_panties(self):
            return any(cloth.underwear for cloth in self.lower_body)

        def bra_covered(self):
            return len(self.upper_body) > 1 and any(cloth.underwear for cloth in self.upper_body)

        def panties_covered(self):
            return len(self.lower_body) > 1 and any(cloth.underwear for cloth in self.lower_body)

        def is_nude(self):
            return len(self.lower_body) + len(self.upper_body) == 0

        def update_slut_requirement(self): # Recalculates the slut requirement of the outfit. Should be called after each new addition.
            new_score = 0
            for attr in ["upper_body", "lower_body"]:
                lst = getattr(self, attr)
                if len(lst):
                    bits = 0xf # bits are unset below for each item that decreases slut value
                    for cloth in lst:
                        new_score += cloth.slut_value
                        if cloth.anchor_below: # no easy tits / pussy access.
                            bits &= ~8
                        if cloth.hide_below: # layer not see-thru.
                            bits &= ~4
                        if not cloth.underwear:
                            bits &= ~2 # wearing an above underwear layer.
                        else:
                            bits &= ~1 # wearing underwear
                    # 10 * (has_access * 2 + has_see-thru * 2 + has_top_layer * 2 + has_underwear)
                    new_score += 10 * (((bits & 8) >> 2) + ((bits & 4) >> 1) + (bits & 3))
                else:
                    new_score += 40 # No top/bottom is worth a flat 40.

            for cloth in self.feet: #Add the extra sluttiness values of any of the pieces of clothign we're wearing.
                new_score += cloth.slut_value

            self.slut_requirement = new_score

    #FIXME: this can really just be a dict.
    class Wardrobe(renpy.store.object): #A bunch of outfits!
        def __init__(self,name,outfits): #Outfits is a list of Outfit objects, or empty if the wardrobe starts empty
            self.name = name
            self.outfits = outfits

        def __copy__(self):
            copy_list = []
            for outfit in self.outfits:
                copy_list.append(outfit)
            return Wardrobe(self.name,copy_list)


        def add_outfit(self,new_outfit):
            self.outfits.append(new_outfit)

        def remove_outfit(self, old_outfit):
            if old_outfit in self.outfits:
                self.outfits.remove(old_outfit)

        def pick_random_outfit(self):
            return copy.deepcopy(renpy.random.choice(self.outfits)) # Take a deep copy, so you can change the outfit in a scene without changing the wardrobe.

        def get_count(self):
            return len(self.outfits)

        def has_outfit_with_name(self, the_name):
            return any(outfit.name == the_name for outfit in self.outfits)

        def get_outfit_with_name(self, the_name):
            return next((c for c in self.outfits if c == the_name), None)

        def trim_wardrobe(self,sluttiness_threshold):
            self.outfits = filter(lambda outfit: outfit.slut_requirement <= sluttiness_threshold, self.outfits)
