init -16 python:
    class Person(renpy.store.object):

        # static variables - shared for every instance of class - to create random characters
        list_of_names = ("Alexia", "Ashley", "Brendan", "Brittany", "Charisma", "Danielle", "Emma", "Erika", "Helen",
                         "Jennifer", "Jenny", "Jessica", "Jose", "Katya", "Lily", "Maya", "Mayumi", "Nora",
                         "Sally", "Sandra", "Saphirette", "Sarah", "Stephanie", "Victoria")

        list_of_last_names = ("Bergstrom", "Fallbrooke", "Fernandez", "Fields", "Hitchcock", "Kurokami", "Marie",
                              "Millstein", "Moran", "Orion", "Peters", "Sky", "Spherica", "Williams")

        list_of_hairs = ("blond", "black", "brown", "red")
        list_of_faces = ("Face_1", "Face_2", "Face_3")
        list_of_eyes = ("blue", "green", "brown", "grey")
        list_of_body_types = ("Average", "Thin", "Fat")

        ##NAKED BODIES##
        body_image_for = {
            "white": Clothing("white skin", 1, True, True, "white", ("stand1","stand2","stand3","doggy"), True, False, 0),
            "black": Clothing("black skin", 1, True, True, "black", ("stand1","stand2","stand3","doggy"), True, False, 0),
            "tan": Clothing("tan skin", 1, True, True, "tan", ("stand1","stand2","stand3","doggy"), True, False, 0)
        }

        list_of_skins = (("white", 3), ("black", 1), ("tan", 1)) # TODO make weigths configureable as preference for user.
        list_of_tits = (("AA",5), ("A",15), ("B",30), ("C",30), ("D",15), ("DD",10), ("DDD",5), ("E",2), ("F",1), ("FF",1))

        list_of_jobs = ("scientist", "secretary", "PR representative", "sales person")

        technobabble_list = ("optimize the electromagnetic pathways", "correct for the nanowave signature", "de-scramble the thermal injector",
                             "crosslink the long chain polycarbons", "carbonate the ethyl groups", "oxidize the functional group",
                             "resynchronize the autosequencers", "invert the final power spike", "kickstart the process a half second early",
                             "stall the process by a half second", "apply a small machine learning algorithm", "hit the thing in just the right spot",
                             "wait patiently for it to finish")

        hair_styles = (Hair_Style("side combed", "Side_Hair"), Hair_Style("twin ponytail", "Twintail"),
                       Hair_Style("short", "Short_Hair"), Hair_Style("ponytail", "Ponytail"))

        #Default personality is a well rounded personaity, without any strong tendencies. Default "Lily" personality.
        list_of_personalities = (Personality("Relaxed", "relaxed_greetings",
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
                                             "reserved_suprised_exclaim"))
        stats = (
            ("Main Stats", (("Charisma", "charisma"), ("Intelligence", "int"), ("Focus", "focus"))),
            ("Work Skills", (("Marketing", "market_skill"), ("Research and Development", "research_skill"), ("Production", "production_skill"), ("Supply Procurement", "supply_skill"), ("Human Resources", "hr_skill"))),
            ("Sex Skills", (("Foreplay", "foreplay"), ("Oral", "oral"), ("Vaginal", "vaginal"), ("Anal", "anal")))
        )
        terse_stat = {
            "Intelligence": "int",
            "Human Resources": "HR",
            "Research and Development": "Research",
            "Supply Procurement": "Supply"
        }
        stat_desc = {
            #Main or Mental stats are generally fixed and cannot be changed permanently. Ranges from 1 to 5 at start, can go up or down (min 0)

                #How likeable the person is. Mainly influences marketing, also determines how well interactions with other characters go. Main stat for HR and sales
                "Charisma": "Your visual appearance and force of personality. Charisma is the key attribute for selling serums and managing your business",
                #How smart the person is. Mainly influences research, small bonuses to most tasks. #Main stat for research and production.
                "Intelligence": "Your raw knowledge and ability to think quickly. Intelligence is the key attribute for research and development of serums",
                #How on task the person stays. Influences most tasks slightly. #Main stat for supplies
                "Focus": "Your mental endurance and precision. Focus is the key attribute for production and supply procurement",

            #Skills can be trained up over time, but are limited by your raw stats. Ranges from 1 to 5 at start, can go up or down (min 0)

                "Human Resources": "Your skill at human resources. Crucial for maintaining an efficent business",
                "Marketing": "Your skill at marketing. Higher skill will allow you to ship more doses of serum per world.day",
                "Research and Development": "Your skill at researching new serum traits and designs. Critical for improving your serum inventorm",
                "Production": "Your skill at producing serum in the production lab. Produced serums can then be sold for profit or kept for personal use",
                "Supply Procurement": "Your skill at obtaining raw supplies for your production division. Without supply, nothing can be created in the lab",

            #These are physical stats about the girl that impact how she behaves in a sex scene. Future values might include things like breast sensitivity, pussy tighness, etc.

                #A catch all for everything that goes on before blowjobs, sex, etc. Includes things like kissing and strip teases.
                "Foreplay": "Your skill at foreplay, including fingering, kissing, and groping", #The girls skill at giving head.
                "Oral": "Your skill at giving oral to women, as well as being a pleasant recipiant", #The girls skill at giving head.
                "Vaginal": "Your skill at vaginal sex in any position", #The girls skill at different positions that involve vaginal sex.
                "Anal": "Your skill at anal sex in any position. (NOTE: No content included in this version)" #The girls skill at different positions that involve anal sex.
        }

        def __init__(self, **kwargs):
            self.__dict__.update(**kwargs)

            #TODO: Integrate this with the rest of the game, so you can have different fonts for different characters, different colours, etc.
            self.char_object = Character(what_font="Avara.ttf") #We use this to customize the font in the dialogue boxes
            self.arousal = 0 #How actively horny a girl is, and how close she is to orgasm. Generally resets to 0 after orgasming, and decreases over time while not having sex (or having bad sex).
            self.inventory = collections.defaultdict(default_to_zero)

        def change_arousal(self,amount):
            self.arousal = max(self.arousal + amount, 0)

        def reset_arousal(self):
            self.arousal = 0
