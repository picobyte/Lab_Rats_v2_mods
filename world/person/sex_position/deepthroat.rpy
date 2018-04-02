init: 
    python:
        deepthroat = Position("Deepthroat",70,"stand2","Kneel","None","Oral",3,20,[],"intro_deepthroat",["scene_deepthroat_1","scene_deepthroat_2"],"outro_deepthroat","transition_default_deepthroat")
        list_of_positions.append(deepthroat)
        
init 1: 
    python:
        deepthroat.link_positions(blowjob,"transition_deepthroat_blowjob")
    
label intro_deepthroat(the_girl, the_location, the_object, the_round):
    "You unzip your pants and pull your underwear down, letting your hard cock spring free."
    mc.name "[the_girl.name], mind getting on your knees and taking this nice and deep for me?"
    if the_girl.sluttiness > 50:
        "[the_girl.name] reaches down and runs a finger along the top of your dick, then smiles and drops to her knees and looks up at you."
        the_girl.name "Okay [mc.name], I'll see what I can do."
    else:
        "[the_girl.name] reaches down and runs a finger along the top of your dick. She hesitates for a few moments, then drops to her knees."
        the_girl.name "I'll... I'll do my best."
    "She kisses the tip of your cock, then slides it into her mouth. Bit by bit she takes it deeper, until you have your entire shaft down her throat. She pauses there for a moment, then starts to bob her head up and down slowly."
    return
    
label scene_deepthroat_1(the_girl, the_location, the_object, the_round):
    "[the_girl.name] holds herself down on your hard cock for a few long seconds. She looks up at you, maintaining eye contact as she licks at the bottom of your shaft with her tongue."
    mc.name "Fuck, that feels great [the_girl.name]."
    "She pushes you just a little bit deeper, then slides back and off. She strokes your wet dick with her hand as she catches her breath."
    the_girl.name "Ah... Glad you like it. Okay, lets keep going."
    "She wastes no time sliding you right back down her throat. She gags a little as she bottoms out on your cock. The feeling of her warm, wet mouth sends pleasant shivers up your spine."
    return
    
label scene_deepthroat_2(the_girl, the_location, the_object, the_round):
    "You place a firm hand on the back of [the_girl.name]'s head, guiding her up and down your shaft. You encourage her to speed up, while making sure she keeps you nice and deep down her throat."
    if the_girl.sluttiness > 80:
        "[the_girl.name] turns her eyes up and meets your gaze as she throats you, her tongue eagerly licking at the bottom of your shaft."
    else:
        "[the_girl.name] closes her eyes and focuses on taking your cock even deeper as she throats you."
        
    if mc.arousal > 70:
        mc.name "Fuck, keep that up and I'll be cumming soon!"
    else:
        mc.name "That's it, keep it up. You're doing a great job [the_girl.name]!"
    
    return
    
label outro_deepthroat(the_girl, the_location, the_object, the_round):
    "The warm, tight feeling of [the_girl.name]'s throat wrapped around your shaft pulls you closer and closer to orgasm. You feel yourself pass the point of no return and let out a soft moan."
    menu:
        "Cum on her face.":
            mc.name "Fuck, here I come!"
            "You take a step back, pulling your cock out of [the_girl.name]'s throat with a satisfyingly wet pop, and take aim at her face."
            if the_girl.sluttiness > 80:
                "[the_girl.name] sticks out her tongue for you and holds still, eager to take your hot load."
                "You let out a shudder moaning as you cum, pumping your sperm onto [the_girl.name]'s face and into her open mouth. She makes sure to wait until you're completely finished."
                the_girl.name "TODO: Add cum response lines."
            elif the_girl.sluttiness > 60:
                "[the_girl.name] closes her eyes and waits patiently for you to cum."
                "You let out a shudder moaning as you cum, pumping your sperm onto [the_girl.name]'s face. She waits until she's sure you're finished, then opens one eye and looks up at you."
            else:
                "[the_girl.name] closes her eyes and turns away, presenting her cheek to you as you finally climax."
                "You let out a shudder moaning as you cum, pumping your sperm onto [the_girl.name]'s face. She flinches as the first splash of warm liquid lands on her cheek, but doesn't pull away entirely."
            "You take a deep breath to steady yourself once you've finised orgasming. [the_girl.name] looks up at you from her knees, face covered in your semen."
            $ the_girl.call_cum_face()
            
        "Cum in her mouth.":
            mc.name "Fuck, I'm about to cum! I'm going to fill that cute mouth of yours up!"
            "You keep your hand on the back of [the_girl.name]'s head to make it clear you want her to keep sucking. She keeps throating you until you tense up and start to pump your load out into her mouth."
            if the_girl.sluttiness > 70:
                "[the_girl.name] doesn't even flinch as you shoot your hot cum across the back of her throat. She keeps bobbing her head up and down until you've let out every last drop, then slides back carefully and looks up with a mouth full of sperm."
            else:
                "[the_girl.name] stops when you shoot your first blast of hot cum across the back of her throat. She pulls back, leaving just the tip of your cock in her mouth as you fill it up with semen. Once you've finished she slides off and looks up to show you a mouth full of sperm."
            
            if the_girl.sluttiness > 80:
                "Once you've had a good long look at your work [the_girl.name] closes her mouth and swallows loudly. It takes a few big gulps to get every last drop of your cum down, but when she opens up again it's all gone."
            else:
                "Once you've had a good long look at your work [the_girl.name] leans over to the side and lets your cum dribble out slowly onto the ground. She straightens up and wipes her lips with the back of her hand."
            $ the_girl.call_cum_mouth()
            
        "Cum down her throat.":
            mc.name "Fuck, here I come!"
            "You use your hand on the back of [the_girl.name]'s head to pull her close, pushing your cock as deep down her throat as you can manage. You grunt and twitch as you start to empty your balls right into her stomach."
            if the_girl.sluttiness > 90:
                "[the_girl.name] looks up at you and stares into your eyes as you climax. She tightens and relaxes her throat, as if to draw out every last drop of semen from you."
                "Whn you're completely finished she pulls off slowly, kissing the tip before leaning back."
                $ the_girl.call_cum_mouth()
            elif the_girl.sluttiness > 60:
                "[the_girl.name] closes her eyes and holds still as you climax. You feel her throat spasm a few times as she struggles to keep your cock in place."
                "When you're finished she pulls off quickly, gasping for air. It takes a few seconds for her to regain her composure."
                $ the_girl.call_cum_mouth()
            else:
                "[the_girl.name] closes her eyes and tries to hold still as you climax. Her throat spasms as soon as the first blast of sperm splashes across the back, and she pulls back suddenly."
                "With no other choice, you stroke yourself off onto her face as she coughs and gasps for breath."
                $ the_girl.call_cum_face()
    return
    
label transition_deepthroat_blowjob(the_girl, the_location, the_object, the_round):
    "You move your hand from the back of [the_girl.name]'s head and sigh contentedly."
    mc.name "Fuck that felt nice."
    "[the_girl.name] slides your cock out of her mouth and strokes it with one hand while she talks to you."
    the_girl.name "Mmm, glad you liked it. I think I'm going to have a sore throat in the morning after all that."
    "She smiles and kisses the tip of your dick, then slides it back into her mouth and starts to suck on it some more, paying more attention to the shaft now."
    return
                                    
label transition_default_deepthroat(the_girl, the_location, the_object, the_round):
    "[the_girl.name] gets ready in front of you, on her knees with her mouth open. You place a hand on the back of her head and pull her towards you, slidding your cock down her throat."
    "After giving her a second to get use to your size you start to guide her back and forth, keeping yourself buried nice and deep in her mouth."
    return