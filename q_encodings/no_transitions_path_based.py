# Irfansha Shaik, 14.01.2022, Aarhus.

# TODO: XXX

from utils.variables_dispatcher import VarDispatcher as vd
from utils.gates import GatesGen as ggen
import math
import utils.lessthen_cir as lsc



class NoTransitionsPathBasedGoal:

  def print_gate_tofile(self, gate, f):
    if len(gate) == 1:
      f.write(gate[0] + '\n')
    else:
      f.write(str(gate[1]) + ' = ' + gate[0] + '(' + ', '.join(str(x) for x in gate[2]) + ')\n')

  def print_encoding_tofile(self, file_path):
    f = open(file_path, 'w')
    for gate in self.quantifier_block:
      self.print_gate_tofile(gate, f)
    f.write('output(' + str(self.final_output_gate) + ')\n')
    for gate in self.encoding:
      self.print_gate_tofile(gate, f)

  # Takes a list of clause variables and maps to a integer value:
  def generate_binary_format(self, clause_variables, corresponding_number):
    num_variables = len(clause_variables)
    # Representation in binary requires number of variables:
    rep_string = '0' + str(num_variables) + 'b'
    bin_string = format(corresponding_number, rep_string)
    cur_variable_list = []
    # Depending on the binary string we set action variables to '+' or '-':
    for j in range(num_variables):
      if (bin_string[j] == '0'):
        cur_variable_list.append(-clause_variables[j])
      else:
        cur_variable_list.append(clause_variables[j])
    return cur_variable_list

  # Generates quanifier blocks:
  def generate_quantifier_blocks(self):

    # Move variables following time variables:
    self.quantifier_block.append(['# Move variables: '])
    for i in range(self.parsed.depth):
      # starts with 0 and even is black (i.e., existential moves):
      if (i % 2 == 0):
        self.quantifier_block.append(['exists(' + ', '.join(str(x) for x in self.move_variables[i]) + ')'])
      else:
        self.quantifier_block.append(['forall(' + ', '.join(str(x) for x in self.move_variables[i]) + ')'])

    # Grounded goal variables before forall position variables:
    self.quantifier_block.append(['# goal path variables: '])
    all_goal_vars = []
    for vars in self.goal_path_variables:
      all_goal_vars.extend(vars)
    self.quantifier_block.append(['exists(' + ', '.join(str(x) for x in all_goal_vars) + ')'])

    # Grounded goal boolean variables before forall position variables:
    self.quantifier_block.append(['# goal path boolean variables: '])
    self.quantifier_block.append(['exists(' + ', '.join(str(x) for x in self.goal_path_boolean_variables) + ')'])

    # Forall position variables:
    self.quantifier_block.append(['# Forall position variables: '])
    self.quantifier_block.append(['forall(' + ', '.join(str(x) for x in self.forall_position_variables) + ')'])

    # Finally predicate variables for each time step:
    self.quantifier_block.append(['# Predicate variables: '])
    self.quantifier_block.append(['exists(' + ', '.join(str(x) for x in self.predicate_variables) + ')'])

    # Exists neighbour variables:
    self.quantifier_block.append(['# Exists neighbour variables: '])
    self.quantifier_block.append(['exists(' + ', '.join(str(x) for x in self.neighbour) + ')'])



  def generate_black_implication(self, time_step):
    self.encoding.append(['# Player 1 (black) implication for time step ' + str(time_step)+ ': '])

    # Move equality constraint with position variables:
    self.encoding.append(['# Equality gate for move and forall positional variables:'])
    self.gates_generator.complete_equality_gate(self.move_variables[time_step], self.forall_position_variables)
    #equality_output_gate = self.gates_generator.output_gate
    conditional_and_output_gate = self.gates_generator.output_gate

    # Now if condition:
    self.encoding.append(['# Equality constraints == time step + 2 black bit must be true:'])
    self.gates_generator.single_equality_gate(conditional_and_output_gate, self.predicate_variables[time_step+2])
    self.transition_step_output_gates.append(self.gates_generator.output_gate)


  def generate_white_implication(self, time_step):
    self.encoding.append(['# Player 2 (white) implication for time step ' + str(time_step)+ ': '])

    # Generating move restriction clauses inside if condition if enabled:
    if (self.parsed.args.forall_move_restrictions == 'in' and self.parsed.num_available_moves != int(math.pow(2, self.num_move_variables))):
      # White move restriction:
      self.encoding.append(['# Move constraints (if not powers of 2 or simply restricting moves) :'])
      #lsc.add_circuit(self.gates_generator, self.move_variables[time_step], self.parsed.num_positions)
      # using new open moves, further restricting search space:
      lsc.add_circuit(self.gates_generator, self.move_variables[time_step], self.parsed.num_available_moves)
      move_restriction_output_gate = self.gates_generator.output_gate

    # Move equality constraint with position variables:
    self.encoding.append(['# Equality gate for move and forall positional variables:'])
    self.gates_generator.complete_equality_gate(self.move_variables[time_step], self.forall_position_variables)
    # If inside move restrictions are enables, including in the if condition:
    if (self.parsed.args.forall_move_restrictions == 'in' and self.parsed.num_available_moves != int(math.pow(2, self.num_move_variables))):
      # conjuction for move restriction and equality constraint:
      self.encoding.append(['# Conjuction for move restriction and above conjunction constraints:'])
      self.gates_generator.and_gate([move_restriction_output_gate, self.gates_generator.output_gate])

    conditional_and_output_gate = self.gates_generator.output_gate

    # Now if condition:
    self.encoding.append(['# Equality constraints == time step + 2 white bit must be true:'])
    self.gates_generator.single_equality_gate(conditional_and_output_gate, self.predicate_variables[time_step+2])
    self.transition_step_output_gates.append(self.gates_generator.output_gate)

  def generate_d_transitions(self):
    self.encoding.append(["# ------------------------------------------------------------------------"])
    self.encoding.append(['# Transitions: '])
    for i in range(self.parsed.depth):
      if (i%2 == 0):
        self.generate_black_implication(i)
      else:
        self.generate_white_implication(i)
    
    # TODO: (Optional) Add atmost one constraints for the black boolean variables:
    # Black player never overwrites:
    # We only need to constraint the moves, so start from index 2:
    for i in range(len(self.predicate_variables)):
      if (i % 2 == 0):
        step_black_implication_bits = []
        for j in range(i):
          step_black_implication_bits.append(-self.predicate_variables[j])
        # conjunction gate for the implication bits:
        self.gates_generator.and_gate(step_black_implication_bits)

        # If the current black bit is true then the conjunciton must be true:
        self.gates_generator.if_then_gate(self.predicate_variables[i], self.gates_generator.output_gate)

        # Appending to the transition step output gates:
        self.transition_step_output_gates.append(self.gates_generator.output_gate)

    self.encoding.append(['# Final transition gate: '])
    self.gates_generator.and_gate(self.transition_step_output_gates)
    self.transition_output_gate = self.gates_generator.output_gate


  def generate_initial_gate(self):
    initial_step_output_gates = []

    self.encoding.append(["# ------------------------------------------------------------------------"])
    self.encoding.append(['# Initial state: '])

    if (len(self.parsed.black_initial_positions) != 0):

       # Constraints in forall branches for black positions:
       black_position_output_gates = []
       for position in self.parsed.black_initial_positions:
         binary_format_clause = self.generate_binary_format(self.forall_position_variables,position)
         self.gates_generator.and_gate(binary_format_clause)
         black_position_output_gates.append(self.gates_generator.output_gate)

       self.encoding.append(['# Or for all black forall position clauses: '])
       self.gates_generator.or_gate(black_position_output_gates)

       black_final_output_gate = self.gates_generator.output_gate

       self.encoding.append(['# if black condition is true then 0th black bit is true: '])
       # Set black bit to true and white bit to false:
       self.gates_generator.and_gate([self.predicate_variables[0], -self.predicate_variables[1]])
       self.gates_generator.if_then_gate(black_final_output_gate, self.gates_generator.output_gate)

       initial_step_output_gates.append(self.gates_generator.output_gate)

    if (len(self.parsed.white_initial_positions) != 0):

      # Constraints in forall branches for white positions:
      white_position_output_gates = []

      for position in self.parsed.white_initial_positions:
        binary_format_clause = self.generate_binary_format(self.forall_position_variables,position)
        self.gates_generator.and_gate(binary_format_clause)
        white_position_output_gates.append(self.gates_generator.output_gate)

      self.encoding.append(['# Or for all white forall position clauses: '])
      self.gates_generator.or_gate(white_position_output_gates)

      white_final_output_gate = self.gates_generator.output_gate

      self.encoding.append(['# if white condition is true then first time step occupied and color white so 1st bit is true: '])
      # Set black bit to true and white bit to false:
      self.gates_generator.and_gate([-self.predicate_variables[0], self.predicate_variables[1]])
      self.gates_generator.if_then_gate(white_final_output_gate, self.gates_generator.output_gate)

      initial_step_output_gates.append(self.gates_generator.output_gate)

    if (len(initial_step_output_gates) != 0):

      # Finally for all other forall branches, the position is unoccupied:
      self.encoding.append(['# for all other branches the first two bits are 0: '])
      self.gates_generator.or_gate([black_final_output_gate, white_final_output_gate])
      branch_if_condition = self.gates_generator.output_gate
      self.gates_generator.and_gate([-self.predicate_variables[0], -self.predicate_variables[1]])
      self.gates_generator.or_gate([branch_if_condition, self.gates_generator.output_gate])
      initial_step_output_gates.append(self.gates_generator.output_gate)
    else:
      self.encoding.append(['# In all branches the first two bits are 0: '])
      self.gates_generator.and_gate([-self.predicate_variables[0], -self.predicate_variables[1]])
      initial_step_output_gates.append(self.gates_generator.output_gate)

    # Specifying neighbours:
    self.encoding.append(['# Specifying neighbours: '])
    for i in range(self.parsed.num_positions):
      # We do not need to specify white position neighbours:
      # NOTE: Careful it is only for hex
      if (i in self.parsed.white_initial_positions):
        continue
      binary_format_clause = self.generate_binary_format(self.forall_position_variables,i)
      self.gates_generator.and_gate(binary_format_clause)
      if_condition_output_gate = self.gates_generator.output_gate
      neighbour_output_gates = []
      self.encoding.append(['# neighbour clauses: '])
      # Neighbours of current position:
      #temp_neighbours = list(self.parsed.neighbour_dict[i])

      # For each neighbour we generate a clause:
      for cur_neighbour in self.parsed.neighbour_dict[i]:
        temp_binary_format_clause = self.generate_binary_format(self.neighbour,cur_neighbour)
        self.gates_generator.and_gate(temp_binary_format_clause)
        neighbour_output_gates.append(self.gates_generator.output_gate)

      # Disjunction of output gates is true:
      self.gates_generator.or_gate(neighbour_output_gates)


      # If then clause for the neighbour implication:
      self.encoding.append(['# if then clause : '])
      self.gates_generator.if_then_gate(if_condition_output_gate,self.gates_generator.output_gate)
      initial_step_output_gates.append(self.gates_generator.output_gate)

    # Now final output gate for the initial state:
    self.gates_generator.and_gate(initial_step_output_gates)
    self.initial_output_gate = self.gates_generator.output_gate


  # Generating goal constraints:
  def generate_goal_gate(self):
    goal_step_output_gates = []
    self.encoding.append(["# ------------------------------------------------------------------------"])
    self.encoding.append(['# Goal state: '])


    # First goal boolean variable is always positive:
    goal_step_output_gates.append(self.goal_path_boolean_variables[0])

    # Path based equality constraints
    for i in range(self.safe_max_path_length - 1):
      self.encoding.append(['# Constratins for position ' + str(i) + ' :'])
      self.encoding.append(['# Equality clause for the current path variables and forall position variables: '])
      self.gates_generator.complete_equality_gate(self.goal_path_variables[i], self.forall_position_variables)
      cur_path_forall_equality_output_gate = self.gates_generator.output_gate


      # Equality for neighbour variables and next position:
      self.encoding.append(['# Equality clause for the neighbour path variables and neighbour variables: '])
      self.gates_generator.complete_equality_gate(self.goal_path_variables[i+1], self.neighbour)
      path_neighbour_equality_output_gate = self.gates_generator.output_gate

      # Equality for next position with current position:
      self.encoding.append(['# Equality clause for the neighbour path variables and current path variables: '])
      self.gates_generator.complete_equality_gate(self.goal_path_variables[i+1], self.goal_path_variables[i])
      next_cur_path_equality_output_gate = self.gates_generator.output_gate



      # if boolean is true along with position forall equality then nieghbour equality is true:
      self.encoding.append(['# if boolean is true along with position forall equality then nieghbour equality is true: '])
      self.gates_generator.and_gate([cur_path_forall_equality_output_gate, self.goal_path_boolean_variables[i]])
      self.gates_generator.if_then_gate(self.gates_generator.output_gate, path_neighbour_equality_output_gate)
      goal_step_output_gates.append(self.gates_generator.output_gate)

      # if boolean is false, then the next position is same as current and next booelean is false too:
      self.encoding.append(['# if boolean is false, then the next position is same as current and next booelean is false too: '])
      self.gates_generator.and_gate([cur_path_forall_equality_output_gate, -self.goal_path_boolean_variables[i]])
      self.gates_generator.if_then_gate(self.gates_generator.output_gate, [next_cur_path_equality_output_gate, -self.goal_path_boolean_variables[i+1]])
      goal_step_output_gates.append(self.gates_generator.output_gate)

      # the position must be occupied and the color must be black:
      self.encoding.append(['# One of the black bits must be true: '])
      step_black_bits = []
      for i in range(len(self.predicate_variables)):
        if (i % 2 == 0):
          step_black_bits.append(self.predicate_variables[i])
      self.gates_generator.or_gate(step_black_bits)
      constraints_output_gate = self.gates_generator.output_gate

      self.encoding.append(['# if then clause : '])
      # The if condition for the path constraints:
      self.gates_generator.if_then_gate(cur_path_forall_equality_output_gate, constraints_output_gate)
      goal_step_output_gates.append(self.gates_generator.output_gate)

    # The last path position also must be occupied and black:
    self.encoding.append(['# Constratins for position ' + str(self.safe_max_path_length - 1) + ' :'])
    self.encoding.append(['# Equality clause for the current path variables and forall position variables: '])
    self.gates_generator.complete_equality_gate(self.goal_path_variables[self.safe_max_path_length - 1], self.forall_position_variables)
    last_if_condition_output_gate = self.gates_generator.output_gate
    # the position must be occupied and the color must be black, we reuse the constraints output gate above:
    self.encoding.append(['# if then clause : '])
    # The if condition for the path constraints:
    self.gates_generator.if_then_gate(last_if_condition_output_gate, constraints_output_gate)
    goal_step_output_gates.append(self.gates_generator.output_gate)


    start_border_output_gates = []
    self.encoding.append(['# Start boarder clauses : '])
    # Specifying the start borders:
    for pos in self.parsed.start_boarder:
      binary_format_clause = self.generate_binary_format(self.goal_path_variables[0],pos)
      self.gates_generator.and_gate(binary_format_clause)
      start_border_output_gates.append(self.gates_generator.output_gate)

    self.encoding.append(['# disjunction of all start boarder positions : '])
    self.gates_generator.or_gate(start_border_output_gates)

    goal_step_output_gates.append(self.gates_generator.output_gate)

    end_border_output_gates = []
    self.encoding.append(['# End boarder clauses : '])
    # Specifying the end borders:
    for pos in self.parsed.end_boarder:
      binary_format_clause = self.generate_binary_format(self.goal_path_variables[-1],pos)
      self.gates_generator.and_gate(binary_format_clause)
      end_border_output_gates.append(self.gates_generator.output_gate)

    self.encoding.append(['# disjunction of all end boarder positions : '])
    self.gates_generator.or_gate(end_border_output_gates)

    goal_step_output_gates.append(self.gates_generator.output_gate)

    # Final goal gate:
    self.encoding.append(['# Final and gate for goal constraints: '])
    self.gates_generator.and_gate(goal_step_output_gates)

    self.goal_output_gate = self.gates_generator.output_gate


  def generate_restricted_black_moves(self):

    step_restricted_black_output_gates = []

    self.encoding.append(["# ------------------------------------------------------------------------"])
    self.encoding.append(['# Restricted black moves: '])

    for i in range(self.parsed.depth):
      if (i%2 == 0):
        #lsc.add_circuit(self.gates_generator, self.move_variables[i], self.parsed.num_positions)
        # restricting more moves:
        lsc.add_circuit(self.gates_generator, self.move_variables[i], self.parsed.num_available_moves)
        step_restricted_black_output_gates.append(self.gates_generator.output_gate)

    self.encoding.append(['# And gate for all restricted black move clauses: '])
    self.gates_generator.and_gate(step_restricted_black_output_gates)
    self.restricted_black_gate = self.gates_generator.output_gate


  # Final output gate is an and-gate with inital, goal and transition gates:
  def generate_final_gate(self):
    self.encoding.append(["# ------------------------------------------------------------------------"])
    self.encoding.append(['# Final gate: '])

    self.encoding.append(['# Conjunction of Initial gate and Transition gate and Goal gate: '])
    # Restrictions on black moves are invalid if not powers of 2:
    if (self.parsed.num_available_moves != int(math.pow(2, self.num_move_variables)) and self.parsed.args.black_move_restrictions == 1):
      self.gates_generator.and_gate([self.restricted_black_gate, self.initial_output_gate, self.transition_output_gate, self.goal_output_gate])
    else:
      self.gates_generator.and_gate([self.initial_output_gate, self.transition_output_gate, self.goal_output_gate])

    self.final_output_gate = self.gates_generator.output_gate


  def __init__(self, parsed):
    self.parsed = parsed
    self.encoding_variables = vd()
    self.quantifier_block = []
    self.dqdimacs_prefix = []
    self.encoding = []
    self.initial_output_gate = 0 # initial output gate can never be 0
    self.goal_output_gate = 0 # goal output gate can never be 0
    self.transition_step_output_gates = []
    self.transition_output_gate = 0 # Can never be 0
    self.restricted_black_gate = 0 # Can never be 0
    self.final_output_gate = 0 # Can never be 0


    # Allocating action variables for each time step until depth:
    # Handling single move, log 1 is 0:
    if (parsed.num_available_moves == 1):
      self.num_move_variables = 1
    else:
      self.num_move_variables = math.ceil(math.log2(parsed.num_available_moves))
    self.move_variables = []
    for i in range(parsed.depth):
      self.move_variables.append(self.encoding_variables.get_vars(self.num_move_variables))

    if (parsed.args.debug == 1):
      print("Number of (log) move variables: ", self.num_move_variables)
      print("Move variables: ",self.move_variables)

    # Moves are same as the vertexs/positions on the board:
    self.num_position_variables = math.ceil(math.log2(parsed.num_positions))


    # Allocating forall position variables:
    self.forall_position_variables = self.encoding_variables.get_vars(self.num_position_variables)

    if (parsed.args.debug == 1):
      print("Forall position variables: ",self.forall_position_variables)

    # Allocating predicate variables, we need two bits to represent initial state occupying
    # and then each bit for one move at the correspoding time step:
    self.predicate_variables = self.encoding_variables.get_vars(parsed.depth+2)

    if (parsed.args.debug == 1):
      print("Predicate variables: ",self.predicate_variables)

    # Allocating path variables for the goal:
    self.goal_path_variables = []
    self.safe_max_path_length = len(self.parsed.black_initial_positions) + int((self.parsed.depth + 1)/2)

    for i in range(self.safe_max_path_length):
      self.goal_path_variables.append(self.encoding_variables.get_vars(self.num_position_variables))

    # Allocating single boolean variable for each goal path position,
    # we avoid redundancy due to stutturing of same position:
    self.goal_path_boolean_variables = self.encoding_variables.get_vars(self.safe_max_path_length)


    # One neighbour is sufficeint for path based:
    self.neighbour = self.encoding_variables.get_vars(self.num_position_variables)

    if (parsed.args.debug == 1):
      print("Goal state variables: ",self.goal_path_variables)
      #print("Neighbour variables: ", self.neighbour_variables)
      print("Neighbour variables: ", self.neighbour)


    # Generating quantifer blocks:
    self.generate_quantifier_blocks()


    self.gates_generator = ggen(self.encoding_variables, self.encoding)

    # Generating d steps i.e., which includes black and white constraints:
    self.generate_d_transitions()

    self.generate_initial_gate()

    self.generate_goal_gate()

    # Note: Improved version needs to change this with only open positions:
    if (self.parsed.num_available_moves != int(math.pow(2, self.num_move_variables)) and self.parsed.args.black_move_restrictions == 1):
      self.generate_restricted_black_moves()

    self.generate_final_gate()
