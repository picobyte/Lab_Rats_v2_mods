init: 
    python:
        piledriver = Position("Piledriver",80,"stand2","Lay","Vagina","Vaginal",15,20,[],"intro_piledriver",["scene_piledriver_1","scene_piledriver_2"],"outro_piledriver","transition_default_piledriver")
        list_of_positions.append(piledriver)
        
init 1:
    python:
        piledriver.link_positions(missionary,"transition_piledriver_missionary")
    
label intro_piledriver(the_girl, the_location, the_object, the_round):
    mc.name "[the_girl.name], I want you to lie down for me."
    "[the_girl.name] nods, glancing briefly at the bulge in your pants. She gets onto the [the_object.name] and waits for you."
    the_girl.name "How's this?"
    "You get your hard cock out and kneel down in front of her. She yelps in suprise when you grab her ankles and bring them up and over her waist."
    mc.name "There we go, this will be even better."
    "You rub the tip of your cock against her clit a few times, then press forward and slide yourself inside of her."
    $the_girl.call_sex_response()
    return
    
label scene_piledriver_1(the_girl, the_location, the_object, the_round):
    "You hold onto [the_girl.name]'s ankles and lean into her, using the position to push yourself nice and deep inside of her."
    the_girl.name "Oh... Fuck... Ah..."
    mc.name "Does that feel good?"
    if the_girl.effective_sluttiness > 100:
        "All [the_girl.name] can do is nod and moan loudly in response. You do your best to drive your cock all the way to it's base, fitting every last inch into [the_girl.name]'s cunt."
    else:
        the_girl.name "It's certainly... Ah... Deep... Wow..."
        "She bites her lip and moans softly. You do your best to drive your cock all the way to it's base, fitting every last inch into [the_girl.name]'s cunt."
    return
    
label scene_piledriver_2(the_girl, the_location, the_object, the_round):
    "You settle into a steady rhythm pumping in and out of [the_girl.name]'s pussy. Having her legs bent over lets you get deeper than you normally can."
    if the_girl.outfit.tits_available():
        "You reach down with one hand and fondle [the_girl.name]'s tits, squeezing them and pinching her nipples."
        the_girl.name "Ah... That feels so strange..."
        mc.name "Do you like it?"
        "[the_girl.name] nods and moans in response. You fuck her a little faster."
    else:
        "You reach down with one hand and run it over [the_girl.name]'s tits over her clothes."
        mc.name "Wish I could get a better look at these girls."
        the_girl.name "Then you'd have to stop fucking me though..."
        "You fuck her a little faster and listen to her moan while you consider your dilemma."
    return
    
label outro_piledriver(the_girl, the_location, the_object, the_round):
    "[the_girl.name]'s pussy is warm, tight and wet as you pump in and out of it, pulling you closer and closer to climaxing with each thrust. You finally can't take any more and feel your orgasm approaching quickly."
    mc.name "Fuck me, I'm going to cum!"
    menu:
        "Cum inside of her.":
            if the_girl.sluttiness > 120:
                the_girl.name "Come on, dump it right inside of me!"
                "You had no intention of stopping either way, but hearing her ask for it makes you cum even harder. You gasp and push yourself as deep as you can, draining your balls into [the_girl.name]'s cunt."
                the_girl.name "Mmmm, it's so nice and warm..."
                
            else:
                the_girl.name "Wait, make sure to pull out!"
                "It's a little late for that now. You gasp and push yourself as deep as you can, draining your balls into [the_girl.name]'s cunt."
                the_girl.name "Well... Fuck... Good thing I'm on the pill I guess."
            "You take a moment to catch your breath, then sit back and pull your cock out of [the_girl.name]. You keep her on her back for a few more seconds, enjoying the way the position keeps your semen inside of her."
            
        "Cum on her face.":
            "You pull your cock out at the last minute, stroking it off with one hand as you point it towards [the_girl.name]'s face."
            if the_girl.sluttiness > 80:
                "[the_girl.name] sticks out her tongue and stares into your eyes as you climax. You spray your load onto her face, splattering some over her tongue and sending some right into her mouth."
                "She closes her mouth and swallows quickly, then bites her lip and smiles at you."
            else:
                "[the_girl.name] closes her eyes and waits for you to climax. You spray your load over her face and dribble a few drops of sperm onto her chest."
            "You sit back and let [the_girl.name]'s legs down. You enjoy the sight of her covered in your semen when she looks at you."
    return
    
label transition_piledriver_missionary(the_girl, the_location, the_object, the_round):
    "You slide back and let [the_girl.name] lower her legs. You go back to fucking her missionary style."
    the_girl.name "Fuck, you really stretched me out like that..."
    return
    
label transition_default_piledriver(the_girl, the_location, the_object, the_round):
    "You put [the_girl.name] on her back, then lift her legs up and bend her over at the waist. You kneel over her, lining your hard cock up with her tight pussy."
    mc.name "Ready?"
    "[the_girl.name] nods, and you slip yourself deep, deep inside of her."
    return