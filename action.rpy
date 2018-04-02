init -20 python:
    # Rooms have actions

    class Action(renpy.store.object): #Contains the information about actions that can be taken in a room. Dispayed when you are asked what you want to do somewhere.
        # Also used for crises, those are not related to any partiular room and are not displayed in a list. They are forced upon the player.
        def __init__(self,name,requirement,effect,args=None):
            self.name = name
            self.requirement = requirement #requirement should be a function that has already been defined. Yay functional programming!
            self.effect = effect
            self.args = args #stores any arguments that we want passed to the action or requirement when the action is created. Should be a list of variables.

        def __cmp__(self,other): ##This and __hash__ are defined so that I can use "if Action in List" and have it find identical actions that are different instances.
            if type(other) is Action:
                if self.name == other.name and self.requirement == other.requirement and self.effect == other.effect and self.args == other.args:
                    return 0

            return -1 if self.__hash__() < other.__hash__() else 1 #Use hash values to break ties.

        def __hash__(self):
            return hash((self.name,self.requirement,self.effect,self.args))

        def check_requirement(self): #Calls the function that was passed to the action when it was created. Currently can only use global variables, will change later to take arbitrary list.
            return self.requirement()

        def call_action(self): #Can only use global variables. args is a list of elements you want to include as arguments. None is default
            if self.args is None:
                renpy.call(self.effect)
            else:
                renpy.call(self.effect,self.args)
            renpy.return_statement()
