init -17 python:
    class Personality(renpy.store.object): #How the character responds to various actions
        def __init__(self,type,greeting_label,sex_response_label,climax_response_label,clothing_accept_label, clothing_reject_label, clothing_review_label, strip_reject_label, sex_accept_label, sex_obedience_accept_label, sex_gentle_reject_label,
            sex_angry_reject_label, seduction_response_label, flirt_response_label, cum_face_label, cum_mouth_label, suprised_exclaim_label): ##TODO: Add more stats when we know what they should be.
            self.type = type
            self.greeting_label = greeting_label
            self.sex_response_label = sex_response_label
            self.climax_response_label = climax_response_label
            self.clothing_accept_label = clothing_accept_label
            self.clothing_reject_label = clothing_reject_label
            self.clothing_review_label = clothing_review_label
            self.strip_reject_label = strip_reject_label
            self.sex_accept_label = sex_accept_label
            self.sex_obedience_accept_label = sex_obedience_accept_label
            self.sex_gentle_reject_label = sex_gentle_reject_label
            self.sex_angry_reject_label = sex_angry_reject_label
            self.seduction_response_label = seduction_response_label
            self.flirt_response_label = flirt_response_label
            self.cum_face_label = cum_face_label
            self.cum_mouth_label = cum_mouth_label
            self.suprised_exclaim_label = suprised_exclaim_label


        def get_greeting(self, the_person):
            renpy.call(self.greeting_label, the_person)

        def get_sex_response(self, the_person):
            renpy.call(self.sex_response_label, the_person)

        def get_climax_response(self, the_person):
            renpy.call(self.climax_response_label, the_person)

        def get_clothing_accept(self, the_person):
            renpy.call(self.clothing_accept_label, the_person)

        def get_clothing_reject(self, the_person):
            renpy.call(self.clothing_reject_label, the_person)

        def get_clothing_review(self, the_person):
            renpy.call(self.clothing_review_label, the_person)

        def get_strip_reject(self, the_person):
            renpy.call(self.strip_reject_label, the_person)

        def get_sex_accept_response(self, the_person):
            renpy.call(self.sex_accept_label, the_person)

        def get_sex_obedience_accept_response(self, the_person, amount):
            renpy.call(self.sex_obedience_accept_label, the_person, amount)

        def get_sex_gentle_reject(self, the_person):
            renpy.call(self.sex_gentle_reject_label, the_person)

        def get_sex_angry_reject(self, the_person, amount):
            renpy.call(self.sex_angry_reject_label, the_person, amount)

        def get_seduction_response(self, the_person):
            renpy.call(self.seduction_response_label, the_person)

        def get_flirt_response(self, the_person):
            renpy.call(self.flirt_response_label, the_person)

        def get_cum_face(self, the_person):
            renpy.call(self.cum_face_label, the_person)

        def get_cum_mouth(self, the_person):
            renpy.call(self.cum_mouth_label, the_person)

        def get_suprised_exclaim(self, the_person):
            renpy.call(self.suprised_exclaim_label, the_person)


    #Default personality is a well rounded personaity, without any strong tendencies. Default "Lily" personality.
    # FIXME: these could be dicts.
    relaxed_personality = Personality(
        "Relaxed", "relaxed_greetings", 
        "relaxed_sex_responses","relaxed_climax_responses",
        "relaxed_clothing_accept","relaxed_clothing_reject","relaxed_clothing_review","relaxed_strip_reject",
        "relaxed_sex_accept","relaxed_sex_obedience_accept","relaxed_sex_gentle_reject","relaxed_sex_angry_reject",
        "relaxed_seduction_response","relaxed_flirt_response",
        "relaxed_cum_face","relaxed_cum_mouth",
        "relaxed_suprised_exclaim"
        )
    
    reserved_personality = Personality(
        "Reserved", "reserved_greetings", 
        "reserved_sex_responses","reserved_climax_responses",
        "reserved_clothing_accept","reserved_clothing_reject","reserved_clothing_review","reserved_strip_reject",
        "reserved_sex_accept","reserved_sex_obedience_accept","reserved_sex_gentle_reject","reserved_sex_angry_reject",
        "reserved_seduction_response","reserved_flirt_response",
        "reserved_cum_face","reserved_cum_mouth",
        "reserved_suprised_exclaim"
        )
    
    list_of_personalities = [relaxed_personality,reserved_personality]
    
    def get_random_personality():
        return renpy.random.choice(list_of_personalities)

###############################
##### Relaxed Personality #####
###############################
init:
    pass

label relaxed_greetings(the_person):
    if the_person.sluttiness > 60:
        if the_person.obedience > 130:
            the_person.name "Hello master, it's good to see you."
        else:
            the_person.name "Hey there handsome, feeling good?" 
    else:
        if the_person.obedience > 130:
            the_person.name "Hello sir."
        else:
            the_person.name "Hey there!"
    return
    
label relaxed_sex_responses(the_person):
    if the_person.sluttiness > 50:
        if the_person.obedience > 130:
            the_person.name "Oh... Please keep doing that to me!"
        else:
            the_person.name "Fuck that feels nice... Keep doing that!"
    else:
        "[the_person.name] closes her eyes and moans quietly to herself."
    return
    
label relaxed_climax_responses(the_person):
    if the_person.sluttiness > 70:
        the_person.name "I'm going to cum! Ah! Make me cum [mc.name], I want to cum so badly! Ah!"
        "She closes her eyes and squeals with pleasure." 
    else:
        the_person.name "Ah! I'm cumming! Oh fuck! Ah!"
    return
    
label relaxed_clothing_accept(the_person):
    if the_person.obedience > 130:
        the_person.name "It's for me? Thank you sir, I'll add it to my wardrobe."
    else:
        the_person.name "Oh, it's cute! Thank's [mc.name]!"
    return
    
label relaxed_clothing_reject(the_person):
    if the_person.obedience > 130:
        the_person.name "Is that really for me sir? I want to... but I don't think I could wear that without getting in some sort of trouble."
    else:
        if the_person.sluttiness > 60:
            the_person.name "Wow. I'm usually up for anything but I think that's going too far."
        else:
            the_person.name "Wow. It's a little... skimpy. I don't think I could wear that."
    return
    
label relaxed_clothing_review(the_person):
    if the_person.obedience > 130:
        the_person.name "I'm sorry sir, you shouldn't have to see me like this. I'll go and get cleaned up so I'm presentable again."
    else:
        if the_person.sluttiness > 40:
            the_person.name "Whew, I think we messed up my clothes a bit. Just give me a quick second to get dressed into something more decent."
        else:
            the_person.name "My clothes are a mess! I'll be back in a moment, I'm going to go get cleaned up."
    return
                                                                            
label relaxed_strip_reject(the_person):
    if the_person.obedience > 130:
        the_person.name "I'm sorry, but can we leave that where it is for now?"
    elif the_person.obedience < 70:
        the_person.name "Slow down there, I'll decide when that comes off."
    else:
        the_person.name "I think that should stay where it is for now."
    return
                                                                            
label relaxed_sex_accept(the_person):
    if the_person.sluttiness > 70:
        if the_person.obedience < 70:
            the_person.name "I was just about to suggest the same thing."
        else:
            the_person.name "Mmm, you have a dirty mind [mc.name], I like it."
    else:
        the_person.name "Okay, we can give that a try."
    return
    
label relaxed_sex_obedience_accept(the_person, amount=None):
    if amount is not None:
        show screen float_up_screen(["%d Happiness"%amount],["float_text_yellow"])

    if the_person.sluttiness > 70:
        the_person.name "Oh god [mc.name], I should really say no... But you always make me feel so good, I can't say no to you."
    else:
        if the_person.obedience > 130:
            the_person.name "Yes sir, if that's what you want to do I'll give it a try."
        else:
            the_person.name "I... Okay, if you really want to, lets give it a try."
    return
    
label relaxed_sex_gentle_reject(the_person):
    if the_person.sluttiness > 50:
        the_person.name "Wait, I don't think I'm warmed up enough for this [mc.name]. How about we do something else first?"
    else:
        the_person.name "Wait. I don't think I'm comfortable with this. Could we just do something else instead?"
    return
    
label relaxed_sex_angry_reject(the_person, amount=None):
    if amount is not None:
        show screen float_up_screen(["%d Happiness"%amount],["float_text_yellow"])
    if the_person.sluttiness < 20:
        the_person.name "Who the fuck do you think I am, some whore who puts out for anyone who asks?"
        the_person.name "Ugh! Get away from me, I don't even want to talk to you after that."
    else:
        the_person.name "What the fuck do you think you're doing, that's disgusting!"
        the_person.name "Get the fuck away from me, I don't even want to talk to you after that!"
    return
    
label relaxed_seduction_response(the_person):
    if the_person.obedience > 130:
        if the_person.sluttiness > 50:
            the_person.name "Yes sir? Do you need help relieving some stress?"
        else:
            the_person.name "Yes sir? Is there something I can help you with?"
    else:
        if the_person.sluttiness > 50:
            the_person.name "Mmm, I know that look. Do you want to fool around a little?"
        elif the_person.sluttiness > 10:
            the_person.name "Oh, do you see something you like?"
        else:
            the_person.name "Oh, I don't really know what to say [mc.name]..."
    return
    
label relaxed_flirt_response(the_person):
    if the_person.obedience > 130:
        if the_person.sluttiness > 50:
            the_person.name "If that's what you want I'm sure I could help with that sir."
        else:
            the_person.name "Thank you for the compliment, sir."
    else:
        if the_person.sluttiness > 50:
            the_person.name "Mmm, if that's what you want I'm sure I could find a chance to give you a quick peak."
            "[the_person.name] smiles at you and spins around, giving you a full look at her body."
        else:
            the_person.name "Hey, maybe if you buy me dinner first."
            "[the_person.name] gives you a wink and smiles."
    return
    
label relaxed_cum_face(the_person):
    if the_person.obedience > 130:
        if the_person.sluttiness > 60:
            the_person.name "Do I look cute covered in your cum, sir?"
            "[the_person.name] licks her lips, cleaning up a few drops of your semen that had run down her face."
        else:
            the_person.name "I hope this means I did a good job."
            "[the_person.name] runs a finger along her cheek, wiping away some of your semen."
    else:
        if the_person.sluttiness > 80:
            the_person.name "Ah... I love a nice, hot load on my face. Don't you think I look cute like this?"
        else:
            the_person.name "Fuck me, you really pumped it out, didn't you?"
            "[the_person.name] runs a finger along her cheek, wiping away some of your semen."
    return
    
label relaxed_cum_mouth(the_person):
    if the_person.obedience > 130:
        if the_person.sluttiness > 60:
            the_person.name "That was very nice sir, thank you."
        else:
            "[the_person.name]'s face grimaces as she tastes your sperm in her mouth."
            the_person.name "Thank you sir, I hope you had a good time."       
    else:
        if the_person.sluttiness > 80:
            the_person.name "Your cum tastes great [mc.name], thanks for giving me so much of it."
            "[the_person.name] licks her lips and sighs happily."            
        else:
            the_person.name "Bleh, I don't know if I'll ever get use to that."
    return
    
label relaxed_suprised_exclaim(the_person):
    $rando = renpy.random.choice(["Fuck!","Shit!","Oh fuck!","Fuck me!","Ah! Oh fuck!", "Ah!", "Fucking tits!", "Holy shit!", "Fucking shit!"])
    the_person.name "[rando]"
    return
            
            
################################
##### Reserved Personality #####
################################
label reserved_greetings(the_person):
    if the_person.sluttiness > 60:
        if the_person.obedience > 130:
            the_person.name "Hello master."
        else:
            the_person.name "Hello, are you feeling as good as you're looking today?" 
    else:
        if the_person.obedience > 130:
            the_person.name "Hello sir."
        else:
            the_person.name "Hello, I hope you're doing well."
    return
    
label reserved_sex_responses(the_person):
    if the_person.sluttiness > 50:
        if the_person.obedience > 130:
            the_person.name "Mmmf, please keep doing that sir!"
        else:
            the_person.name "Wow that feels... nice. Please don't stop."
    else:
        "[the_person.name] closes her eyes and moans quietly to herself."
    return
    
label reserved_climax_responses(the_person):
    if the_person.sluttiness > 70:
        the_person.name "You're going to... Ah! You're going to make me climax [mc.name]!"
        "She closes her eyes as she tenses up. She freezes for a long second, then lets out a long, slow breath." 
    else:
        the_person.name "Oh, I think I'm about to... Oh yes!"
    return
    
label reserved_clothing_accept(the_person):
    if the_person.obedience > 130:
        the_person.name "You're too kind sir. I'll add it to my wardrobe right away."
    else:
        the_person.name "For me? Oh, I'm not use to getting gifts like this..."
    return
    
label reserved_clothing_reject(the_person):
    if the_person.obedience > 130:
        the_person.name "You're too kind sir, really. I don't think I can accept such a... beautiful gift from you though."
    else:
        if the_person.sluttiness > 60:
            the_person.name "It's very nice [mc.name], but I think it's a little too revealing, even for me. Maybe when I'm feeling a little more bold, okay?"
        else:
            the_person.name "Really [mc.name]? Just suggesting that I would wear something like that is a little too forward, don't you think?"
    return
    
label reserved_clothing_review(the_person):
    if the_person.obedience > 130:
        the_person.name "I'm such a mess right now sir, I just have to go and get tidied up for you. I'll be back in a moment."
    else:
        if the_person.sluttiness > 40:
            the_person.name "Oh dear, my clothes are just a mess after all of that. Not that I'm complaining, of course, but I should go get tidied up. Back in a moment."
        else:
            the_person.name "Oh, I look like such a mess right now. I'll be back in a moment."
    return
                                                                            
label reserved_strip_reject(the_person):
    if the_person.obedience > 130:
        the_person.name "I'm sorry sir, but I think that should stay where it is for now. For modesty's sake."
    elif the_person.obedience < 70:
        the_person.name "That's going to stay right there for now. I'll decide when I want it to come off, okay?."
    else:
        the_person.name "[mc.name], I don't feel comfortable taking that off. Just leave it put."
    return
                                                                            
label reserved_sex_accept(the_person):
    if the_person.sluttiness > 70:
        if the_person.obedience < 70:
            the_person.name "Good, I didn't want to be the one to suggest it but that sounds like fun."
        else:
            the_person.name "Mmm, you think we should give that a try? I'm feeling adventurous today, lets go."
    else:
        the_person.name "Oh, I know I shouldn't [mc.name]... but I think you've managed to convince me."
    return
    
label reserved_sex_obedience_accept(the_person, amount=None):
    if amount is not None:
        show screen float_up_screen(["%d Happiness" % amount],["float_text_yellow"])

    if the_person.sluttiness > 70:
        the_person.name "I shouldn't... I really shouldn't. But I know you want me, and I think I want you too. Promise you'll make me feel good too?"
    else:
        if the_person.obedience > 130:
            the_person.name "Okay sir, if that's what you want. I'll do what I can to serve you."
        else:
            the_person.name "If it were anyone other than you I'd say no [mc.name]. Don't get too use to this, okay?"
    return
    
label reserved_sex_gentle_reject(the_person):
    if the_person.sluttiness > 50:
        the_person.name "Wait, a lady must be romanced first [mc.name]. At least get me warmed up first."
    else:
        the_person.name "This doesn't seem like the kind of thing a proper lady would do. Lets do something else, please."
    return
    
label reserved_sex_angry_reject(the_person, amount=None):
    if amount is not None:
        show screen float_up_screen(["%d Happiness" % amount],["float_text_yellow"])
    if the_person.sluttiness < 20:
        the_person.name "Excuse me? Do I look like some sort of prostitute?"
        the_person.name "Get away from me, you're lucky I don't turn you into the police for that! Give me some space, I don't want to talk after that."
    else:
        the_person.name "Um, what do you think you're doing [mc.name]? That's disgusting, and certainly no way to act around a lady!"
    return
    
label reserved_seduction_response(the_person):
    if the_person.obedience > 130:
        if the_person.sluttiness > 50:
            the_person.name "Hello sir, is there something I can help you with? Something of a personal nature perhaps?"
        else:
            the_person.name "Hello sir, is there something I can help you with?"
    else:
        if the_person.sluttiness > 50:
            the_person.name "You've got that look in your eye again. there's just no satisfying you, is there? You're lucky I'm such a willing participant."
        elif the_person.sluttiness > 10:
            the_person.name "Oh [mc.name], you always know how to make a woman feel wanted..."
        else:
            the_person.name "[mc.name], isn't that a little bit forward of you? I'm not saying no though..."
    return
    
label reserved_flirt_response(the_person):
    if the_person.obedience > 130:
        if the_person.sluttiness > 50:
            the_person.name "It would be so improper, but for you I'm sure I could arange something special."
        else:
            the_person.name "Thank you for the compliment, sir, I appreciate it."
    else:
        if the_person.sluttiness > 50:
            the_person.name "Oh [mc.name], that's so naughty of you to even think about..."
            "[the_person.name] winks at you and spins, giving you a full look at her body."
            the_person.name "How will I ever get you to contain yourself?"
        else:
            the_person.name "Please sir, a woman like me likes a little romance in her relationships. At least buy me dinner first."
    return
            
label reserved_cum_face(the_person):
    if the_person.obedience > 130:
        if the_person.sluttiness > 60:
            the_person.name "Ah, that's always a pleasure, sir."
        else:
            the_person.name "Well that's certainly a lot. I hope that means I did a satisfactory job."
    else:
        if the_person.sluttiness > 80:
            the_person.name "Oh [mc.name], what are you doing to me? I'm beginning to like looking like this!"            
        else:
            the_person.name "Oh god [mc.name], could you imagine if someone saw me like this? I really should go and get cleaned up."
    return
    
label reserved_cum_mouth(the_person):
    if the_person.obedience > 130:
        if the_person.sluttiness > 60:
            the_person.name "Mmm, always a pleasure to taste you sir. I hope you had a good time."
        else:
            "[the_person.name] puckers her lips, obviously not happy with the taste but too polite to say anything."
    else:
        if the_person.sluttiness > 80:
            the_person.name "You're making me act like such a slut [mc.name], what would the other women think if they knew what I just did?"
        else:
            the_person.name "Well, at least there's no mess to clean up. I need to go wash my mouth out after that though."
    return
    
label reserved_suprised_exclaim(the_person):
    $rando = renpy.random.choice(["Oh my!","Oh, that's not good!", "Whoa!", "Ah!", "My word!", "Oops!", "Bah!", "Dangnabbit!"])
    the_person.name "[rando]"
    return
    
    
