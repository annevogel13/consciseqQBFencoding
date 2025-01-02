""" Anne Merel de Jong, 01.2025, St Gallen (CH)
"""

import math
from utils.gates import GatesGen as ggen
from utils.variables_dispatcher import VarDispatcher as vd

"""
rules to encode : 
1. Turn alternation 
2. Placement rules (stones only placed on empty itnersections )
3. Capturing stones 
4. Ko rule (no repeating the previous board state) <-- avoid infinite loops

!! can a encoding file have both blackwins and whitewins ? currently encoded only for black to win 

TODO make a logical order for the function in the class GoQBF
TODO check if it is possible to regroup attributes of the class GoQBF
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

    def validate_parsed_input(self):
        """
        Validates the parsed input to ensure correctness and consistency.
        Checks:
        - blackinitials and whiteinitials: No overlap, valid positions.
        - times: At least one time step and valid format.
        - blackturns: Valid times and correct alternation logic.
        - positions: No duplicates and valid format.
        - blackwins : Valid positions and no overlap.
        """

        # Check positions
        if hasattr(self.parsed, "positions"):
            if len(self.parsed.positions) != len(set(self.parsed.positions)):
                raise ValueError("Duplicate positions detected.")
        else:
            raise ValueError("Field 'positions' is missing.")

        # Check blackinitials and whiteinitials
        if hasattr(self.parsed, "blackinitials") and hasattr(
            self.parsed, "whiteinitials"
        ):
            black_initials = set(self.parsed.blackinitials)
            white_initials = set(self.parsed.whiteinitials)
            # the set intersection operator
            overlap = black_initials & white_initials
            if overlap:
                raise ValueError(
                    f"Overlap detected between blackinitials and whiteinitials: {overlap}"
                )

            invalid_black_initials = black_initials - set(self.parsed.positions)
            invalid_white_initials = white_initials - set(self.parsed.positions)
            if invalid_black_initials:
                raise ValueError(
                    f"Invalid blackinitials not in positions: {invalid_black_initials}"
                )
            if invalid_white_initials:
                raise ValueError(
                    f"Invalid whiteinitials not in positions: {invalid_white_initials}"
                )

        # Check times
        if hasattr(self.parsed, "times"):
            if not self.parsed.times:
                raise ValueError("No times provided.")
            if len(self.parsed.times) < 1:
                raise ValueError("At least one time step is required.")
        else:
            raise ValueError("Field 'times' is missing.")

        # Check blackturns
        if hasattr(self.parsed, "blackturns"):
            # - is the set operator for difference
            invalid_black_turns = set(self.parsed.blackturns) - set(self.parsed.times)
            if invalid_black_turns:
                raise ValueError(
                    f"Invalid blackturns not in times: {invalid_black_turns}"
                )
        else:
            raise ValueError("Field 'blackturns' is missing.")

        # Check if 'blackwins' exists
        if not hasattr(self.parsed, "blackwins"):
            raise ValueError("Field 'blackwins' is missing in the parsed input.")

        # Validate each win condition
        for win_condition in self.parsed.blackwins:
            invalid_positions = set(win_condition) - set(self.parsed.positions)
            if invalid_positions:
                raise ValueError(f"Invalid positions in blackwins: {invalid_positions}")

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
        self.quantifier_block.append(["# Move variables: "])
        for t in range(self.parsed.depth):
            self.quantifier_block.append(self.move_variables[t])

        # 2. position variables (3 per position)
        self.quantifier_block.append(["# Position variables: "])
        for state in ["black", "white", "empty"]:
            for t in range(self.parsed.depth):
                self.quantifier_block.append(
                    [
                        "exists("
                        + ", ".join(str(x) for x in self.position_states[state][t])
                        + ")"
                    ]
                )

        # 3. Liberty variables (empty adjacent positions) for each position:
        self.quantifier_block.append(["# Liberty variables: "])
        for t in range(self.parsed.depth):
            self.quantifier_block.append(
                ["exists(" + ", ".join(str(x) for x in self.liberty_variables[t]) + ")"]
            )

        # 4. State transition variables:
        self.quantifier_block.append(["# State transitions: "])
        self.encode_variables(self.num_positions, 1, self.quantifier_block)

        if self.parsed.args.debug == 1:
            print("Quantifier blocks: ", self.quantifier_block)

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

    def find_group(self, t, start_pos, visited):
        """
        Identifies the connected group of stones starting at `start_pos`.
        Returns:
        - group: Set of positions in the group.
        - group_color: Color of the stones in the group ("black" or "white").
        """
        # TODO critical point -> if this function fails it will all fail
        queue = [start_pos]
        group = set()
        group_color = None

        while queue:
            pos = queue.pop()
            if pos in visited:
                continue
            visited.add(pos)
            group.add(pos)

            # Determine the color of the group
            if not group_color:
                if self.position_states["black"][t][pos]:
                    group_color = "black"
                elif self.position_states["white"][t][pos]:
                    group_color = "white"

            # Add adjacent stones of the same color to the group
            adj_positions = self.get_adjacent_positions(pos)
            for adj in adj_positions:
                if adj not in visited and self.position_states[group_color][t][adj]:
                    queue.append(adj)

        return group, group_color

    def encode_liberties(self):
        """
        Encodes liberties for each position at each turn.
        A position's liberty is true if any of its adjacent positions are empty.
        """
        for t in range(self.parsed.depth):
            # Track visited positions to identify groups
            visited = set()

            for pos in range(self.num_positions):
                # Skip positions already processed
                if pos in visited:
                    continue

                # Identify the group starting at this position
                group, group_color = self.find_group(t, pos, visited)

                if group_color:
                    # Calculate liberties for the group
                    group_liberty_vars = []
                    for group_pos in group:
                        adj_positions = self.get_adjacent_positions(group_pos)
                        adj_empty_vars = [
                            self.position_states["empty"][t][adj]
                            for adj in adj_positions
                            if adj not in group
                        ]
                        group_liberty_vars.extend(adj_empty_vars)

                    # Combine liberties into a single variable for the group
                    if group_liberty_vars:
                        liberty_var = self.liberty_variables[t][pos]
                        self.gates_generator.or_gate(group_liberty_vars + [liberty_var])

    def encode_capture_rules(self, t):
        """
        Encodes capture rules for each position at each turn.
        A stone is captured if all its liberties are occupied by the opponent.
        """

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

        # Ensure that the initial positions are within the board size

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

    def not_gate(self, var):
        """
        Encodes a NOT gate for the given variable.
        """
        self.gates_generator.and_gate([var, -var])

    def prevent_repeated_board_state(self, t):
        """
        Ko rule: Prevents repeating the previous board state.
        """

        same_state_vars = []
        for pos in range(self.num_positions):
            for color in ["black", "white", "empty"]:
                curr_var = self.position_states[color][t][pos]
                next_var = self.position_states[color][t + 1][pos]
                # TODO could be that we need complete_equiality_gate
                self.gates_generator.single_equality_gate(curr_var, next_var)

            # Generate equivalence for the position's state at k and t+1
            equivalence_gate = self.encoding_variables.get_vars(1)[0]
            self.gates_generator.single_equality_gate(curr_var, next_var)
            same_state_vars.append(equivalence_gate)

        # Combine all equivalences for the board into a single "same state" gate
        board_same_gate = self.encoding_variables.get_vars(1)[0]
        self.gates_generator.and_gate(same_state_vars + [board_same_gate])

        # Prevent the next state from matching this previous state
        not_board_same_gate = self.encoding_variables.get_vars(1)[0]
        self.not_gate(board_same_gate)

        # Append the constraint to ensure the board state is not repeated
        self.encoding.append(f"-{not_board_same_gate} 0")

    def generate_transition_rules(self):
        """
        Encodes the rules governing state transitions between turns.
        This function calls individual rule encoding functions for:
        - Stone placement
        - Capture rules
        - State retention
        - Ko Rule (prevent repeated board state)
        """
        for t in range(self.parsed.depth - 1):
            self.encode_stone_placement(t)
            self.encode_capture_rules(t)
            self.encode_state_retention(t)
            self.prevent_repeated_board_state(t)

    def generate_goal_state(self):
        """
        Encodes the goal state based on the parsed input.
        - If the goal depends on `#blackwins`, encode multiple conditions for Black to win.

        """

        # Process each win condition and store gates for later combination
        self.goal_output_gates = []
        for goal_positions in self.parsed.blackwins:
            # Retrieve variables representing the positions in the goal
            win_vars = [
                self.position_states["black"][-1][self.parsed.positions.index(pos)]
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

        # Combine all goal gates into a single final output gate
        self.final_output_gate = self.encoding_variables.get_vars(1)[0]
        self.gates_generator.or_gate(self.goal_output_gates + [self.final_output_gate])

    def verify_encoding(self):
        """
        Verifies that all essential components of the QBF encoding are present.
        - Checks: Initial state, transition rules, goal state, and final output gate.
        """
        missing_components = []

        # Check initial state
        if not self.encoding:
            missing_components.append("Initial state encoding")

        # Check goal state
        if not hasattr(self, "goal_output_gates") or not self.goal_output_gates:
            missing_components.append("Goal state")

        # Check final output gate
        if not self.final_output_gate:
            missing_components.append("Final output gate")

        # Raise error or log warnings
        if missing_components:
            raise ValueError(
                f"The following components are missing in the encoding: {missing_components}"
            )

        print("Encoding verification passed successfully.")

    def __init__(self, parsed):

        self.parsed = parsed
        self.validate_parsed_input()

        self.encoding_variables = vd()

        self.quantifier_block = []
        self.encoding = []
        self.final_output_gate = 0

        # Gates generator
        self.gates_generator = ggen(self.encoding_variables, self.encoding)

        # Initialize board and position-related variables
        self.num_positions = parsed.board_size**2
        num_position_variables = self.num_positions * self.parsed.depth * 2

        # 3 per position : empty, black, white
        self.position_states = {"empty": [], "white": [], "black": []}
        self.position_states["empty"] = self.encode_variables(
            self.parsed.depth, self.num_positions
        )
        self.position_states["white"] = self.encode_variables(
            self.parsed.depth, self.num_positions
        )
        self.position_states["black"] = self.encode_variables(
            self.parsed.depth, self.num_positions
        )

        # track liberties (empty adjacent positions) -> maximum of 4 per position
        self.liberty_variables = self.encode_variables(
            self.parsed.depth, self.num_positions
        )

        # Move variables (one per move)
        self.move_variables = self.encode_variables(num_position_variables, 1)

        # Generate encoding components
        self.encode_liberties()
        self.generate_initial_state()
        self.generate_transition_rules()
        self.generate_goal_state()

        # Combine all components into the final gate
        self.generate_final_gate()

        # verifiy the completeness of the encodding
        self.verify_encoding()

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
        with open(file_path, "w", encoding="utf-8") as f:
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
