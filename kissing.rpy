init: 
    python:
        kissing = Position("Kissing",10,"stand2","Stand","None","Foreplay",5,5,[],"intro_kissing",["scene_kissing_1","scene_kissing_2"],"outro_kissing","transition_default_kissing")
        list_of_positions.append(kissing)
        
init 1: 
    python:
        kissing.link_positions(blowjob,"transition_kissing_blowjob")
    
label intro_kissing(the_girl, the_location, the_object, the_round):
    "You put your arm around [the_girl.name]'s waist and pull her close. Her eyes close as you lean in and press your lips against hers."
    "After a brief moment her arms wrap your torso in return. She pulls you close and presses against you."
    return
    
label scene_kissing_1(the_girl, the_location, the_object, the_round):
    #"You lock smoochers, gently kissing her."
    "You run your hands over [the_girl.name], feeling her back and hips as you kiss. Her tongue darts out to meet yours ocasionally, dancing playfully with yours."
    if the_girl.arousal > 40:
        "[the_girl.name] grinds her hips up against yours and moans softly while you make out."
    else:
        "Neither of you make a sound for a few moments as you make out, eyes closed and holding each other close."
    return
    
label scene_kissing_2(the_girl, the_location, the_object, the_round):
    #"You boop snoots, tenderly staring into her eyes. She holds you close, kissing you on the neck."
    #"Your snoots boop furiously, the sound echoing around the room."
    "You and [the_girl.name] make out for a long moment before she breaks the kiss and looks deep into your eyes"
    $the_girl.call_sex_response() #TODO: Make a non-sex happy response, for kissing, fondling, etc.
    if the_girl.arousal > 40:
        "She wraps her hand around the back of your head and pulls you close again. Her lips part and her tongue meets your as she kisses you passionately."
    else:
        "She closes her eyes again and leans in close, returning your kisses with just as much enthusiasm."
    return
    
label outro_kissing(the_girl, the_location, the_object, the_round):
    #"You part, snoots seperating slowly as you sare into her eyes. She whispers gently into your ear."
    #"Girl" "Oh god, my snoot. You booped me crazy."
    "[the_girl.name]'s tongue feels like satin against your lips, it's touch sends shivers up and down your spine."
    if the_girl.arousal > 100:
        "Watching her cum has gotten you more excited than you thought you would be. You're grinding your hips against hers now, rubbing your erection against her through your pants."
    elif the_girl.arousal > 40:
        "Her soft moans and eager movement make you even more excited. You're grinding your own hips against hers now, rubbing your erection against her through your pants."
    else:
        "You're grinding your own hips against hers now, rubbing your erection against her through your pants."
    "You finally let out a low moan and hold [the_girl.name] close. A shiver runs up your spine as your climax, shooting your load out into your underwear."
    "It takes a moment for you to recover from your orgasm. Once you're able to you step back and smooth out your shirt, the crotch of your pants uncomfortably wet now."
    return
    
label transition_kissing_blowjob(the_girl, the_location, the_object, the_round):
    #"You part smoochers, and she leans close to you."
    #"You" "I've got something else for you to boop."
    #"You wait, and soon she's on her knees, booping your second snoot."
    #"Transition from kissing to blowjob."
    "You break the kiss between you and [the_girl.name] and look into her eyes, idly stroking her hair with a hand."
    "[mc.name]" "[the_girl.name], how about you take care of this for me?"
    "You reach down with your other hand and unzip your pants. You pull your underwear down and let your hard cock spring free."
    if the_girl.sluttiness > 80:
        "[the_girl.name] stares down at your cock hungrily, licking her lips."
        the_girl.name "Mmm, let me at it."
        "[the_girl.name] drops down to her knees quickly, shuffling right up next to you and resting your hard shaft on her cheek."
    else:
        "[the_girl.name] looks down at your erection then back up at you. She smiles and nods, dropping slowly to her knees while her hands run down your sides."
        the_girl.name "How's this?"
    "[the_girl.name] leans in close and kisses the tip of your dick gently, swirling her tongue around the tip."
    return
    
label transition_default_kissing(the_girl, the_location, the_object, the_round):
    "You take [the_girl.name] in your arms and hold her close. She leans against you as you kiss her, breasts pressed up against your chest."
    "It's not long before the two of you are making out, arms clasped tightly around each other."
    return