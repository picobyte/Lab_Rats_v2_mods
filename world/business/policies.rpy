init -40 python:
    ## This file holds the upgrades for your business, known as "policies".
    ## Policies have a:
    ## 1) Name, used when displaying the button for them/
    ## 2) A description, a text description of the effects the policy will have on your business.
    ## 3) A cost, a value in $$$ that purchasing the policy will cost.
    ## 4) A requirement, a function that is evaluated when checking to see if the player can purchase this policy.

    policies = {
        "Strict Corporate Uniforms": {
            "desc": "Requiring certain styles of attire in the business world is nothing new. " +
            "Allows you to define a conservative uniform with a sluttiness requirement of 5 or less.",
            "cost": 500, "req": set(), "max_outfits_to_change": 5
        },
        "Relaxed Corporate Uniforms": {
            "desc": "Corporate dress code is broadened to include more casual apparel. " +
            "Allows you to define a uniform with a sluttiness requirement of 15 or less.",
            "cost": 1000, "req": set(["Strict Corporate Uniforms"]), "max_outfits_to_change": 15
        },
        "Casual Corporate Uniforms": {
            "desc": "Corporate dress code is further broadened, while the uniform policy is simultaneously " +
            "refined to dictate more and more intimate details. Allows you to define a uniform with a sluttiness requirement of 25 or less.",
            "cost": 2000, "req": set(["Relaxed Corporate Uniforms"]), "max_outfits_to_change": 25
        },
        "Reduced Coverage Corporate Uniforms": {
            "desc": "The term \"appropriate coverage\" in the employee manual is redefined to include bare bras " +
            "or panties. Allows you to define a uniform with a sluttiness requirement of 40 or less.",
            "cost": 5000, "req": set(["Casual Corporate Uniforms"]), "max_outfits_to_change": 40
        },
        "Minimal Coverage Corporate Uniforms": {
            "desc": "Corporate dress code is broadened further. Uniforms must now only meet a \"minumum coverage\" requirement, " +
            "generally nothing more than a set of bra and panties. Allows you to define a uniform with a sluttiness requirement of 60 or less.",
            "cost": 10000, "req": set(["Reduced Coverage Corporate Uniforms"]), "max_outfits_to_change": 60
        },
        "Corporate Enforced Nudity": {
            "desc": "Corporate dress code is removed in favour of a \"need to wear\" system. All clothing items that are deemed " +
            "non-essential are subject to employer approval. Conveniently, all clothing is deemed non-essential. " +
            "Allows you to define a uniform with a sluttiness requirement of 80 or less.",
            "cost": 25000, "req": set(["Minimal Coverage Corporate Uniforms"]), "max_outfits_to_change": 80
        },
        "Maximal Arousal Uniform Policy": {
            "desc": "Visually stimulating uniforms are deemed essential to the workplace. Any and all clothing items " +
            "and accessories are allowed, uniform sluttiness requirement is uncapped.",
            "cost": 50000, "req": set(["Corporate Enforced Nudity"]), "max_outfits_to_change": 999 #ie. no limit at all.
        },
        "Male Focused Modeling": {
            "desc": "The adage \"Sex Sells\" is especially true when selling your serum to men. Serum will sell for %1 " +
            "per point of sluttiness of your marketing uniform.",
            "cost": 500, "req": set(["Strict Corporate Uniforms"])
        },

        #### SERUM TESTING POLICY SECTION ####
        "Mandatory Serum Testing": {
            "desc": "Modification of the standard employee contract will make serum testing of all finished designs mandatory upon request.",
            "cost": 2000, "req": set()
        },
        "Daily Serum Dosage": {
            "desc": "Mandatory serum testing is expanded into a full scale daily dosage program. Each employee will recieve " +
            "a dose of the selected serum for their department, if one is currently in the stockpile.",
            "cost": 5000, "req": set(["Mandatory Serum Testing"])
        },
        #### RECRUITMENT IMPROVEMENT POLICIES ####
        "Recruitment Batch Size Improvement One": {
            "desc": "More efficent hiring software will allow you to interview up to review up to four resumes in a single recruitment batch.",
            "cost": 200, "req": set()
        },
        "Recruitment Batch Size Improvement Two": {
            "desc": "Further improvements in hiring software and protocols allows you to review up to six resumes in a single recruitment batch.",
            "cost": 600, "req": set(["Recruitment Batch Size Improvement One"])
        },
        "Recruitment Batch Size Improvement Three": {
            "desc": "A complete suite of recruitment software lets you maximize the use of your time while reviewing resumes. " +
            "Allows you to review ten resumes in a single recruitment batch.",
            "cost": 1200, "req": set(["Recruitment Batch Size Improvement Two"])
        },

        "Recruitment Skill Improvement": {
            "desc": "Restricting your recruitment search to university and college graduates improves their skill across all disiplines. " +
            "Raises all skill caps when hiring new employees by two.",
            "cost": 800, "req": set(), "effect": {"Work Skills": 2}
        },
        "Recruitment Stat Improvment": {
            "desc": "A wide range of networking connections can put you in touch with the best and brightest in the industry. " +
            "Raises all statistic caps when hiring new employees by two.",
            "cost": 1500, "req": set(["Recruitment Skill Improvement"]), "effect": {"Main Stats": 2}
        },
        "High Suggestibility Recruits": {
            "desc": "You change your focus to hiring younger, more impressionable employees. New employees will all have a starting suggestibility of 10.",
            "cost": 600, "req": set(), "effect": {"suggest": 10}
        },
        "High Obedience Recruits": {
            "desc": "A highly regimented business appeals to some people. By improving your corporate image and stressing company " +
            "stability new recruits will have a starting obedince 10 points higher than normal.",
            "cost": 1000, "req": set(["High Suggestibility Recruits"]), "effect": {"obedience": 10}
        },
        "High Sluttiness Recruites": {
            "desc": "Narrowing your resume search parameters to include previous experience at strip clubs, bars, and modeling agencies " +
            "produces a batch of potential employees with a much higher initial slutiness value. Increases starting sluttiness by 20.",
            "cost": 1200, "req": set(["High Obedience Recruits"]), "effect": {"sluttiness": 20}
        },

        #### SEX SKILLS IMPROVEMENT POLICIES ####
        "Foreplay Skill Improvement": {
            "desc": "Investigate social connections of working employees to find potential employees that are hot and outgoing.",
            "cost": 1000, "req": set(), "effect": {"Foreplay": 2}
        },
        "Oral Skill Improvement": {
            "desc": "Require some of your working employees to scout, off duty, for potential recruits that are very proficient with their mouths.",
            "cost": 2000, "req": set(["Foreplay Skill Improvement", "Mandatory Serum Testing"]), "effect": {"Oral": 3}
        },
        "Vaginal Skill Improvement": {
            "desc": "Send your scouts to bars and sauna's to find employees that have a lot of sexual experience.",
            "cost": 5000, "req": set(["Oral Skill Improvement", "Daily Serum Dosage"]), "effect": {"Vaginal": 4}
        },
        "Anal Skill Improvement": {
            "desc": "Require your personel to work off-duty in the porn industry, to find recruits that will work for your business near the back door.",
            "cost": 10000, "req": set(["Vaginal Skill Improvement", "Daily Serum Dosage", "Corporate Enforced Nudity"]), "effect": {"Anal": 5}
        }
    }
