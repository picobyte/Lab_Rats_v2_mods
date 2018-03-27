init -2:
    python:
        
        def get_random_from_list(list):
            if len(list) > 0:
                return list[renpy.random.randint(0,len(list)-1)]
            else:
                return None
            
        def get_random_from_weighted_list(list): #Passed a list of parameters which are ["Thing", weighted value]
            if len(list) == 0:
                return None
            
            total_value = 0
            for item in list:
                total_value += item[1] #Get the total weighting value that we use to determine what thing we've picked.
                
            random_value = renpy.random.randint(0,total_value) #Gets us a value somewhere inside of our probability space.
            running_total = 0
            for item in list:
                if random_value <= (item[1]+running_total):
                    return item[0]
                else:
                    running_total += item[1]
        
        list_of_names = []
        
        list_of_names.append("Jessica")
        list_of_names.append("Jenny")
        list_of_names.append("Victoria")   
        list_of_names.append("Lily")
        list_of_names.append("Jennifer")
        list_of_names.append("Nora")
        list_of_names.append("Stephanie")
        list_of_names.append("Alexia")
        list_of_names.append("Danielle")
        list_of_names.append("Ashley")
        list_of_names.append("Brittany")
        list_of_names.append("Sally")
        list_of_names.append("Helen")
        list_of_names.append("Sarah")
        list_of_names.append("Erika")
        list_of_names.append("Sandra")
        list_of_names.append("Maya")
        list_of_names.append("Emma")
        list_of_names.append("Katya")
        list_of_names.append("Saphirette")
        list_of_names.append("Charisma")
        list_of_names.append("Mayumi")
        list_of_names.append("Brendan")
        list_of_names.append("Jose")
            
        def get_random_name():
            return get_random_from_list(list_of_names)
            
        list_of_last_names = []
        list_of_last_names.append("Hitchcock")
        list_of_last_names.append("Peters")
        list_of_last_names.append("Fallbrooke")
        list_of_last_names.append("Williams")
        list_of_last_names.append("Orion")
        list_of_last_names.append("Marie")
        list_of_last_names.append("Millstein")
        list_of_last_names.append("Sky")
        list_of_last_names.append("Spherica")
        list_of_last_names.append("Fields")
        list_of_last_names.append("Moran")
        list_of_last_names.append("Kurokami")
        list_of_last_names.append("Bergstrom")
        list_of_last_names.append("Fernandez")
        
        def get_random_last_name():
            return get_random_from_list(list_of_last_names)
            
        list_of_hairs = []
        list_of_hairs.append("blond")
        list_of_hairs.append("brown")
        list_of_hairs.append("black")
        list_of_hairs.append("red")
        
        def get_random_hair_colour():
            return get_random_from_list(list_of_hairs)
            
        list_of_skins = []
        list_of_skins.append(["white",3])
        list_of_skins.append(["black",1])
        list_of_skins.append(["tan",1])
        
        def get_random_skin():
            return get_random_from_weighted_list(list_of_skins)
            
        list_of_faces = []
        list_of_faces.append("Face_1")
        list_of_faces.append("Face_2")
        list_of_faces.append("Face_3")
        
        def get_random_face():
            return get_random_from_list(list_of_faces)
            
        list_of_eyes = []
        list_of_eyes.append("blue")
        list_of_eyes.append("green")
        list_of_eyes.append("brown")
        list_of_eyes.append("grey")
        
        def get_random_eye():
            return get_random_from_list(list_of_eyes)
            
        list_of_tits = []
        list_of_tits.append(["AA",5])
        list_of_tits.append(["A",15])
        list_of_tits.append(["B",30])
        list_of_tits.append(["C",30])
        list_of_tits.append(["D",15])
        list_of_tits.append(["DD",10])
        list_of_tits.append(["DDD",5])
        list_of_tits.append(["E",2])
        list_of_tits.append(["F",1])
        list_of_tits.append(["FF",1])
        
        def get_random_tit():
            return get_random_from_weighted_list(list_of_tits)
            
        def get_smaller_tits(current_tits):
            for tits in list_of_tits:
                if current_tits == tits[0]:
                    current_index = list_of_tits.index(tits)
            if current_index > 0: #If they are not min size.
                return list_of_tits[current_index-1][0]
            else:
                return current_tits
            
        def get_larger_tits(current_tits):
            for tits in list_of_tits:
                if current_tits == tits[0]: #Needed to account for the fact that this is now a 3d array.
                    current_index = list_of_tits.index(tits)
            if current_index < len(list_of_tits)-1: #If they are not max size, get the next index up.
                return list_of_tits[current_index+1][0]
            else:
                return current_tits #This is as large as they can get on our current chart.
            
        list_of_jobs = []
        list_of_jobs.append("scientist")
        list_of_jobs.append("secretary")
        list_of_jobs.append("PR representative")
        list_of_jobs.append("sales person")
        
        def get_random_job():
            return get_random_from_list(list_of_jobs)
            
        list_of_body_types = []
        list_of_body_types.append("Thin")
        list_of_body_types.append("Average")
        list_of_body_types.append("Fat")
        
        def get_random_body_type():
            return get_random_from_list(list_of_body_types)
            
        technobabble_list = []
        technobabble_list.append("optimize the electromagnetic pathways")
        technobabble_list.append("correct for the nanowave signature")
        technobabble_list.append("de-scramble the thermal injector")
        technobabble_list.append("crosslink the long chain polycarbons")
        technobabble_list.append("carbonate the ethyl groups")
        technobabble_list.append("oxdize the functional group")
        technobabble_list.append("resynchronize the autosequencers")
        technobabble_list.append("invert the final power spike")
        technobabble_list.append("kickstart the process a half second early")
        technobabble_list.append("stall the process by a half second")
        technobabble_list.append("apply a small machine learning algorithm")
        technobabble_list.append("hit the thing in just the right spot")
        technobabble_list.append("wait patiently for it to finish")
        
        
init 1 python:
    def generate_premade_list():
        global list_of_premade_characters
        list_of_premade_characters = []
        list_of_premade_characters.append(create_random_person(body_type = "Fat", height=0.99, skin="tan", tits="DD",hair_colour="red",hair_style=side_hair))
        list_of_premade_characters.append(create_random_person(body_type = "Thin", height=1.0, skin="white", tits="B",hair_colour="red",hair_style=side_hair))
        list_of_premade_characters.append(create_random_person(body_type = "Fat", height=0.96, skin="white", tits="DD",hair_colour="Brown",hair_style=twintail_hair))
    
    def get_premade_character(): #Get a premade character and return them when the function is called.
        person = get_random_from_list(list_of_premade_characters)
        if person is not None:
            list_of_premade_characters.remove(person)
        return person
            