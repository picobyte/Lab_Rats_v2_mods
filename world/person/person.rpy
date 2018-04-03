init -16 python:
    class Person(renpy.store.object):

        # static variables - shared for every instance of class - to create random characters
        list_of_names = ["Alexia", "Ashley", "Brendan", "Brittany", "Charisma", "Danielle", "Emma", "Erika", "Helen",
                         "Jennifer", "Jenny", "Jessica", "Jose", "Katya", "Lily", "Maya", "Mayumi", "Nora",
                         "Sally", "Sandra", "Saphirette", "Sarah", "Stephanie", "Victoria"]

        list_of_last_names = ["Bergstrom", "Fallbrooke", "Fernandez", "Fields", "Hitchcock", "Kurokami", "Marie",
                              "Millstein", "Moran", "Orion", "Peters", "Sky", "Spherica", "Williams"]

        list_of_hairs = ["blond", "black", "brown", "red"]
        list_of_faces = ["Face_1", "Face_2", "Face_3"]
        list_of_eyes = ["blue", "green", "brown", "grey"]
        list_of_body_types = [ "Average", "Thin", "Fat"]

        ##NAKED BODIES##
        body_image_for = {
            "white": Clothing("white skin", 1, True, True, "white", ["stand1","stand2","stand3","doggy"], True, False, 0),
            "black": Clothing("black skin", 1, True, True, "black", ["stand1","stand2","stand3","doggy"], True, False, 0),
            "tan": Clothing("tan skin", 1, True, True, "tan", ["stand1","stand2","stand3","doggy"], True, False, 0)
        }

        list_of_skins = [("white", 3), ("black", 1), ("tan", 1)] # TODO make weigths configureable as preference for user.
        list_of_tits = [("AA",5), ("A",15), ("B",30), ("C",30), ("D",15), ("DD",10), ("DDD",5), ("E",2), ("F",1), ("FF",1)]

        list_of_jobs = ["scientist", "secretary", "PR representative", "sales person"]

        technobabble_list = [ "optimize the electromagnetic pathways", "correct for the nanowave signature", "de-scramble the thermal injector",
                             "crosslink the long chain polycarbons", "carbonate the ethyl groups", "oxdize the functional group",
                             "resynchronize the autosequencers", "invert the final power spike", "kickstart the process a half second early",
                             "stall the process by a half second", "apply a small machine learning algorithm", "hit the thing in just the right spot",
                             "wait patiently for it to finish"]

        hair_styles = [Hair_Style("side combed", "Side_Hair"), Hair_Style("twin ponytail", "Twintail"),
                       Hair_Style("short", "Short_Hair"), Hair_Style("ponytail", "Ponytail")]

        #Default personality is a well rounded personaity, without any strong tendencies. Default "Lily" personality.
        list_of_personalities = [Personality("Relaxed", "relaxed_greetings",
                                             "relaxed_sex_responses","relaxed_climax_responses",
                                             "relaxed_clothing_accept","relaxed_clothing_reject","relaxed_clothing_review","relaxed_strip_reject",
                                             "relaxed_sex_accept","relaxed_sex_obedience_accept","relaxed_sex_gentle_reject","relaxed_sex_angry_reject",
                                             "relaxed_seduction_response","relaxed_flirt_response",
                                             "relaxed_cum_face","relaxed_cum_mouth",
                                             "relaxed_suprised_exclaim"),
                                 Personality("Reserved", "reserved_greetings",
                                             "reserved_sex_responses","reserved_climax_responses",
                                             "reserved_clothing_accept","reserved_clothing_reject","reserved_clothing_review","reserved_strip_reject",
                                             "reserved_sex_accept","reserved_sex_obedience_accept","reserved_sex_gentle_reject","reserved_sex_angry_reject",
                                             "reserved_seduction_response","reserved_flirt_response",
                                             "reserved_cum_face","reserved_cum_mouth",
                                             "reserved_suprised_exclaim")]

        def __init__(self, name, stats, skills, sex_list):
            self.name = name

            #TODO: Integrate this with the rest of the game, so you can have different fonts for different characters, different colours, etc.
            self.char_object = Character(name,what_font="Avara.ttf") #We use this to customize the font in the dialogue boxes

            ##Mental stats##
            #Mental stats are generally fixed and cannot be changed permanently. Ranges from 1 to 5 at start, can go up or down (min 0)
            self.charisma = stats[0] #How likeable the person is. Mainly influences marketing, also determines how well interactions with other characters go. Main stat for HR and sales
            self.int = stats[1] #How smart the person is. Mainly influences research, small bonuses to most tasks. #Main stat for research and production.
            self.focus = stats[2] #How on task the person stays. Influences most tasks slightly. #Main stat for supplies

            ##Work Skills##
            #Skills can be trained up over time, but are limited by your raw stats. Ranges from 1 to 5 at start, can go up or down (min 0)
            self.hr_skill = skills[0]
            self.market_skill = skills[1]
            self.research_skill = skills[2]
            self.production_skill = skills[3]
            self.supply_skill = skills[4]

            ##Sex Stats##
            #These are physical stats about the girl that impact how she behaves in a sex scene. Future values might include things like breast sensitivity, pussy tighness, etc.
            self.arousal = 0 #How actively horny a girl is, and how close she is to orgasm. Generally resets to 0 after orgasming, and decreases over time while not having sex (or having bad sex).

            ##Sex Skills##
            #These represent how skilled a girl is at different kinds of intimacy, ranging from kissing to anal. The higher the skill the closer she'll be able to bring you to orgasm (whether you like it or not!)
            self.sex_skills = {}
            self.sex_skills["Foreplay"] = sex_list[0] #A catch all for everything that goes on before blowjobs, sex, etc. Includes things like kissing and strip teases.
            self.sex_skills["Oral"] = sex_list[1] #The girls skill at giving head.
            self.sex_skills["Vaginal"] = sex_list[2] #The girls skill at different positions that involve vaginal sex.
            self.sex_skills["Anal"] = sex_list[3] #The girls skill at different positions that involve anal sex.

        def change_arousal(self,amount):
            self.arousal += amount
            if self.arousal < 0:
                self.arousal = 0

        def reset_arousal(self):
            self.arousal = 0
