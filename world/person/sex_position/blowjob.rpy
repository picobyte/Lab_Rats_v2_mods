init: 
    python:
        blowjob = Position("Blowjob",50,"stand2","Kneel","None","Oral",2,20,[],"intro_blowjob",["scene_blowjob_1","scene_blowjob_2"],"outro_blowjob","transition_default_blowjob")
        list_of_positions.append(blowjob)
        
init 1:
    python:
        blowjob.link_positions(deepthroat,"transition_blowjob_deepthroat")
    
label intro_blowjob(the_girl, the_location, the_object, the_round):
    "You unzip your pants and pull your underwear down far enough to let your hard cock out."
    world.mc.name "How about your take care of this for me?"
    if the_girl.sluttiness > 35:
        "[the_girl.name] looks at your shaft for a moment, then drops to her knees in front of you. She runs her hands along your hips, then leans foward and slides her lips over the tip of your dick."
    else:
        "[the_girl.name] looks down at your shaft for a moment, thinks about it for a moment, then drops to her knees in front of you. She leans forward and kisses the tip of your dick gingerly."
    return
    
label scene_blowjob_1(the_girl, the_location, the_object, the_round):
    "[the_girl.name] keeps her mouth open wide and bobs her head back and forth to slide your cock in and out. The feeling of her soft, warm mouth sends shivers up your spine."
    "You rest your hand on her head, guiding her as she sucks you off."
    if the_girl.arousal > 60:
        if the_girl.outfit.vagina_available():
            "[the_girl.name] has a hand between her legs with two fingers sliding in and out of her pussy as she sucks you off. She moans softly whenever she isn't muffled by your dick."
        else:
            "[the_girl.name] has a hand between her legs, rubbing her crotch eagerly through her clothing as she sucks you off."
    "[world.mc.name]" "That's it, keep it up."
    return
    
label scene_blowjob_2(the_girl, the_location, the_object, the_round):
    "[the_girl.name] pulls your cock out of her her mouth and leans in even closer. She runs her tongue along the bottom of your shaft, pausing at the top to kiss the tip a few times."
    the_girl.name "Does that feel good?"
    world.mc.name "Yeah, it does. Keep it up."
    if the_girl.sluttiness > 75:
        "[the_girl.name] rubs your wet cock over her cheeks and sighs happily, then starts to lick the sides and bottom again. She makes sure to get every inch before sliding you back into her mouth."
    else:
        "[the_girl.name] smiles happily and keeps licking your cock, making sure to get every inch before sliding it back into her mouth."
        
    if the_girl.arousal > 60 and the_girl.outfit.vagina_visible():
        "[the_girl.name] seems very turned on right now. You can see that her pussy is dripping wet right now."
    return
    
label outro_blowjob(the_girl, the_location, the_object, the_round):
    "Little by little the soft, warm mouth of [the_girl.name] brings you closer to orgasm. One last pass across her velvet tongue is enough to push you past the point of no return."
    menu:
        "Cum on her face.":
            world.mc.name "Fuck, here I come!"
            "You take a step back, pulling your cock out of [the_girl.name]'s mouth with a satisfyingly wet pop, and take aim at her face."
            if the_girl.sluttiness > 80:
                "[the_girl.name] sticks out her tongue for you and holds still, eager to take your hot load."
                "You let out a shuddering moan as you cum, pumping your sperm onto [the_girl.name]'s face and into her open mouth. She makes sure to wait until you're completely finished."
            elif the_girl.sluttiness > 60:
                "[the_girl.name] closes her eyes and waits patiently for you to cum."
                "You let out a shuddering moan as you cum, pumping your sperm onto [the_girl.name]'s face. She waits until she's sure you're finished, then opens one eye and looks up at you."
            else:
                "[the_girl.name] closes her eyes and turns away, presenting her cheek to you as you finally climax."
                "You let out a shuddering moan as you cum, pumping your sperm onto [the_girl.name]'s face. She flinches as the first splash of warm liquid lands on her cheek, but doesn't pull away entirely."
            "You take a deep breath to steady yourself once you've finised orgasming. [the_girl.name] looks up at you from her knees, face covered in your semen."
            $ the_girl.call_cum_face()
            
        "Cum in her mouth.":
            world.mc.name "Fuck, I'm about to cum!"
            "You keep a hand on the back of [the_girl.name]'s head to make it clear you want her to keep sucking. She keeps blowing you until you tense up and start to pump your load out into her mouth."
            if the_girl.sluttiness > 70:
                "[the_girl.name] doesn't even flinch as you shoot your hot cum across the back of her throat. She keeps bobbing her head up and down until you've let out every last drop, then slides back carefully and looks up with a mouth full of sperm."
            else:
                "[the_girl.name] stops when you shoot your first blast of hot cum across the back of her throat. She pulls back, leaving just the tip of your cock in her mouth as you fill it up with semen. Once you've finished she slides off and looks up to show you a mouth full of sperm."
            
            if the_girl.sluttiness > 80:
                "Once you've had a good long look at your work [the_girl.name] closes her mouth and swallows loudly. It takes a few big gulps to get every last drop of your cum down, but when she opens up again it's all gone."
            else:
                "Once you've had a good long look at your work [the_girl.name] leans over to the side and lets your cum dribble out slowly onto the ground. She straightens up and wipes her lips with the back of her hand."
            $ the_girl.call_cum_mouth()
    return
    
label transition_blowjob_deepthroat(the_girl, the_location, the_object, the_round):
    world.mc.name "Fuck that feels great [the_girl.name]. Think you can take it any deeper?"
    "[the_girl.name] slides off your dick with a wet pop and takes a few breaths."
    the_girl.name "Well, I can try."
    "Once she's caught her breath she opens her mouth wide and slides you back down her throat. She doesn't stop until her nose taps your stomach and she has your entire cock in her mouth."
    return
    
label transition_default_blowjob(the_girl, the_location, the_object, the_round):
    "[the_girl.name] gets onto her knees in front of you and takes your hard cock in her hands. She strokes it tentativly a few times, then leans in and slides the tip into her mouth."
    world.mc.name"That's it, that's a good girl."
    return