init: 
    python:
        missionary = Position("Missionary",40,"stand2","Lay","Vagina","Vaginal",20,15,[],"intro_missionary",["scene_missionary_1","scene_missionary_2"],"outro_missionary","transition_default_missionary")
        list_of_positions.append(missionary)
    
init 1:
    python:
        missionary.link_positions(piledriver,"transition_missionary_piledriver")
        
label intro_missionary(the_girl, the_location, the_object, the_round):
    "You run your hands along [the_girl.name]'s hips, feeling the shape of her body."
    mc.name "I want you to lie down for me."
    "She nods and lies down on the [the_object.name], waiting while you unzip your pants and climb on top of her."
    "[the_girl.name] wraps her arms around you and holds you close as you line your cock up with her pussy. She sighs happily into your ear as you slide into her."
    return
    
label scene_missionary_1(the_girl, the_location, the_object, the_round):
    $ the_girl.call_sex_response()
    "[the_girl.name] digs her fingers into your back as you pump in and out of her tight slit. She moans into your ear, letting you hear her soft gasps and yelps."
    if the_girl.arousal > 50:
        "Her pussy is dripping wet now, practically begging you to fuck it more. You kiss her and keep going."
    else:
        "Her pussy is starting to get nice and wet as you fuck it. You kiss her and keep going."
    return
    
label scene_missionary_2(the_girl, the_location, the_object, the_round):
    the_girl.name "Oh fuck... Kiss me [mc.name]!"
    "[the_girl.name] puts her arms around your head and neck and pulls you down to her. She closes her eyes and kisses you, sending her tongue out to twirl around yours."
    "You return the kiss, making out with her as you pump your hips back and forth. Her own hips rise and fall to meet yours."
    if the_girl.arousal > 50:
        "Her wet, hot pussy feels amazing wrapped around your cock. She's dripping wet now and obviously enjoying your treatment."
    else:
        "Her tight pussy feels amazing wrapped around your cock. From her moans and gasps you can tell she's enjoying your treatment."
    return
    
label outro_missionary(the_girl, the_location, the_object, the_round):
    "You get to hear every little gasp and moan from [the_girl.name] as you're pressed up against her. Combined with the feeling of fucking her pussy it's not long before you're pushed past the point of no return."
    mc.name "I'm going to cum!"
    if the_girl.sluttiness > 120:
        the_girl.name "Go ahead and cum inside me. I want it nice and deep again, get me really fucking pregnant!"
    else:
        the_girl.name "Ah! Make sure to pull out!"
    menu:
        "Cum inside of her.":
            "You use your full weight to push your cock deep inside of [the_girl.name]'s cunt as you climax. She gasps and claws lightly at your back as you pump your seed into her."
            if the_girl.sluttiness > 120:
                the_girl.name "That's it... Ah..."
            else:
                the_girl.name "Fuck! I said not to... Ah... Not to do that! You're lucky I'm on the pill."
            "You take a moment to catch your breath, then roll off of [the_girl.name] and lie beside her."
            
        "Cum on her chest.":
            "You pull out at the last moment and grab your cock. You kneel and stroke yourself off, blowing your load over [the_girl.name]'s stomach."
            the_girl.name "Ah... Good job... Ah..."
            "You sit back and sigh contentedly, enjoying the sight of [the_girl.name]'s body covered in your semen."
    return
    
label transition_missionary_piledriver(the_girl, the_location, the_object, the_round):
    "[the_girl.name]'s pussy feels so warm and inviting, you can't help but want to get deeper inside of her. You pause for a moment and reach down for her legs."
    the_girl.name "Hey, what's... Whoa!"
    "You pull her legs up and bend them over her shoulders. You hold onto her ankles as you start to fuck her again, pushing your hard cock nice and deep."
    return
    
label transition_default_missionary(the_girl, the_location, the_object, the_round):
    "You put [the_girl.name] on her back and lie down on top of her, lining your hard cock up with her tight cunt."
    "After running the tip of your penis along her slit a few times you press forward, sliding inside of her. She gasps softly and closes her eyes."
    return