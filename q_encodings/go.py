# Anne Merel de Jong, 01.01.2025, St Gallen (CH)
import math
from utils.gates import GatesGen as ggen
from utils.variables_dispatcher import VarDispatcher as vd

"""
rules to encode : 
1. Turn alternation 
2. Placement rules (stones only placed on empty itnersections )
3. Capturing stones 
4. Ko rule (no repeating the previous board state) <-- avoid infinite loops
"""


class GoQBF:
    """Class to encode the game of Go as a QBF
    main components of the QBF encoding :
    1. Quantifier blocks : generates the variables used in the encoding
    2. Initial state : intial positions of black, white and empty stones
    3. Transition functions : rules for how the game can change from one
    time step to the next (need to be seperated for black and white)
    4. Goal state : condition that must be met for a player to win the game
    5. Restrictred moves : restrict the moves to be only legal according to the rules of the game
    6. Final gate : conjunction of the initial state, transition functions and goal state
    """

    def generate_quantifier_blocks(self):
        """Function that generates the quanitifier blocks (step1)
        Step-by-step breakdown :
        1. move variables
        2. position variables
        3. liberty variables
        4. state transition variables
        5. additional game-specific variables
        """

        # 1. move variables
        self.quantifier_blocks.append(["# Move variables: "])
        for i in range(self.parsed.depth):
            self.quantifier_blocks.append(self.move_variables[i])

        # 2. position variables (3 per position)
        self.quantifier_blocks.append(["# Position variables: "])
        for pos in range(self.num_positions):
            self.quantifier_blocks.append(
                [
                    "exists("
                    + ", ".join(str(x) for x in self.position_variables[pos])
                    + ")"
                ]
            )

        # Liberty variables (empty adjacent positions) for each position:
        self.quantifier_blocks.append(["# Liberty variables: "])
        for pos in range(self.num_positions):
            self.quantifier_blocks.append(
                [
                    "exists("
                    + ", ".join(str(x) for x in self.liberty_variables[pos])
                    + ")"
                ]
            )

        # State transition variables:
        self.quantifier_blocks.append(["# State transitions: "])
        self.encode_variables(self.num_positions, 1, self.quantifier_blocks)

        if self.parsed.args.debug == 1:
            print("Quantifier blocks: ", self.quantifier_blocks)

    def encode_liberties(self):
        pass

    def encode_caputure_rules(self):
        pass

    def __init__(self, parsed):
        self.parsed = parsed
        self.encoding_variables = vd()

        self.quantifier_block = []
        self.encoding = []
        self.transition_step_output_gates = []
        self.final_output_gate = 0

        self.board_size = parsed.board_size
        self.num_positions = self.board_size**2
        self.num_turns = parsed.depth
        self.num_position_variables = self.num_positions * self.num_turns * 2

        self.num_position_variables = math.ceil(math.log2(self.num_positions))

        # 3 per position : empty, black, white
        self.position_states = {"empty": [], "white": [], "black": []}
        self.position_states["empty"] = self.encode_variables(
            self.num_turns, self.num_positions
        )
        self.position_states["white"] = self.encode_variables(
            self.num_turns, self.num_positions
        )
        self.position_states["black"] = self.encode_variables(
            self.num_turns, self.num_positions
        )

        # track liberties (empty adjacent positions) -> maximum of 4 per position
        self.liberty_variables = self.encode_variables(
            self.num_turns, self.num_positions
        )

        # update functions
        self.encode_liberties()
        self.encode_caputure_rules()

        # Move variables (one per move)
        self.move_variables = self.encode_variables(self.num_position_variables, 1)

        # Will be filled in the generate_quantifier_blocks function
        self.quantifier_blocks = []

        if parsed.args.debug == 1:
            print("Position variables: ", self.position_states)
            print("Liberty variables: ", self.liberty_variables)
            print("Move variables: ", self.move_variables)

    def encode_variables(self, _range, _number_vars, add_to=None):
        "Helper function to encode a function"
        if add_to is None:
            tmp = []
            for _ in range(_range):
                tmp.append(self.encoding_variables.get_vars(_number_vars))

            return tmp

        for _ in range(_range):
            add_to.append(self.encoding_variables.get_vars(_number_vars))

        return None

    def print_encoding_tofile(self, file_path):
        """Function to print the encoding to a file"""
        with open(file_path, "w") as f:
            for gate in self.quantifier_block:
                f.write(" ".join(gate) + "\n")
            f.write(f"output({self.final_output_gate})\n")
            for gate in self.encoding:
                f.write(" ".join(map(str, gate)) + "\n")


parsed = {
    "board_size": 3,
    "depth": 3,
    "initial_black_positions": [0],
    "initial_white_positions": [],
    "goal_positions": [0],
}
go_qbf = GoQBF(parsed)
go_qbf.print_encoding_tofile("go_game.qbf")
