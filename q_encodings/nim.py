
from utils.gates import GatesGen as ggen
from utils.variables_dispatcher import VarDispatcher as vd

class Nim: 
    
    def print_gate_to_file(self, gate,file):
        pass 
    
    def print_encoding_to_file(self,filepath):
        pass
    
    def generate_quantifier_blocks(self):
        pass 
    
    def player_transition(self, timestep):
        pass 

    def generate_d_transitions(self):
        pass
    
    def generate_intial_gate(self):
        pass
    
    def generate_restricted_moves(self):
        pass
        
    def generate_final_gate(self):
        pass 
    
    def __init__(self, parsed):
        self.parsed = parsed
        self.encoding_variables = vd()
        self.quantifier_block = []
        self.dqdimacs_prefix = []
        self.encoding = []
        self.initial_output_gate = 0  # initial output gate can never be 0
        self.goal_output_gate = 0  # goal output gate can never be 0
        self.transition_step_output_gates = []
        self.transition_output_gate = 0  # Can never be 0
        self.restricted_black_gate = 0  # Can never be 0
        self.restricted_white_gate = 0  # Can never be 0
        self.final_output_gate = 0  # Can never be 0
        
        if parsed.num_available_moves == 1:
            self.num_move_variables = 1
        else:
            self.num_move_variables = math.ceil(math.log2(parsed.num_available_moves))
            
        self.move_variables = []
        for i in range(parsed.depth):
            self.move_variables.append(
                self.encoding_variables.get_vars(self.num_move_variables)
            )