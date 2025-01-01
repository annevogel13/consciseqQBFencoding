# Anne Merel de Jong, 01.01.2025, St Gallen (CH)
import math
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.gates import GatesGen as ggen
from utils.variables_dispatcher import VarDispatcher as vd

"""
rules to encode : 
1. Turn alternation 
2. Placement rules (stones only placed on empty itnersections )
3. Capturing stones 
4. Ko rule (no repeating the previous board state) <-- avoid infinite loops

!! can a encoding file have both blackwins and whitewins ? 
"""
#TODO make a logical order for the function in the class GoQBF
#TODO check if it is possible to regroup attributes of the class GoQBF, grouping them in seperate objects 

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

    def at_most_one_formula(self, variables):
        """
        Encodes an "At Most One" constraint for the given list of variables.
        Ensures that no two variables in the list can be true simultaneously.

        :param variables: List of variables for which the constraint is applied.
        """
        for i, var_i in enumerate(variables):
            for var_j in variables[i + 1 :]:
                # Add a clause ensuring that var_i and var_j cannot both be true
                self.gates_generator.and_gate([-var_i, -var_j])

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

    def get_adjacent_positions(self, pos):
        """
        Returns the adjacent positions for a given position on the board.
        Assumes a square grid board.
        """
        board_size = int(math.sqrt(self.num_positions))
        row, col = divmod(pos, board_size)
        adjacent = []

        # Add valid adjacent positions
        if row > 0:
            adjacent.append(pos - board_size)  # Up
        if row < board_size - 1:
            adjacent.append(pos + board_size)  # Down
        if col > 0:
            adjacent.append(pos - 1)  # Left
        if col < board_size - 1:
            adjacent.append(pos + 1)  # Right

        return adjacent

    def encode_liberties(self):
        """
        Encodes liberties for each position at each turn.
        A position's liberty is true if any of its adjacent positions are empty.
        """
        for t in range(self.num_turns):
            for pos in range(self.num_positions):
                # Get adjacent positions for the current position
                adj_positions = self.get_adjacent_positions(pos)

                # Get the "empty" state variables for the adjacent positions at turn t
                adj_empty_vars = [
                    self.position_states["empty"][t][adj] for adj in adj_positions
                ]

                # Generate an OR gate for the adjacent empty variables
                # Liberty is true if any adjacent position is empty
                if adj_empty_vars:
                    liberty_var = self.liberty_variables[t][pos]
                    self.gates_generator.or_gate(adj_empty_vars + [liberty_var])

    #TODO add the t parameter 
    def encode_capture_rules(self, t):
        """
        Encodes capture rules for each position at each turn.
        A stone is captured if all its liberties are occupied by the opponent.
        """
        for t in range(self.num_turns - 1):  # Capture happens between consecutive turns
            for pos in range(self.num_positions):
                # Liberty variable for this position at turn t
                liberty_var = self.liberty_variables[t][pos]

                # Capture rule for White
                white_stone_var = self.position_states["white"][t][pos]
                white_empty_next = self.position_states["empty"][t + 1][pos]

                self.gates_generator.if_then_gate(
                    -white_stone_var,  # If there is a White stone
                    liberty_var,  # Then liberties must exist (or else it's captured)
                )

                self.gates_generator.if_then_gate(
                    -liberty_var,  # If no liberties exist
                    white_empty_next,  # Then the position becomes empty
                )

                # Capture rule for Black
                black_stone_var = self.position_states["black"][t][pos]
                black_empty_next = self.position_states["empty"][t + 1][pos]
                self.gates_generator.if_then_gate(
                    -black_stone_var,  # If there is a Black stone
                    liberty_var,  # Then liberties must exist (or else it's captured)
                )

                self.gates_generator.if_then_gate(
                    -liberty_var,  # If no liberties exist
                    black_empty_next,  # Then the position becomes empty
                )

    def generate_initial_state(self):
        """
        Encodes the initial state of the board based on the parsed input.
        - Black stones are placed at `parsed.initial_black_positions`.
        - White stones are placed at `parsed.initial_white_positions`.
        - All other positions are initially empty.
        """

        initial_clauses = []

        for pos in range(self.num_positions):
            if pos in self.parsed.initial_black_positions:
                # If position is in the initial Black positions
                black_var = self.position_states["black"][0][pos]
                initial_clauses.append(f"{black_var} 0")  # Set to Black

            elif pos in self.parsed.initial_white_positions:
                # If position is in the initial White positions
                white_var = self.position_states["white"][0][pos]
                initial_clauses.append(f"{white_var} 0")  # Set to White
            else:
                # Otherwise, the position is initially empty
                empty_var = self.position_states["empty"][0][pos]
                initial_clauses.append(f"{empty_var} 0")  # Set to Empty

            # Exactly-one constraints: ensure the position is in only one state
            self.at_most_one_formula(
                [
                    self.position_states["black"][0][pos],
                    self.position_states["white"][0][pos],
                    self.position_states["empty"][0][pos],
                ]
            )

        # Append all clauses to the encoding
        self.encoding.extend(initial_clauses)

    def encode_stone_placement(self, t):
        """
        Encodes the rule that stones can only be placed on empty positions.
        """
        for pos in range(self.num_positions):
            empty_curr = self.position_states["empty"][t][pos]
            black_next = self.position_states["black"][t + 1][pos]
            white_next = self.position_states["white"][t + 1][pos]

            # If the position is empty, it cannot become both Black and White
            self.gates_generator.if_then_gate(
                empty_curr,
                -(black_next + white_next),
            )

    def encode_state_retention(self, t):
        """
        Encodes the rule that stones retain their state if not captured.
        """
        for color in ["black", "white"]:
            for pos in range(self.num_positions):
                curr_state = self.position_states[color][t][pos]
                next_state = self.position_states[color][t + 1][pos]

                # Retain stones of the current color
                self.gates_generator.if_then_gate(
                    curr_state,
                    next_state,
                )

    #TODO check if this is the most efficient way of checking this 
    def prevent_repeated_board_state(self, t):
        '''
        Ko rule: Prevents repeating the previous board state.
        '''
        for k in range(t + 1):  # Compare with all previous turns
            same_state_vars = []
            for pos in range(self.num_positions):
                # Compare Black stones
                black_t = self.position_states["black"][k][pos]
                black_t1 = self.position_states["black"][t + 1][pos]
               # same_state_vars.append(self.gates_generator.iff_gate(black_t, black_t1))

                # Compare White stones
                white_t = self.position_states["white"][k][pos]
                white_t1 = self.position_states["white"][t + 1][pos]
               # same_state_vars.append(self.gates_generator.iff_gate(white_t, white_t1))

                # Compare Empty positions
                empty_t = self.position_states["empty"][k][pos]
                empty_t1 = self.position_states["empty"][t + 1][pos]
              #  same_state_vars.append(self.gates_generator.iff_gate(empty_t, empty_t1))

            # Combine all "same state" conditions for this comparison into a single gate
            same_state_gate = self.encoding_variables.get_vars(1)[0]
            self.gates_generator.and_gate(same_state_vars + [same_state_gate])

            # Prevent the next state from matching this previous state
            #self.gates_generator.not_gate(same_state_gate)


    def generate_transition_rules(self):
        """
        Encodes the rules governing state transitions between turns.
        This function calls individual rule encoding functions for:
        - Stone placement
        - Capture rules
        - State retention
        - Ko Rule (prevent repeated board state)
        """
        for t in range(self.num_turns - 1):
            self.encode_stone_placement(t)
            self.encode_capture_rules(t)
            self.encode_state_retention(t)
            self.prevent_repeated_board_state(t)

    def generate_goal_state(self):
        """
        Encodes the goal state based on the parsed input.
        - If the goal depends on `#blackwins`, encode multiple conditions for Black to win.
        - If the goal depends on `#whitewins`, encode multiple conditions for White to win.
        """

        # Determine which win condition to use
        if hasattr(self.parsed, "blackwins"):
            win_conditions = self.parsed.blackwins
            state = "black"
        elif hasattr(self.parsed, "whitewins"):
            win_conditions = self.parsed.whitewins
            state = "white"
        else:
            raise ValueError(
                "Goal condition not defined: Add either `#blackwins` or `#whitewins`."
            )

        # Process each win condition and store gates for later combination
        self.goal_output_gates = []
        for goal_positions in win_conditions:
            # Retrieve variables representing the positions in the goal
            win_vars = [
                self.position_states[state][-1][self.parsed.positions.index(pos)]
                for pos in goal_positions
            ]

            # Create an AND gate for the current win condition
            goal_gate = self.encoding_variables.get_vars(1)[0]
            self.gates_generator.and_gate(win_vars + [goal_gate])
            self.goal_output_gates.append(goal_gate)

    def generate_final_gate(self):
        """
        Combines all goal gates into a single final output gate.
        - Uses OR logic to combine the gates generated by `generate_goal_state`.
        """
        if not hasattr(self, "goal_output_gates") or not self.goal_output_gates:
            raise ValueError(
                "No goal conditions have been generated. Call `generate_goal_state` first."
            )

        # Combine all goal gates into a single final output gate
        self.final_output_gate = self.encoding_variables.get_vars(1)[0]
        self.gates_generator.or_gate(self.goal_output_gates + [self.final_output_gate])

    def __init__(self, parsed):
        self.parsed = parsed
        self.encoding_variables = vd()

        self.quantifier_block = []
        self.encoding = []
        self.transition_step_output_gates = []
        self.final_output_gate = 0
        # Gates generator
        self.gates_generator = ggen(self.encoding_variables, self.encoding)

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

        self.captured_states = {
            "white": self.encode_variables(self.num_turns, self.num_positions),
            "black": self.encode_variables(self.num_turns, self.num_positions),
        }

        # track liberties (empty adjacent positions) -> maximum of 4 per position
        self.liberty_variables = self.encode_variables(
            self.num_turns, self.num_positions
        )

        # update functions
        self.encode_liberties()
        #self.encode_capture_rules()

        # Move variables (one per move)
        self.move_variables = self.encode_variables(self.num_position_variables, 1)

        # Will be filled in the generate_quantifier_blocks function
        self.quantifier_blocks = []

        # Generate encoding components
        self.generate_initial_state()
        self.generate_transition_rules()
        self.generate_goal_state()

        # Combine all components into the final gate
        self.generate_final_gate()

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


class ParsedTmp:
    """Class to store the parsed input for the GoQBF class"""

    def __init__(
        self,
        board_size,
        depth,
        initial_black_positions,
        initial_white_positions,
        goal_positions,
    ):
        self.board_size = board_size
        self.depth = depth
        self.initial_black_positions = initial_black_positions
        self.initial_white_positions = initial_white_positions
        self.goal_positions = goal_positions


_parsed = ParsedTmp(
    board_size=3,
    depth=3,
    initial_black_positions=[0],
    initial_white_positions=[],
    goal_positions=[0],
)

go_qbf = GoQBF(_parsed)
go_qbf.print_encoding_tofile("go_game.qbf")
