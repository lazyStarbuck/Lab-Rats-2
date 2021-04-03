init -2 python:
    class Role(renpy.store.object): #Roles are assigned to special people. They have a list of actions that can be taken when you talk to the person and acts as a flag for special dialogue options.
        def __init__(self, role_name, actions, hidden = False, on_turn = None, on_move = None, on_day = None):
            self.role_name = role_name
            self.actions = actions # A list of actions that can be taken. These actions are shown when you talk to a person with this role if their requirement is met.
            # At some point we may want a seperate list of role actions that are available when you text someone.
            self.hidden = hidden #A hidden role is not shown on the "Roles" list
            self.on_turn = on_turn #A function that is run each turn on every person with this Role.
            self.on_move = on_move #A function that is run each move phase on every person with this Role.
            self.on_day = on_day

            self.linked_roles = [] #A list of other roles. If this role is removed, all linked roles are removed as well.

        def __cmp__(self,other):
            matches = True
            if not self.role_name == other.role_name:
                matches = False

            for an_action in self.actions:
                if not an_action in other.actions:
                    matches = False
                    break

            for an_action in other.actions:
                if not an_action in self.actions:
                    matches = False
                    break

            if not self.on_turn == other.on_turn:
                matches = False

            if not self.on_move == other.on_move:
                matches = False

            if not self.on_day == other.on_day:
                matches = False

            if matches:
                return 0
            else:
                if other is None:
                    return 1
                elif self.__hash__() < other.__hash__(): #Use hash values to break ties.
                    return -1
                else:
                    return 1

        def run_turn(self, the_person):
            if self.on_turn is not None:
                self.on_turn(the_person)

        def run_move(self, the_person):
            if self.on_move is not None:
                self.on_move(the_person)

        def run_day(self, the_person):
            if self.on_day is not None:
                self.on_day(the_person)

        def link_role(self, the_role):
            if the_role not in self.linked_roles:
                self.linked_roles.append(the_role)
