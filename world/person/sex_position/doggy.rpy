init: 
    python:
        doggy = Position("Doggy",60,"doggy","Lay","Vagina","Vaginal",15,20,[],"intro_doggy",["scene_doggy_1","scene_doggy_2"],"outro_doggy","transition_default_doggy")
        list_of_positions.append(doggy)
        
#init 1: 
#    python:
#        #Here is where you would put connections if they existed.
    
label intro_doggy(the_girl, the_location, the_object, the_round):
    world.mc.name "[the_girl.name], I want you to get on your hands and knees for me."
    if the_girl.sluttiness > 80:
        the_girl.name "Mmm,, you know just what I like [world.mc.name]."
    else:
        the_girl.name "Like this?"
    "[the_girl.name] gets onto all fours in front of you on the [the_object.name]. She wiggles her ass impatiently at you as you get your hard cock lined up."
    if the_girl.arousal > 60:
        "You rub the tip of your penis against [the_girl.name]'s cunt, feeling how nice and wet she is already. She moans softly when you slide the head of your dick over her clit."
    else:
        "You rub the tip of your penis against [the_girl.name]'s cunt, getting ready to slide yourself inside."
    "When you're ready you push forward, slipping your shaft deep inside of [the_girl.name]. She gasps and quivers ever so slightly as you start to pump in and out."
    return
    
label scene_doggy_1(the_girl, the_location, the_object, the_round):
    "You grab onto [the_girl.name] by her hips and settle into a steady rhythm, pumping your cock in and out of her tight pussy."
    $ the_girl.call_sex_response()
    if the_girl.has_large_tits() and the_girl.outfit.tits_visible():
        "You give her ass a good spank and keep fucking her. Her big tits pendulum back and forth under her body, moving in time with your thrusts."
    else:
        "You give her ass a good spank and keep fucking her, enjoying the way her slit gets wetter and wetter as you go."
    return
    
label scene_doggy_2(the_girl, the_location, the_object, the_round):
    "[the_girl.name] lowers her shoulders against [the_object.name] and moans as you fuck her from behind."
    the_girl.name "Ah... it feels so big!"
    "You reach forward and place a hand around [the_girl.name]'s neck, using it as leverage to thrust even faster. She arches her back and lets out a series of satisfied yelps."
    $the_girl.call_sex_response()
    if the_girl.arousal > 80:
        "[the_girl.name]'s pussy is dripping wet, warm and tight around your cock. She twitches and gasps occasionally as you slide in, practically begging you to fuck her more."
    else:
        "[the_girl.name]'s pussy feels warm and tight around your cock as you fuck her."
    return
    
label outro_doggy(the_girl, the_location, the_object, the_round):
    "[the_girl.name]'s tight cunt draws you closer to your orgasm with each thrust. You finally pass the point of no return and speed up, fucking her as hard as you can manage."
    $the_girl.call_sex_response()
    world.mc.name "Ah, I'm going to cum!"
    menu:
        "Cum inside of her.":
            "You pull back on [the_girl.name]'s hips and drive your cock deep inside of her as you cum. She gasps softly in time with each new shot of hot semen inside of her."
            if the_girl.sluttiness > 80:
                the_girl.name "Oh wow, there's so much of it..."
            else:
                the_girl.name "Oh fuck, you're lucky I'm on the pill." #TODO: Make it possible to not be on the pill
            "You wait until your orgasm has passed completely, then pull out and sit back. Your cum starts to drip out of [the_girl.name]'s slit almost immediately."
            
        "Cum on her ass.":
            "You pull out of [the_girl.name] at the last moment, stroking your shaft as you blow your load over her ass. She holds still for you as you cover her with your sperm."
            if the_girl.sluttiness > 120:
                the_girl.name "What a waste, you should have put that inside of me."
                "She reaches back and runs a finger through the puddles of cum you've put on her, then licks her finger clean."
            else:
                the_girl.name "Oh wow, there's so much of it..."
            "You sit back and sigh contentedly, enjoying the sight of [the_girl.name] covered in your semen."
    return
    
label transition_default_doggy(the_girl, the_location, the_object, the_round):
    "[the_girl.name] gets on her hands and knees as you kneel behind her. You bounce your hard shaft on her ass a couple of times before lining yourself up with her cunt."
    "Once you're both ready you push yourself forward, slipping your hard shaft deep inside of her. She lets out a gasp under her breath."
    return