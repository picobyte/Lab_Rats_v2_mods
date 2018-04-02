## This file holds the upgrades for your business, known as "policies".
## Policies have a:
## 1) Name, used when displaying the button for them/
## 2) A description, a text description of the effects the policy will have on your business.
## 3) A cost, a value in $$$ that purchasing the policy will cost.
## 4) A requirement, a function that is evaluated when checking to see if the player can purchase this policy.

init -1 python:

    class Policy(renpy.store.object): # An upgrade that can be purchased by the character for their business.
        def __init__(self,name,desc,requirement,cost):
            self.name = name #A short name for the policy.
            self.desc = desc #A text description of the policy.
            self.requirement = requirement #a function that is run to see if the PC can purchase this policy.
            self.cost = cost #Cost in dollars.

        def __cmp__(self,other): #
            if type(other) is Policy:
                if self.name == other.name and self.desc == other.desc and self.cost == other.cost:
                    return 0

            return -1 if self.__hash__() < other.__hash__() else 1 #Use hash values to break ties.

        def __hash__(self):
            return hash((self.name,self.desc,self.cost))


    #### UNIFORM POLICY SECTION ####
    def strict_uniform_policy_requirement(): #
        return True
        
    strict_uniform_policy = Policy(name = "Strict Corporate Uniforms",
        desc = "Requiring certain styles of attire in the business world is nothing new. Allows you to define a conservative uniform with a sluttiness requirement of 5 or less.",
        cost = 500,
        requirement = strict_uniform_policy_requirement)

    mc.business.available_policies.add(strict_uniform_policy)

    def relaxed_uniform_policy_requirement():
        return strict_uniform_policy in mc.business.active_policies

    relaxed_uniform_policy = Policy(name = "Relaxed Corporate Uniforms",
        desc = "Corporate dress code is broadened to include more casual apparel. Allows you to define a uniform with a sluttiness requirement of 15 or less.",
        cost = 1000,
        requirement = relaxed_uniform_policy_requirement)

    mc.business.available_policies.add(relaxed_uniform_policy)

    def casual_uniform_policy_requirement():
        return relaxed_uniform_policy in mc.business.active_policies

    casual_uniform_policy = Policy(name = "Casual Corporate Uniforms",
        desc = "Corporate dress code is further broadened, while the uniform policy is simultaneously refined to dictate more and more intimate details. Allows you to define a uniform with a sluttiness requirement of 25 or less.",
        cost = 2000,
        requirement = casual_uniform_policy_requirement)

    mc.business.available_policies.add(casual_uniform_policy)

    def reduced_coverage_uniform_policy_requirment():
        return casual_uniform_policy in mc.business.active_policies

    reduced_coverage_uniform_policy = Policy(name = "Reduced Coverage Corporate Uniforms",
        desc = "The term \"appropriate coverage\" in the employee manual is redefined to include bare bras or panties. Allows you to define a uniform with a sluttiness requirement of 40 or less.",
        cost = 5000,
        requirement = reduced_coverage_uniform_policy_requirment)

    mc.business.available_policies.add(reduced_coverage_uniform_policy)

    def minimal_coverage_uniform_policy_requirement():
        return reduced_coverage_uniform_policy in mc.business.active_policies

    minimal_coverage_uniform_policy = Policy(name = "Minimal Coverage Corporate Uniforms",
        desc = "Corporate dress code is broadened further. Uniforms must now only meet a \"minumum coverage\" requirement, generally nothing more than a set of bra and panties. Allows you to define a uniform with a sluttiness requirement of 60 or less.",
        cost = 10000,
        requirement = minimal_coverage_uniform_policy_requirement)

    mc.business.available_policies.add(minimal_coverage_uniform_policy)

    def corporate_enforced_nudity_requirement():
        return minimal_coverage_uniform_policy in mc.business.active_policies

    corporate_enforced_nudity_policy = Policy(name = "Corporate Enforced Nudity",
        desc = "Corporate dress code is removed in favour of a \"need to wear\" system. All clothing items that are deemed non-essential are subject to employer approval. Conveniently, all clothing is deemed non-essential. Allows you to define a uniform with a sluttiness requirement of 80 or less.",
        cost = 25000,
        requirement = corporate_enforced_nudity_requirement)

    mc.business.available_policies.add(corporate_enforced_nudity_policy)

    def maximal_arousal_uniform_policy_requirement():
        return corporate_enforced_nudity_policy in mc.business.active_policies

    maximal_arousal_uniform_policy = Policy(name = "Maximal Arousal Uniform Policy",
        desc = "Visually stimulating uniforms are deemed essential to the workplace. Any and all clothing items and accessories are allowed, uniform sluttiness requirement is uncapped.",
        cost = 50000,
        requirement = maximal_arousal_uniform_policy_requirement)

    mc.business.available_policies.add(maximal_arousal_uniform_policy)

    def male_focused_marketing_requirement():
        return strict_uniform_policy in mc.business.active_policies

    male_focused_marketing_policy = Policy(name = "Male Focused Modeling",
        desc = "The adage \"Sex Sells\" is especially true when selling your serum to men. Serum will sell for %1 per point of sluttiness of your marketing uniform.",
        cost = 500,
        requirement = male_focused_marketing_requirement)

    mc.business.available_policies.add(male_focused_marketing_policy)



    #### SERUM TESTING POLICY SECTION ####
    
    def mandatory_serum_testing_policy_requirement():
        return True
        
    mandatory_serum_testing_policy = Policy(name = "Mandatory Serum Testing",
        desc = "Modification of the standard employee contract will make serum testing of all finished designs mandatory upon request.",
        cost = 2000,
        requirement = mandatory_serum_testing_policy_requirement)

    mc.business.available_policies.add(mandatory_serum_testing_policy)

    def daily_serum_dosage_policy_requirement():
        return mandatory_serum_testing_policy in mc.business.active_policies

    daily_serum_dosage_policy = Policy(name = "Daily Serum Dosage",
        desc = "Mandatory serum testing is expanded into a full scale daily dosage program. Each employee will recieve a dose of the selected serum for their department, if one is currently in the stockpile.",
        cost = 5000,
        requirement = daily_serum_dosage_policy_requirement)

    mc.business.available_policies.add(daily_serum_dosage_policy)

    #### RECRUITMENT IMPROVEMENT POLICIES ####
    
    def recruitment_batch_one_requirement():
        return True
        
    recruitment_batch_one_policy = Policy(name = "Recruitment Batch Size Improvement One",
        desc = "More efficent hiring software will allow you to interview up to review up to four resumes in a single recruitment batch.",
        cost = 200,
        requirement = recruitment_batch_one_requirement)

    mc.business.available_policies.add(recruitment_batch_one_policy)

    def recruitment_batch_two_requirement():
        return recruitment_batch_one_policy in mc.business.active_policies

    recruitment_batch_two_policy = Policy(name = "Recruitment Batch Size Improvement Two",
        desc = "Further improvements in hiring software and protocols allows you to review up to six resumes in a single recruitment batch.",
        cost = 600,
        requirement = recruitment_batch_two_requirement)

    mc.business.available_policies.add(recruitment_batch_two_policy)

    def recruitment_batch_three_requirement():
        return recruitment_batch_two_policy in mc.business.active_policies

    recruitment_batch_three_policy = Policy(name = "Recruitment Batch Size Improvement Three",
        desc = "A complete suite of recruitment software lets you maximize the use of your time while reviewing resumes. Allows you to review ten resumes in a single recruitment batch.",
        cost = 1200,
        requirement = recruitment_batch_three_requirement)

    mc.business.available_policies.add(recruitment_batch_three_policy)

    def recruitment_skill_improvement_requirement():
        return True
        
    recruitment_skill_improvement_policy = Policy(name = "Recruitment Skill Improvement",
        desc = "Restricting your recruitment search to university and college graduates improves their skill across all disiplines. Raises all skill caps when hiring new employees by two.",
        cost = 800,
        requirement = recruitment_skill_improvement_requirement)

    mc.business.available_policies.add(recruitment_skill_improvement_policy)

    def recruitment_stat_improvement_requirement():
        return recruitment_skill_improvement_policy in mc.business.active_policies

    recruitment_stat_improvement_policy = Policy(name = "Recruitment Stat Improvment",
        desc = "A wide range of networking connections can put you in touch with the best and brightest in the industry. Raises all statistic caps when hiring new employees by two.",
        cost = 1500,
        requirement = recruitment_stat_improvement_requirement)

    mc.business.available_policies.add(recruitment_stat_improvement_policy)

    def recruitment_high_suggest_requirement():
        return True
    
    recruitment_suggest_improvment_policy = Policy(name = "High Suggestibility Recruits",
        desc = "You change your focus to hiring younger, more impressionable employees. New employees will all have a starting suggestibility of 10.",
        cost = 600,
        requirement = recruitment_high_suggest_requirement)

    mc.business.available_policies.add(recruitment_suggest_improvment_policy)

    def recruitment_obedience_improvement_requirement():
        return recruitment_suggest_improvment_policy in mc.business.active_policies

    recruitment_obedience_improvement_policy = Policy(name = "High Obedience Recruits",
        desc = "A highly regimented business appeals to some people. By improving your corporate image and stressing company stability new recruits will have a starting obedince 10 points higher than normal.",
        cost = 1000,
        requirement = recruitment_obedience_improvement_requirement)

    mc.business.available_policies.add(recruitment_obedience_improvement_policy)

    def recruitment_slut_improvement_requirement():
        return recruitment_obedience_improvement_policy in mc.business.active_policies

    recruitment_slut_improvement_policy = Policy(name = "High Sluttiness Recruites",
        desc = "Narrowing your resume search parameters to include previous experience at strip clubs, bars, and modeling agencies produces a batch of potential employees with a much higher initial slutiness value. Increases starting sluttiness by 20.",
        cost = 1200,
        requirement = recruitment_slut_improvement_requirement)

    mc.business.available_policies.add(recruitment_slut_improvement_policy)

    #TODO: Add a policy that improves the sex skills of your recruits.
        
            
    
