init: 
    python:
        against_wall = Position("Against the Wall",60,"stand2","Lean","Vagina","Vaginal",20,20,[],"intro_against_wall",["scene_against_wall_1","scene_against_wall_2","scene_against_wall_3"],"outro_against_wall","transition_default_against_wall")
        list_of_positions.append(against_wall)
        
#init 1:
#    python:
#        ##Here is where you would put connections if they existed.
    
label intro_against_wall(the_girl, the_location, the_object, the_round):
    "You put your arms around [the_girl.name] and spin her around, pointing her towards the [the_object.name]."
    if the_girl.sluttiness > 80:
        "[the_girl.name] plants her palms against [the_object.name] and wiggles her butt at you as you unzip your pants."
        the_girl.name "Mmm, what are you going to do to me?"
    else:
        "[the_girl.name] plants her palms against [the_object.name] and waits patiently while you unzip your pants."
    "You get your hard cock out and tap it against [the_girl.name]'s ass cheeks a couple of times, then line up with her pussy. She gasps softly as you slide yourself inside of her."
    return
    
label scene_against_wall_1(the_girl, the_location, the_object, the_round):
    "You grab onto [the_girl.name] by her hips and settle into a steady rhythm, pumping your cock in and out of her tight pussy."
    $ the_girl.call_sex_response()
    if the_girl.has_large_tits() and the_girl.outfit.tits_available():
        "You reach around and grab a handful of [the_girl.name]'s nice [the_girl.tits] sized tits. You give them a squeeze as you fuck her, rubbing your thumb over her hardening nipple."
    else:
        "You give [the_girl.name]'s ass a spank while you fuck her. She gasps softly."
    the_girl.name "Oh [mc.name]..."
    return
    
label scene_against_wall_2(the_girl, the_location, the_object, the_round):
    "You place a hand on [the_girl.name]'s shoulder and press her against the [the_object.name]. You pick up the pace and fuck her as hard as you can manage."
    if the_girl.sluttiness > 70:
        the_girl.name "Fuck, it feels like you're going to rip me in half with your huge cock!"
    else:
        the_girl.name "Ah... Fuck, you feel so big!"
    if the_girl.arousal > 50:
        "Her pussy is dripping wet. It feels great to slide yourself all the way into her with each stroke."
    else:
        "Her pussy is getting wetter as you go, reacting to the nice pounding you're giving her."   
    return

label scene_against_wall_3(the_girl, the_location, the_object, the_round):
    if the_girl.arousal + the_girl.sluttiness > 100:
        "[the_girl.name] rocks her hips back to meet yours with each thrust. You pause for a moment and let her work your shaft all by herself."
        "She looks back at you, bites her lip, and pushes herself deep on your cock. She gasps softly as she starts to grind her ass against your hips."
        $ the_girl.call_sex_response()
    else:
        "[the_girl.name] arches her back and leans into each of your thrusts, letting you get nice and deep. You pause for a second to appreciate the view of her cute ass."
        the_girl.name "Come on [mc.name], don't just stare at it..."
        "She pushes her ass back and slides you all the way inside of her again."
        

label outro_against_wall(the_girl, the_location, the_object, the_round):
    "[the_girl.name]'s tight cunt draws you closer to your orgasm with each thrust. You speed up as you pass the point of no return, pushing her up against the [the_object.name] and laying into her."
    $the_girl.call_sex_response()
    mc.name "Fuck, I'm going to cum!"
    menu:
        "Cum inside of her.":
            "You push forward as you finally climax, thrusting your cock as deep inside of [the_girl.name] as you can manage. She gasps softly each time your dick pulses and shoots hot cum into her."
            if the_girl.sluttiness > 80:
                the_girl.name "That's it, fill me up!"
            else:
                the_girl.name "Fuck... Ah you're lucky I'm on the pill..."
            "You wait until your orgasm has passed, then step back and sigh happily. [the_girl.name] stays leaning against the [the_object.name] for a few seconds as your semen drips down her leg."
            
        "Cum on her ass.":
            "You pull out of [the_girl.name] at the last moment, stroking your shaft as you blow your load over her ass. She wiggles her butt as you cover it with your sperm."
            if the_girl.sluttiness > 120:
                the_girl.name "What a waste, that would have felt so much better inside of me..."
                "She reaches back and runs a finger through the puddles of cum you've put on her, then licks her finger clean and winks at you."
            else:
                the_girl.name "Oh wow, there's so much of it. It feels so warm..."
            "You sigh contentedly and relax for a moment, enjoying the sight of [the_girl.name] covered in your semen."
    return
    
label transition_default_against_wall(the_girl, the_location, the_object, the_round):
    "You spin [the_girl.name] to face the [the_object.name] and she plants her palms on the surface, sticking her ass out at you."
    "You run the tip of your cock along her slit a few times, then slide yourself inside of her tight cunt."
    return