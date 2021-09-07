# Irfansha Shaik, 01.09.2021, Aarhus.

import os, subprocess
import argparse
import math


def parse(problem_path):
  f = open(problem_path, 'r')
  lines = f.readlines()
  f.close()

  parsed_dict = {}

  for line in lines:
    stripped_line = line.strip("\n").strip(" ").split(" ")
    # we ignore if it is a comment:
    if ('%' == line[0] or line == '\n'):
      continue
    if ("#" in line):
      new_key = line.strip("\n")
      parsed_dict[new_key] = []
    else:
      parsed_dict[new_key].append(stripped_line)
  return parsed_dict

def print_to_file(file_path, parsed_dict):
  f = open(file_path, 'w')
  f.write("#blackinitials\n")
  for val in parsed_dict["#blackinitials"]:
    f.write(val[0]+ '\n')

  f.write("#whiteinitials\n")
  for val in parsed_dict["#whiteinitials"]:
    f.write(val[0] + '\n')

  f.write("#times\n")
  f.write(' '.join(parsed_dict["#times"][0]) + '\n')

  f.write("#blackturns\n")
  f.write(' '.join(parsed_dict["#blackturns"][0]) + '\n')

  f.write("#positions\n")
  f.write(' '.join(parsed_dict["#positions"][0]) + '\n')

  f.write("#blackwins\n")
  for win in parsed_dict["#blackwins"]:
    f.write(' '.join(win) + '\n')
  f.close()

def read_winning_move(file_path):
  f = open(file_path, 'r')
  lines = f.readlines()
  f.close()

  for line in lines:
    if ("First winning move" in line):
      split_line = line.split(" ")
      return split_line[-1].strip("\n")
    if ("Plan not found" in line):
      return -1

# depending on the board position, corresponding symbol is returned:
def get_symbol(position, parsed_dict):
  position_symbol = parsed_dict['#positions'][0][position]
  if [position_symbol] in parsed_dict['#blackinitials']:
    return 'x'
  elif [position_symbol] in parsed_dict['#whiteinitials']:
    return 'o'
  else:
    return '-'



# Printing the board looking the parsed state of the board:
def print_board(board_size, parsed_dict):
  spaces = board_size + 1

  for i in range(1, board_size+1):
    temp_string = ''
    for j in range(spaces):
      temp_string += "  "
    for j in range(i):
      # Mapping to the linear position sequence:
      mapped_i = j
      mapped_j = (board_size - i) + j
      position = (board_size*mapped_i)+ mapped_j
      cur_symbol = get_symbol(position, parsed_dict)
      temp_string += cur_symbol
      temp_string += "   "
    print(temp_string)
    spaces -= 1
  spaces += 2

  for i in range(1,board_size):
    temp_string = ''
    for j in range(spaces):
      temp_string += "  "
    for j in range(board_size-i):
      mapped_i = i+j
      mapped_j = j
      position = (board_size*mapped_i)+ mapped_j
      cur_symbol = get_symbol(position, parsed_dict)
      temp_string += cur_symbol
      temp_string += "   "
    print(temp_string)
    spaces += 1


# Main:
if __name__ == '__main__':
  text = "Plays interactively if a winning strategy is found for given depth, Q-sage is black player and takes the first move"
  parser = argparse.ArgumentParser(description=text,formatter_class=argparse.RawTextHelpFormatter)
  parser.add_argument("--problem", help="problem file path", default = 'testcases/Hein_hex/hein_04_3x3-05.pg')
  parser.add_argument("--depth", help="Depth, default 3", type=int,default = 3)

  args = parser.parse_args()
  # Reading the input problem file
  parsed_dict = parse(args.problem)
  board_size = int(math.sqrt(len(parsed_dict['#positions'][0])))

  # Initializing open moves:
  open_moves = []
  for move in parsed_dict['#positions'][0]:
    if ([move] not in parsed_dict['#blackinitials'] and [move] not in parsed_dict['#whiteinitials']):
      open_moves.append(move)
  #print(open_moves)



  print("Q-sage plays with symbol 'x', and with the goal to connect bottom left to top right")
  print("Finding a winning strategy...")

  # Repeat the loop of running until either winning configuration is reached
  while (args.depth > 0):
    temp_input_file = "intermediate_files/interactive_problem_file"
    # Writing to temporary intermediate file:
    print_to_file(temp_input_file, parsed_dict)
    command = "python3 Q-sage.py --run 2 --ignore_file_depth 1 --depth " + str(args.depth) + " --problem " + temp_input_file + " > intermediate_files/interactive_output"
    subprocess.run([command], shell = True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT ,check=True)
    winning_move = read_winning_move("intermediate_files/interactive_output")
    if (winning_move == -1):
      print("Not deep enough, winning strategy not found")
      exit()
    else:
      print("Winning strategy found, Q-sage plays move: ",winning_move)
      # updating the dictionary with black move:
      parsed_dict["#blackinitials"].append([winning_move])
      # Updating the open moves:
      open_moves.remove(winning_move)
      print_board(board_size, parsed_dict)
      args.depth = args.depth - 2
      if (args.depth <= 0):
        print("Q-sage wins! game complete")
      else:
        # Looping until valid move is played:
        while(1):
          # printing the available moves:
          print("Available moves: ", open_moves)
          white_move = input("Enter your move: ")
          if white_move in open_moves:
            # updating the dictionary with white move:
            parsed_dict["#whiteinitials"].append([white_move])
            # Updating open moves:
            open_moves.remove(white_move)
            break
          else:
            print("\nNot a valid open move, try again")