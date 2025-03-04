# Irfansha Shaik, 17.01.2022, Aarhus.

# TODO: It is possible to avoid multiple inequalities for the black not overwriting the white


import math

import utils.lessthen_cir as lsc
from utils.gates import GatesGen as ggen
from utils.variables_dispatcher import VarDispatcher as vd


class CompactGoalCompactPositonal:

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

    # witness variables:
    self.quantifier_block.append(['# witness variables: '])
    all_goal_vars = []
    for vars in self.witness_variables:
      all_goal_vars.extend(vars)
    self.quantifier_block.append(['exists(' + ', '.join(str(x) for x in all_goal_vars) + ')'])

    # Start chain variables:
    self.quantifier_block.append(['# Start variables: '])
    self.quantifier_block.append(['exists(' + ', '.join(str(x) for x in self.start_two_chain_positions[0]) + ')'])
    self.quantifier_block.append(['exists(' + ', '.join(str(x) for x in self.start_two_chain_positions[1]) + ')'])

    # End chain variables:
    self.quantifier_block.append(['# End variables: '])
    self.quantifier_block.append(['exists(' + ', '.join(str(x) for x in self.end_two_chain_positions[0]) + ')'])
    self.quantifier_block.append(['exists(' + ', '.join(str(x) for x in self.end_two_chain_positions[1]) + ')'])


    # Forall witness length variables:
    self.quantifier_block.append(['# Forall witness length variables: '])
    self.quantifier_block.append(['forall(' + ', '.join(str(x) for x in self.forall_witness_length_variables) + ')'])

    # Exists witness variables:
    self.quantifier_block.append(['# Exists witness variables: '])
    self.quantifier_block.append(['exists(' + ', '.join(str(x) for x in self.exists_witness_variables[0]) + ')'])
    self.quantifier_block.append(['exists(' + ', '.join(str(x) for x in self.exists_witness_variables[1]) + ')'])

    # inner most chain variables:
    self.quantifier_block.append(['# Inner most chain variables: '])
    self.quantifier_block.append(['exists(' + ', '.join(str(x) for x in self.inner_most_two_chain_positions[0]) + ')'])
    self.quantifier_block.append(['exists(' + ', '.join(str(x) for x in self.inner_most_two_chain_positions[1]) + ')'])



  # Generate neighbour clauses:
  def generate_neighbour_clauses(self, first, second):
    step_neighbour_output_gates = []
    # Connections with nieghbour information for the exists witness variables in the inner most layer:
    # Now specifying the implication for each pair:
    # iterating through each possible position value:
    for i in range(self.parsed.num_available_moves):
      self.encoding.append(['# position clauses: '])
      binary_format_clause = self.generate_binary_format(first,i)
      self.gates_generator.and_gate(binary_format_clause)
      if_condition_output_gate = self.gates_generator.output_gate
      neighbour_output_gates = []
      self.encoding.append(['# neighbour clauses: '])

      # For each neighbour we generate a clause:
      for cur_neighbour in self.parsed.neighbour_dict[i]:
        temp_binary_format_clause = self.generate_binary_format(second,cur_neighbour)
        self.gates_generator.and_gate(temp_binary_format_clause)
        neighbour_output_gates.append(self.gates_generator.output_gate)

      # For allowing shorter paths, we say the position is also its neighbour:
      temp_binary_format_clause = self.generate_binary_format(second,i)
      self.gates_generator.and_gate(temp_binary_format_clause)
      neighbour_output_gates.append(self.gates_generator.output_gate)

      # One of the values must be true, so a disjunction:
      self.gates_generator.or_gate(neighbour_output_gates)

      # If then clause for the neighbour implication:
      self.encoding.append(['# if then clause : '])
      self.gates_generator.if_then_gate(if_condition_output_gate,self.gates_generator.output_gate)

      step_neighbour_output_gates.append(self.gates_generator.output_gate)

    self.gates_generator.and_gate(step_neighbour_output_gates)
    return self.gates_generator.output_gate


  def position_is_black(self,position):
    # Position must be only black:
    self.encoding.append(['# Positions can only have the black moves : '])
    step_disjunction_output_gates = []
    # Iterating through the black moves:
    for i in range(self.parsed.depth):
      if (i%2 == 0):
        self.gates_generator.complete_equality_gate(position, self.move_variables[i])
        step_disjunction_output_gates.append(self.gates_generator.output_gate)
    # One of the equality must be true:
    self.gates_generator.or_gate(step_disjunction_output_gates)
    return self.gates_generator.output_gate


  def position_is_white(self,position):
    # Position must be only black:
    self.encoding.append(['# Position is white moves : '])
    step_disjunction_output_gates = []
    # Iterating through the black moves:
    for i in range(self.parsed.depth):
      if (i%2 != 0):
        self.gates_generator.complete_equality_gate(position, self.move_variables[i])
        step_disjunction_output_gates.append(self.gates_generator.output_gate)
    # One of the equality must be true:
    self.gates_generator.or_gate(step_disjunction_output_gates)
    return self.gates_generator.output_gate



  def __init__(self, parsed):
    self.parsed = parsed
    self.encoding_variables = vd()
    self.quantifier_block = []
    self.encoding = []
    self.step_output_gates = []
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


    # Allocating path variables for the goal,
    # For now assuming the empty board:
    self.witness_variables = []
    self.safe_max_path_length = int((self.parsed.depth + 1)/2)

    for i in range(self.safe_max_path_length):
      self.witness_variables.append(self.encoding_variables.get_vars(self.num_move_variables))

    if (parsed.args.debug == 1):
      print("Goal state variables: ",self.witness_variables)

    # Log forall variables for length of the witness:
    self.num_witness_path_variables = math.ceil(math.log2(self.safe_max_path_length))
    self.forall_witness_length_variables = self.encoding_variables.get_vars(self.num_witness_path_variables)

    if (parsed.args.debug == 1):
      print("Forall witness length variables: ",self.forall_witness_length_variables)
    
    # Two existential varibles for the witness varaibles:
    self.exists_witness_variables = []
    for i in range(2):
      self.exists_witness_variables.append(self.encoding_variables.get_vars(self.num_move_variables))



    # Start and ending two chain positions:
    self.start_two_chain_positions = []
    for i in range(2):
      self.start_two_chain_positions.append(self.encoding_variables.get_vars(self.num_move_variables))


    self.end_two_chain_positions = []
    for i in range(2):
      self.end_two_chain_positions.append(self.encoding_variables.get_vars(self.num_move_variables))

    #'''
    self.inner_most_two_chain_positions = []
    for i in range(2):
      self.inner_most_two_chain_positions.append(self.encoding_variables.get_vars(self.num_move_variables))
    #'''

    # Generating quantifer blocks:
    self.generate_quantifier_blocks()

    self.gates_generator = ggen(self.encoding_variables, self.encoding)


    # Black cannot overwrite white moves:

    # Iterating through all the black moves:
    self.encoding.append(['# Black does not overwrite the white moves : '])
    for i in range(self.parsed.depth):
      if (i%2 == 0):
        # Iterating through all the white moves:
        for j in range(i):
          if (j%2 == 1):
            self.gates_generator.complete_equality_gate(self.move_variables[i], self.move_variables[j])
            # Black moves cannot be equal to white, so negative:
            self.step_output_gates.append(-self.gates_generator.output_gate)

    # Positions in the witness must be among the black moves:

    # The first exists witness (inner most) must be only black:
    self.encoding.append(['# Witness positions can only have the black moves : '])
    step_disjunction_output_gates = []
    # Iterating through the black moves:
    for i in range(self.parsed.depth):
      if (i%2 == 0):
        self.gates_generator.complete_equality_gate(self.exists_witness_variables[0], self.move_variables[i])
        step_disjunction_output_gates.append(self.gates_generator.output_gate)
    # One of the equality must be true:
    self.gates_generator.or_gate(step_disjunction_output_gates)
    self.step_output_gates.append(self.gates_generator.output_gate)


    # The witness must make a path:
    #-------------------------------------------------------------------------------------
    # Start boarder:
    start_border_output_gates = []
    for pos in self.parsed.start_boarder:
      binary_format_clause = self.generate_binary_format(self.witness_variables[0],pos)
      self.gates_generator.and_gate(binary_format_clause)
      start_border_output_gates.append(self.gates_generator.output_gate)

    self.encoding.append(['# disjunction of all start boarder positions : '])
    self.gates_generator.or_gate(start_border_output_gates)
    self.original_start_position_output_gate = self.gates_generator.output_gate


    start_step_chain_output_gates = []

    # If the first two chain boolean variable is true then the two chain positions must be start positions:
    first_two_chain_start_border_output_gates = []
    self.encoding.append(['# First two chain start boarder clauses : '])
    # Specifying the start borders for first two chain position:
    for pos in self.parsed.start_boarder:
      binary_format_clause = self.generate_binary_format(self.start_two_chain_positions[0],pos)
      self.gates_generator.and_gate(binary_format_clause)
      first_two_chain_start_border_output_gates.append(self.gates_generator.output_gate)

    self.encoding.append(['# disjunction of all first chain start boarder positions : '])
    self.gates_generator.or_gate(first_two_chain_start_border_output_gates)
    start_step_chain_output_gates.append(self.gates_generator.output_gate)


    # If the second two chain boolean variable is true then the two chain positions must be start positions:
    second_two_chain_start_border_output_gates = []
    self.encoding.append(['# Second two chain start boarder clauses : '])
    # Specifying the start borders for first two chain position:
    for pos in self.parsed.start_boarder:
      binary_format_clause = self.generate_binary_format(self.start_two_chain_positions[1],pos)
      self.gates_generator.and_gate(binary_format_clause)
      second_two_chain_start_border_output_gates.append(self.gates_generator.output_gate)

    self.encoding.append(['# disjunction of all second chain start boarder positions : '])
    self.gates_generator.or_gate(second_two_chain_start_border_output_gates)
    start_step_chain_output_gates.append(self.gates_generator.output_gate)


    #======================================================================================================================================
    # disjunction of : 1. first start two chain is black and neighbour
    #                  2. both are open and not equal and are neighbours of the first witness position
    #--------------------------------------------------------------------
    # neighbour constraints:
    first_start_neighbour_output_gate = self.generate_neighbour_clauses(self.start_two_chain_positions[0],self.witness_variables[0])
    second_start_neighbour_output_gate = self.generate_neighbour_clauses(self.start_two_chain_positions[1],self.witness_variables[0])
    # first constraint:
    # if black or white:
    first_black_output_gate = self.position_is_black(self.start_two_chain_positions[0])
    first_white_output_gate = self.position_is_white(self.start_two_chain_positions[0])

    start_chain_disjunction_output_gates = []

    # 1. first start two chain is black and neigbour:
    self.gates_generator.and_gate([first_black_output_gate, first_start_neighbour_output_gate])
    start_chain_disjunction_output_gates.append(self.gates_generator.output_gate)

    #second constraint if black or white:
    second_black_output_gate = self.position_is_black(self.start_two_chain_positions[1])
    second_white_output_gate = self.position_is_white(self.start_two_chain_positions[1])

    # 2. both are open and not equal and are neighbours of the first witness position
    # both must be different:
    self.gates_generator.complete_equality_gate(self.start_two_chain_positions[0],self.start_two_chain_positions[1])
    start_chain_positions_inequality_output_gate = -self.gates_generator.output_gate

    # first start chain position is not black and not white, second start chain position is not black and not white, both are different and they are neighbours to first witness position:
    self.gates_generator.and_gate([-first_black_output_gate, -first_white_output_gate, -second_black_output_gate, -second_white_output_gate, first_start_neighbour_output_gate, second_start_neighbour_output_gate, start_chain_positions_inequality_output_gate])
    start_chain_disjunction_output_gates.append(self.gates_generator.output_gate)


    # disjunction of the chain link:
    self.gates_generator.or_gate(start_chain_disjunction_output_gates)

    start_step_chain_output_gates.append(self.gates_generator.output_gate)

    #======================================================================================================================================

    # conjunction of the chain link:
    self.gates_generator.and_gate(start_step_chain_output_gates)

    # Disjunction linking the start boarder chain:
    self.gates_generator.or_gate([self.gates_generator.output_gate, self.original_start_position_output_gate])

    self.step_output_gates.append(self.gates_generator.output_gate)

    #-------------------------------------------------------------------------------------

    # Connecting the witness with the inner most witness variables:
    self.encoding.append(['# Connecting witness variables to inner most witness variables : '])
    for i in range(self.safe_max_path_length-1):
      # Specifying the branch:
      self.encoding.append(['# Specifying the branch : '])
      branch_variables = self.generate_binary_format(self.forall_witness_length_variables, i)
      self.gates_generator.and_gate(branch_variables)
      branch_output_gate = self.gates_generator.output_gate

      # Equality for the witness position with the first inner most witness variable:
      self.gates_generator.complete_equality_gate(self.witness_variables[i], self.exists_witness_variables[0])
      first_equality_output_gate = self.gates_generator.output_gate

      # Equality for the next witness position with the second inner most witness variable:
      self.gates_generator.complete_equality_gate(self.witness_variables[i+1], self.exists_witness_variables[1])
      second_equality_output_gate = self.gates_generator.output_gate

      # If then gate for the implication:
      self.gates_generator.if_then_gate(branch_output_gate, [first_equality_output_gate, second_equality_output_gate])
      self.step_output_gates.append(self.gates_generator.output_gate)

    # Last position must be connected too:
    # Specifying the branch:
    self.encoding.append(['# Specifying the branch : '])
    branch_variables = self.generate_binary_format(self.forall_witness_length_variables, self.safe_max_path_length-1)
    self.gates_generator.and_gate(branch_variables)
    branch_output_gate = self.gates_generator.output_gate

    # Equality for the witness position with the first inner most witness variable:
    self.gates_generator.complete_equality_gate(self.witness_variables[self.safe_max_path_length-1], self.exists_witness_variables[0])
    first_equality_output_gate = self.gates_generator.output_gate

    # If then gate for the implication:
    self.gates_generator.if_then_gate(branch_output_gate, first_equality_output_gate)
    self.step_output_gates.append(self.gates_generator.output_gate)


    #------------------------------------------------------------------------------------------------------------------------------------

    # Neighbour relation for inner most exitential witness variables:
    inner_most_neighbour_output_gate = self.generate_neighbour_clauses(self.exists_witness_variables[0],self.exists_witness_variables[1])
    # only when disabling the inner most connection:
    #self.step_output_gates.append(inner_most_neighbour_output_gate)

    #'''

    #======================================================================================================================================
    # disjunction of : 1. first inner two chain is black and neighbour of both inner witness positions
    #                  2. both inner two chain are open and not equal and are neighbours of the both inner witness positions
    #--------------------------------------------------------------------
    # first inner chain position neighbour constraints:
    first_inner_left_neighbour_output_gate = self.generate_neighbour_clauses(self.exists_witness_variables[0], self.inner_most_two_chain_positions[0])
    first_inner_right_neighbour_output_gate = self.generate_neighbour_clauses(self.inner_most_two_chain_positions[0], self.exists_witness_variables[1])



    # second inner chain position neighbour constraints:
    second_inner_left_neighbour_output_gate = self.generate_neighbour_clauses(self.exists_witness_variables[0], self.inner_most_two_chain_positions[1])
    second_inner_right_neighbour_output_gate = self.generate_neighbour_clauses(self.inner_most_two_chain_positions[1], self.exists_witness_variables[1])

    # first constraint:
    # if black or white:
    first_black_output_gate = self.position_is_black(self.inner_most_two_chain_positions[0])
    first_white_output_gate = self.position_is_white(self.inner_most_two_chain_positions[0])

    inner_chain_disjunction_output_gates = []

    # 1. first inner two chain is black and neigbour:
    self.gates_generator.and_gate([first_black_output_gate, first_inner_left_neighbour_output_gate, first_inner_right_neighbour_output_gate])
    inner_chain_disjunction_output_gates.append(self.gates_generator.output_gate)

    # second constraint, if black or white:
    second_black_output_gate = self.position_is_black(self.inner_most_two_chain_positions[1])
    second_white_output_gate = self.position_is_white(self.inner_most_two_chain_positions[1])

    # 2. both are open and not equal and are neighbours of the inner witness position
    # both must be different:
    self.gates_generator.complete_equality_gate(self.inner_most_two_chain_positions[0],self.inner_most_two_chain_positions[1])
    inner_chain_positions_inequality_output_gate = -self.gates_generator.output_gate

    # first inner chain position is not black and not white, second inner chain position is not black and not white, both are different and they are neighbours to first witness position:
    self.gates_generator.and_gate([-first_black_output_gate, -first_white_output_gate, -second_black_output_gate, -second_white_output_gate, first_inner_left_neighbour_output_gate, first_inner_right_neighbour_output_gate, second_inner_left_neighbour_output_gate, second_inner_right_neighbour_output_gate, inner_chain_positions_inequality_output_gate])
    inner_chain_disjunction_output_gates.append(self.gates_generator.output_gate)


    # disjunction of the chain link:
    self.gates_generator.or_gate(inner_chain_disjunction_output_gates)

    #======================================================================================================================================

    # Disjunction linking the inner boarder chain:
    self.gates_generator.or_gate([self.gates_generator.output_gate, inner_most_neighbour_output_gate])

    self.step_output_gates.append(self.gates_generator.output_gate)
    #'''

    #------------------------------------------------------------------------------------------------------------------------------------


    #----------------------------------------------------------------------------------------------------

    # End boarder:
    end_border_output_gates = []
    self.encoding.append(['# End boarder clauses : '])
    # Specifying the end borders:
    for pos in self.parsed.end_boarder:
      binary_format_clause = self.generate_binary_format(self.witness_variables[-1],pos)
      self.gates_generator.and_gate(binary_format_clause)
      end_border_output_gates.append(self.gates_generator.output_gate)

    self.encoding.append(['# disjunction of all end boarder positions : '])
    self.gates_generator.or_gate(end_border_output_gates)
    self.original_end_position_output_gate = self.gates_generator.output_gate


    end_step_chain_output_gates = []

    # If the first two chain boolean variable is true then the two chain positions must be end positions:
    first_two_chain_end_border_output_gates = []
    self.encoding.append(['# First two chain end boarder clauses : '])
    # Specifying the end borders for first two chain position:
    for pos in self.parsed.end_boarder:
      binary_format_clause = self.generate_binary_format(self.end_two_chain_positions[0],pos)
      self.gates_generator.and_gate(binary_format_clause)
      first_two_chain_end_border_output_gates.append(self.gates_generator.output_gate)

    self.encoding.append(['# disjunction of all first chain end boarder positions : '])
    self.gates_generator.or_gate(first_two_chain_end_border_output_gates)
    end_step_chain_output_gates.append(self.gates_generator.output_gate)


    # If the second two chain boolean variable is true then the two chain positions must be end positions:
    second_two_chain_end_border_output_gates = []
    self.encoding.append(['# Second two chain end boarder clauses : '])
    # Specifying the end borders for second two chain position:
    for pos in self.parsed.end_boarder:
      binary_format_clause = self.generate_binary_format(self.end_two_chain_positions[1],pos)
      self.gates_generator.and_gate(binary_format_clause)
      second_two_chain_end_border_output_gates.append(self.gates_generator.output_gate)

    self.encoding.append(['# disjunction of all second chain end boarder positions : '])
    self.gates_generator.or_gate(second_two_chain_end_border_output_gates)
    end_step_chain_output_gates.append(self.gates_generator.output_gate)



    #======================================================================================================================================
    # disjunction of : 1. first end two chain is black and neighbour
    #                  2. both are open and not equal and are neighbours of the last witness position
    #--------------------------------------------------------------------
    # neighbour constraints:
    first_end_neighbour_output_gate = self.generate_neighbour_clauses(self.witness_variables[-1], self.end_two_chain_positions[0])
    second_end_neighbour_output_gate = self.generate_neighbour_clauses(self.witness_variables[-1], self.end_two_chain_positions[1])
    # first constraint:
    # if black or white:
    first_black_output_gate = self.position_is_black(self.end_two_chain_positions[0])
    first_white_output_gate = self.position_is_white(self.end_two_chain_positions[0])

    end_chain_disjunction_output_gates = []

    # 1. first end two chain is black and neigbour:
    self.gates_generator.and_gate([first_black_output_gate, first_end_neighbour_output_gate])
    end_chain_disjunction_output_gates.append(self.gates_generator.output_gate)

    # second constraint if black or white:
    second_black_output_gate = self.position_is_black(self.end_two_chain_positions[1])
    second_white_output_gate = self.position_is_white(self.end_two_chain_positions[1])

    # 2. both are open and not equal and are neighbours of the last witness position
    # both must be different:
    self.gates_generator.complete_equality_gate(self.end_two_chain_positions[0],self.end_two_chain_positions[1])
    end_chain_positions_inequality_output_gate = -self.gates_generator.output_gate

    # first end chain position is not black and not white, second end chain position is not black and not white, both are different and they are neighbours to first witness position:
    self.gates_generator.and_gate([-first_black_output_gate, -first_white_output_gate, -second_black_output_gate, -second_white_output_gate, first_end_neighbour_output_gate, second_end_neighbour_output_gate, end_chain_positions_inequality_output_gate])
    end_chain_disjunction_output_gates.append(self.gates_generator.output_gate)


    # disjunction of the chain link:
    self.gates_generator.or_gate(end_chain_disjunction_output_gates)

    end_step_chain_output_gates.append(self.gates_generator.output_gate)

    #======================================================================================================================================


    # conjunction of the chain link:
    self.gates_generator.and_gate(end_step_chain_output_gates)

    # Disjunction linking the end boarder chain:
    self.gates_generator.or_gate([self.gates_generator.output_gate, self.original_end_position_output_gate])

    self.step_output_gates.append(self.gates_generator.output_gate)

    #---------------------------------------------------------------------------------------------------


    # Black restrictions as option:
    if (self.parsed.num_available_moves != int(math.pow(2, self.num_move_variables)) and self.parsed.args.black_move_restrictions == 1):

      # For the empty boards we can restrict the first move:
      if (self.parsed.num_available_moves % 2 == 0) :
        lsc.add_circuit(self.gates_generator, self.move_variables[0], int((self.parsed.num_available_moves)/2))
      else:
        lsc.add_circuit(self.gates_generator, self.move_variables[0], int((self.parsed.num_available_moves+1)/2))
      self.step_output_gates.append(self.gates_generator.output_gate)

      self.encoding.append(['# Restricted black moves: '])
      for i in range(self.parsed.depth):
        if (i%2 == 0):
          # restricting more moves:
          lsc.add_circuit(self.gates_generator, self.move_variables[i], self.parsed.num_available_moves)
          # Can be added directly to the step output gates:
          self.step_output_gates.append(self.gates_generator.output_gate)

    # Final conjunction:
    self.encoding.append(['# Final conjunction gate : '])
    self.gates_generator.and_gate(self.step_output_gates)
    self.final_output_gate = self.gates_generator.output_gate
