init -26 python:

    ##Serum traits that can be added to a serum design##
    default_serum_traits = {
        "improved serum production": {
            "name": "Improved Serum Production",
            "desc": "General improvements to the basic serum design. Improves suggestion gain and value.",
            "requires": set(),
            "research done": 0,
            "research required": 200,
            "trait": {
                "research required": 50,
                "production": 10,
                "value": 20
            },
            "antagonists": set(),
            "effect": {
                "suggest": 10
            }
        },
        "basic medical serum production": {
            "name": "Basic Medical Application",
            "desc": "Adding a few basic medical applications significantly increases the value of this serum.",
            "requires": set(),
            "research done": 0,
            "research required": 200,
            "trait": {
                "research required": 50,
                "production": 10,
                "value": 40
            },
            "antagonists": set(),
            "effect": {}
        },
        "obedience enhancer effect": {
            "name": "Obedience Enhancer",
            "desc": "A blend of off the shelf pharmaceuticals will make the recipient more receptive to direct orders.",
            "requires": set(["improved serum production","basic medical serum production"]),
            "research done": 0,
            "research required": 300,
            "trait": {
                "research required": 75,
                "production": 5,
                "value": 5
            },
            "antagonists": set(),
            "effect": {
                "obedience": 10
            }
        },
        "improved duration effect": {
            "name": "Improved Reagent Purification",
            "desc": "By carefully purifying the starting materials the length of time a serum remains active can be greatly increased.",
            "requires": set(["improved serum production","basic medical serum production"]),
            "research done": 0,
            "research required": 350,
            "trait": {
                "research required": 75,
                "production": 15,
                "value": 10
            },
            "antagonists": set(),
            "effect": {
                "duration": 2
            }
        },
        "aphrodisiac effect": {
            "name": "Distilled Aprodisac",
            "desc": "Careful distilation can concentrate the active ingredient from common aprodisiacs, producing a sudden spike in sluttiness when consumed.",
            "requires": set(["improved duration effect","basic medical serum production"]),
            "research done": 0,
            "research required": 250,
            "trait": {
                "research required": 60,
                "production": 10,
                "value": 25
            },
            "antagonists": set(),
            "effect": {
                "sluttiness": 15
            }
        },
        "advanced serum production": {
            "name": "Advanced Serum Production",
            "desc": "Advanced improvements to the basic serum design. Greatly improves suggestion gain and value.",
            "requires": set(["improved serum production","basic medical serum production"]),
            "research done": 0,
            "research required": 800,
            "trait": {
                "research required": 200,
                "production": 25,
                "value": 50
            },
            "antagonists": set(),
            "effect": {
                "suggest": 30
            }
        },
        "low volatility reagents effect": {
            "name": "Low Volatility Reagents",
            "desc": "Carefully sourced and stored reagents will greatly prolong the effects of a serum, at an increased production cost.",
            "requires": set(["advanced serum production","improved duration effect"]),
            "research done": 0,
            "research required": 600,
            "trait": {
                "research required": 150,
                "production": 40,
                "value": 20
            },
            "antagonists": set(),
            "effect": {
                "duration": 5
            }
        },
        "futuristic serum production": {
            "name": "Futuristic Serum Production",
            "desc": "Space age technology makes the serum incredibly valuable and maxes out suggestion gain.",
            "requires": set(["advanced serum production"]),
            "research done": 0,
            "research required": 3000,
            "trait": {
                "research required": 500,
                "production": 50,
                "value": 200
            },
            "antagonists": set(),
            "effect": {
                "suggest": 100
            }
        },
        "growing breast effect": {
            "name": "Breast Enhancement",
            "desc": "Grows breasts overnight. Has a 10% chance of increasing a girls breast size by one step with each time unit.",
            "requires": set(["advanced serum production","basic medical serum production"]),
            "research done": 0,
            "research required": 500,
            "trait": {
                "research required": 125,
                "production": 20,
                "value": 50
            },
            "antagonists": set(["shrinking breast effect"]),
            "effect": {
                "cupsize": 1
            }
        },
        "shrinking breast effect": {
            "name": "Breast Reduction",
            "desc": "Shrinks breasts overnight. Has a 10% chance of decreasing a girls breast size by one step with each time unit.",
            "requires": set(["advanced serum production","basic medical serum production"]),
            "research done": 0,
            "research required": 500,
            "trait": {
                "research required": 125,
                "production": 20,
                "value": 50
            },
            "antagonists": set(["growing breast effect"]),
            "effect": {
                "cupsize": -1
            }
        },
        "focus enhancement production": {
            "name": "Medical Amphetamines",
            "desc": "The inclusion of low doses of amphetamines help the user focus intently for long periods of time.",
            "requires": set(["advanced serum production","basic medical serum production"]),
            "research done": 0,
            "research required": 800,
            "trait": {
                "research required": 150,
                "production": 20,
                "value": 30
            },
            "antagonists": set(),
            "effect": {
                "focus": 2
            }
        },
        "int enhancement production": {
            "name": "Quick Release Nootropics",
            "desc": "Nootropics enhance cognition and learning. These fast acting nootropics produce results almost instantly, but for a limited period of time.",
            "requires": set(["advanced serum production","basic medical serum production"]),
            "research done": 0,
            "research required": 800,
            "trait": {
                "research required": 150,
                "production": 20,
                "value": 30
            },
            "antagonists": set(),
            "effect": {
                "int": 2
            }
        },
        "cha enhancement production": {
            "name": "Stress Inhibitors",
            "desc": "By reducing the users natural stress response to social interactions they are able to express themselves more freely and effectively. Takes effect immediately, but lasts only for a limited time",
            "requires": set(["advanced serum production","basic medical serum production"]),
            "research done": 0,
            "research required": 800,
            "trait": {
                "research required": 150,
                "production": 20,
                "value": 30
            },
            "antagonists": set(),
            "effect": {
                "charisma": 2
            }
        },
        "happiness tick effect": {
            "name": "Slow Release Dopamine",
            "desc": "By slowly flooding the users dopamine receptors they can be put into a long lasting sense of bliss. Raises happiness by 5 each time unit, but users will become more carefree as time goes on, lowering obedience by 5.",
            "requires": set(["futuristic serum production","basic medical serum production"]),
            "research done": 0,
            "research required": 2500,
            "trait": {
                "research required": 100,
                "production": 20,
                "value": 100
            },
            "antagonists": set(),
            "effect": { # bliss
                "happiness": 2,
                "obedience": -2
            }
        }
    }

