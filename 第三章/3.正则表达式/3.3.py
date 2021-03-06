class Pattern:

    def bracket(self, outer_precedence):
        if self.precedence() < outer_precedence:
            return "(' + to_s + ')"
        else:
            return self.to_s()

    def inspect(self):
        return '/{}/'.format(self)

    def matches(self, string):
        return self.to_nfa_design().accepts(string)


class Empty(Pattern):

    def to_s(self):
        return ''

    def precedence(self):
        return 3

    def to_nfa_design(self):
        start_state = object()
        accept_states = [start_state]
        rulebook = NFARulebook([])

        return NFADesign(start_state, accept_states, rulebook)


class Literal(Pattern):

    def __init__(self, character):
        self.character = character

    def to_s(self):
        return self.character

    def precedence(self):
        return 3

    def to_nfa_design(self):
        start_state = object()
        accept_state = object()
        rule = FARule(start_state, self.character, accept_state)
        rulebook = NFARulebook([rule])

        return NFADesign(start_state, [accept_state], rulebook)


class Concatenate(Pattern):

    def __init__(self, first, second):
        self.first = first
        self.second = second

    def to_s(self):
        lis = []
        for pattern in [self.first, self.second]:
            lis + list(map(pattern.bracket, pattern.precedence()))
        return ''.join(lis)

    def precedence(self):
        return 1

    def to_nfa_design(self):
        first_nfa_design = self.first.to_nfa_design()
        second_nfa_design = self.second.to_nfa_design()

        start_state = first_nfa_design.start_state
        accept_states = second_nfa_design.accept_states

        rules = first_nfa_design.rulebook.rules + second_nfa_design.rulebook.rules
        extra_rules = [FARule(state, None, second_nfa_design.start_state)
                       for state in first_nfa_design.accept_states]
        rulebook = NFARulebook(rules + extra_rules)

        return NFADesign(start_state, accept_states, rulebook)


class Choose(Pattern):

    def __init__(self, first, second):
        self.first = first
        self.second = second

    def to_s(self):
        lis = []
        for pattern in [self.first, self.second]:
            lis + list(map(pattern.bracket, pattern.precedence()))
        return '|'.join(lis)

    def precedence(self):
        return 0

    def to_nfa_design(self):
        first_nfa_design = self.first.to_nfa_design()
        second_nfa_design = self.second.to_nfa_design()

        start_state = object()
        accept_states = first_nfa_design.accept_states + second_nfa_design.accept_states
        rules = first_nfa_design.rulebook.rules + second_nfa_design.rulebook.rules
        extra_rules = [FARule(start_state, None, nfa_design.start_state)
                       for nfa_design in [first_nfa_design, second_nfa_design]]
        rulebook = NFARulebook(rules + extra_rules)

        return NFADesign(start_state, accept_states, rulebook)


class Repeat(Pattern):

    def __init__(self, pattern):
        self.pattern = pattern

    def to_s(self):
        self.pattern.bracket(self.precedence()) + '*'

    def precedence(self):
        return 2

    def to_nfa_design(self):
        pattern_nfa_design = self.pattern.to_nfa_design()

        start_state = object()
        accept_states = pattern_nfa_design.accept_states + [start_state]
        rules = pattern_nfa_design.rulebook.rules
        extra_rules = [FARule(accept_state, None, pattern_nfa_design.start_state)
                       for accept_state in pattern_nfa_design.accept_states] + \
                      [FARule(start_state, None, pattern_nfa_design.start_state)]
        rulebook = NFARulebook(rules + extra_rules)

        return NFADesign(start_state, accept_states, rulebook)
