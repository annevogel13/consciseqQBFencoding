# Irfansha Shaik, 07.07.2022, Aarhus

import argparse
import glob
import os
from pathlib import Path

# Main:
if __name__ == '__main__':
  text = "Takes SGF hex file and generators Gex,R-Gex,MR-Gex inputs in different formats"
  parser = argparse.ArgumentParser(description=text,formatter_class=argparse.RawTextHelpFormatter)
  parser.add_argument("--input_file", help="SGF hex file, either of a tournament or simply a set of games")
  parser.add_argument("--output_dir", help="path to output directory", default = "intermediate_files/output")
  parser.add_argument("--unrolling_depth", help="number of move to unroll the game, default 1", type=int, default = 1)
  parser.add_argument("--instance_depth", help="gex input depth, default 11", type=int, default = 11)
  parser.add_argument("--only_upto_rgex", help=" MR-Gex and minimal hyper graph are hard to compute so we can disable them, default 1", type=int, default = 1)
  args = parser.parse_args()


  #=====================================================================================================================================
  # Checking if intermediate_files exists:
  if not Path("intermediate_files").is_dir():
    print("Creating intermediate_files directory")
    os.mkdir("intermediate_files")

  # Checking if intermediate_files/B-Hex directory exists:
  if not Path("intermediate_files/B-Hex").is_dir():
    print("Creating intermediate_files/B-Hex directory")
    os.mkdir("intermediate_files/B-Hex")

  #=====================================================================================================================================
  # Checking if out directory exits:
  if not Path(args.output_dir).is_dir():
    print("Invalid output directory path: " + args.output_dir)
    print("Creating new output directory with same path.")
    os.mkdir(args.output_dir)
  #=====================================================================================================================================

  #=====================================================================================================================================
  # tournament_parse script reads from intermediate_files/games_list.txt;
  # so writing to the games list file:
  # reading and writing, instead of copying the file directly:
  f_input = open(args.input_file, "r")
  input_lines = f_input.readlines()
  f_input.close()

  f_parsed_game_output = open("intermediate_files/games_list.txt", "w")
  for line in input_lines:
    f_parsed_game_output.write(line)
  f_parsed_game_output.close()

  print("======================================================================")
  # generating parsed games list:
  print("Parsing the SGF file...")
  print("Generating parsed games list...")

  parse_command = "python3 tournment_parse.py"
  os.system(parse_command)
  print("Parse complete")
  print("======================================================================")
  #=====================================================================================================================================
  # Generating B-Hex files using generate_gex_human_games.py:

  print("Generating B-Hex files...")
  bhex_generation_command = "python3 generate_gex_human_games.py --unrolling_depth " + str(args.unrolling_depth)
  os.system(bhex_generation_command)
  # printing number of files generated:
  bhex_files_list = glob.glob(os.path.join("intermediate_files/B-Hex", "*"))

  bhex_copy_command = "cp -r intermediate_files/B-Hex/ " + args.output_dir + "/"
  os.system(bhex_copy_command)
  print("Complete, number of files created: ", len(bhex_files_list))
  print("======================================================================")
  #=====================================================================================================================================
  # Generate R-Gex, and only consider reachable instances
  print("Generating R-GEX files...")
  reachable_instances = []
  # Generating R-Gex directory:
  if not Path(args.output_dir + "/R-Gex").is_dir():
    print("Creating new R-Gex directory in output folder.")
    os.mkdir(args.output_dir + "/R-Gex")

  # Generating R-Gex/Gex-format directory:
  if not Path(args.output_dir + "/R-Gex/Gex-format").is_dir():
    print("Creating new R-Gex/Gex-format directory in output folder.")
    os.mkdir(args.output_dir + "/R-Gex/Gex-format")


  print("Computing reachable R-Gex instances...")
  print("Writing to R-Gex/Gex_format folder in output folder in Gex format...")
  for file in bhex_files_list:
    cur_instance_name = file.split("/")[-1]
    # best to write to a file and read the contents:
    rgex_command = "python3 transform_hex_board.py  --prune_unreachable_nodes 1  --compute_distances 1 --ignore_file_depth 1 --problem " +  file + " --depth " + str(args.instance_depth) + " > intermediate_files/cur_gex_file"
    #print(rgex_command)
    os.system(rgex_command)
    #print(file)
    # if file is not empty then we write it to the R-gex file and remember its name for next computations:
    if (os.stat("intermediate_files/cur_gex_file").st_size != 0):
      rgex_file_name = "depth_" + str(args.instance_depth) + "_" + cur_instance_name
      copy_command  = "cp intermediate_files/cur_gex_file " + args.output_dir + "/R-Gex/Gex-format/" + rgex_file_name
      os.system(copy_command)
      reachable_instances.append(cur_instance_name)
  print("Complete, number of reachable instances found: ", len(reachable_instances))
  print("---------------------------------------------------------------------")
  #-------------------------------------------------------------------------------------------------------------------------------------
  # first generating the EGF-format directory:
  # Generating R-Gex/EGF-format directory:
  if not Path(args.output_dir + "/R-Gex/EGF-format").is_dir():
    print("Creating new R-Gex/EGF-format directory in output folder.")
    os.mkdir(args.output_dir + "/R-Gex/EGF-format")
  print("Writing to R-Gex/EGF-format folder in output folder in EGF format...")
  # Generate R-Gex in EGF-format
  for file in reachable_instances:
    # we use the transform_hex_board.py to print in EGF-fromat:
    rgex_egf_command = "python3 transform_hex_board.py --compute_distances 1 --output_format egf --problem " + args.output_dir + "/R-Gex/Gex-format/depth_" + str(args.instance_depth) + "_" + file + " > " + args.output_dir + "/R-Gex/EGF-format/depth_"  + str(args.instance_depth) + "_" + file
    #print(rgex_egf_command)
    os.system(rgex_egf_command)
  print("Complete.")
  print("======================================================================")
  #=====================================================================================================================================
  # Generate Gex, and only reachable instances (in Gex-format and EGF-format)
  print("Generating GEX files...")
  # Generating Gex directory:
  if not Path(args.output_dir + "/Gex").is_dir():
    print("Creating new Gex directory in output folder.")
    os.mkdir(args.output_dir + "/Gex")
  # Gex in Gex-format:
  # Generating Gex/Gex-format directory:
  if not Path(args.output_dir + "/Gex/Gex-format").is_dir():
    print("Creating new Gex/Gex-format directory in output folder.")
    os.mkdir(args.output_dir + "/Gex/Gex-format")
  print("Writing to Gex/Gex-format folder in output folder in Gex format...")
  # Generate R-Gex in Gex-format
  for file in reachable_instances:
    # we use the transform_hex_board.py to print in Gex-fromat:
    rgex_egf_command = "python3 transform_hex_board.py --ignore_file_depth 1 --problem intermediate_files/B-Hex/" + file + " --depth " + str(args.instance_depth) + " > " + args.output_dir + "/Gex/Gex-format/depth_"  + str(args.instance_depth) + "_" + file
    #print(rgex_egf_command)
    os.system(rgex_egf_command)
  print("Complete.")
  print("---------------------------------------------------------------------")
  #-------------------------------------------------------------------------------------------------------------------------------------
  # Gex in EGF-format:
  # Generating Gex/EGF-format directory:
  if not Path(args.output_dir + "/Gex/EGF-format").is_dir():
    print("Creating new Gex/EGF-format directory in output folder.")
    os.mkdir(args.output_dir + "/Gex/EGF-format")
  print("Writing to Gex/EGF-format folder in output folder in EGF format...")
  # Generate R-Gex in EGF-format
  for file in reachable_instances:
    # we use the transform_hex_board.py to print in EGF-fromat:
    rgex_egf_command = "python3 transform_hex_board.py --output_format egf --ignore_file_depth 1 --problem intermediate_files/B-Hex/" + file + " --depth " + str(args.instance_depth) + " > " + args.output_dir + "/Gex/EGF-format/depth_"  + str(args.instance_depth) + "_" + file
    #print(rgex_egf_command)
    os.system(rgex_egf_command)
  print("Complete.")
  print("======================================================================")
  #=======================================================================================================================================
  # we only need to generate if the flag is disabled:
  if (args.only_upto_rgex == 0):
    #=====================================================================================================================================
    # Generate MR-Gex, and only reachable instances (in Gex-format and EGF-format)
    print("Generating MR-GEX files...")
    print("Warning: Can take long time for deeper games to compute minimal simple paths!")
    # Generating MR-Gex directory:
    if not Path(args.output_dir + "/MR-Gex").is_dir():
      print("Creating new MR-Gex directory in output folder.")
      os.mkdir(args.output_dir + "/MR-Gex")
    # MR-Gex in Gex-format:
    # Generating MR-Gex/Gex-format directory:
    if not Path(args.output_dir + "/MR-Gex/Gex-format").is_dir():
      print("Creating new MR-Gex/Gex-format directory in output folder.")
      os.mkdir(args.output_dir + "/MR-Gex/Gex-format")
    print("Writing to MR-Gex/Gex-format folder in output folder in Gex format...")
    # Generate MR-Gex in Gex-format
    for file in reachable_instances:
      # we use the transform_hex_board.py to print in Gex-fromat:
      # we use the R-Gex directly to compute the MR-Gex:
      mrgex_command = "python3 transform_hex_board.py  --compute_distances 1 --prune_unreachable_nodes 1 --prune_minimal_path_unreachable_nodes 1 --problem " + args.output_dir + "/R-Gex/Gex-format/depth_"  + str(args.instance_depth) + "_" + file + " > " + args.output_dir + "/MR-Gex/Gex-format/depth_"  + str(args.instance_depth) + "_" + file
      #print(mrgex_command)
      os.system(mrgex_command)
    print("Complete.")
    print("---------------------------------------------------------------------")
    #-------------------------------------------------------------------------------------------------------------------------------------
    # MR_Gex in EGF-format:
    # Generating MR-Gex/EGF-format directory:
    if not Path(args.output_dir + "/MR-Gex/EGF-format").is_dir():
      print("Creating new MR-Gex/EGF-format directory in output folder.")
      os.mkdir(args.output_dir + "/MR-Gex/EGF-format")
    print("Writing to MR-Gex/EGF-format folder in output folder in EGF format...")
    # Generate MR-Gex in EGF-format
    for file in reachable_instances:
      # we use the transform_hex_board.py to print in EGF-fromat:
      # using already computed MR-Gex files to avoid redundant computation:
      mrgex_egf_command = "python3 transform_hex_board.py --compute_distances 1 --output_format egf --problem " + args.output_dir + "/MR-Gex/Gex-format/depth_"  + str(args.instance_depth) + "_" + file + " > " + args.output_dir + "/MR-Gex/EGF-format/depth_"  + str(args.instance_depth) + "_" + file
      #print(mrgex_egf_command)
      os.system(mrgex_egf_command)
    print("Complete.")
    print("======================================================================")
    #=====================================================================================================================================
    # Generate PG_format (hypergraph), and only reachable instances
    # Generating PG-format directory:
    if not Path(args.output_dir + "/PG-format").is_dir():
      print("Creating new PG-format directory in output folder.")
      os.mkdir(args.output_dir + "/PG-format")
    print("Writing to PG-format folder in output folder in PG format...")
    # Generate Minimal hypergraph in PG-format
    for file in reachable_instances:
      # we use the generate_hypergraph.py to print in PG-fromat:
      # we use the MR-Gex to compute, to avoid redundant computation:
      pgformat_command = "python3 generate_hypergraph.py --problem " + args.output_dir + "/MR-Gex/Gex-format/depth_"  + str(args.instance_depth) + "_" + file + " > " + args.output_dir + "/PG-format/depth_"  + str(args.instance_depth) + "_" + file
      os.system(pgformat_command)
    print("Complete.")
    print("======================================================================")
    #=====================================================================================================================================
  #=======================================================================================================================================
  # Generate white flipped B-Hex, and only reachable instances (in EGF-format)
  print("Generating White flipped B-Hex files...")
  # Generating White flipped directory:
  if not Path(args.output_dir + "/White_flipped").is_dir():
    print("Creating new White flipped directory in output folder.")
    os.mkdir(args.output_dir + "/White_flipped")
  # White flipped in Gex-format:
  # Generating White_flipped/B-Hex directory:
  if not Path(args.output_dir + "/White_flipped/B-Hex").is_dir():
    print("Creating new /White_flipped/B-Hex directory in output folder.")
    os.mkdir(args.output_dir + "/White_flipped/B-Hex")
  print("Writing to /White_flipped/B-Hex folder in output folder in Gex format...")
  # Generate Minimal hypergraph in PG-format
  for file in reachable_instances:
    # we use the flip_white_black_players.py:
    flip_wb_command = "python3 flip_white_black_players.py --problem intermediate_files/B-Hex/" + file + " > " + args.output_dir + "/White_flipped/B-Hex/" + file
    os.system(flip_wb_command)
  print("Complete.")
  print("---------------------------------------------------------------------")
  #=====================================================================================================================================
  # Generate white flipped Gex, and only reachable instances (in EGF-format)
  # Generating White_flipped/B-Hex directory:
  if not Path(args.output_dir + "/White_flipped/Gex_EGF-format").is_dir():
    print("Creating new /White_flipped/Gex_EGF-format directory in output folder.")
    os.mkdir(args.output_dir + "/White_flipped/Gex_EGF-format")
  print("Writing to /White_flipped/Gex_EGF-format folder in output folder in EGF format...")
  # Generate Gex in EGF-format
  for file in reachable_instances:
    # we use the transform_hex_board.py to print in Gex-fromat:
    wb_gex_egf_command = "python3 transform_hex_board.py --ignore_file_depth 1 --drop_start_end_board_edges 0 --output_format egf --problem " + args.output_dir + "/White_flipped/B-Hex/" + file + " --depth " + str(args.instance_depth) + " > " + args.output_dir + "/White_flipped/Gex_EGF-format/depth_"  + str(args.instance_depth) + "_" + file
    #print(rgex_egf_command)
    os.system(wb_gex_egf_command)
  print("Complete.")
  print("======================================================================")
  #=====================================================================================================================================
  # Generate white flipped R-Gex, and only reachable instances (in EGF-format)
  if not Path(args.output_dir + "/White_flipped/R-Gex_EGF-format").is_dir():
    print("Creating new /White_flipped/R-Gex_EGF-format directory in output folder.")
    os.mkdir(args.output_dir + "/White_flipped/R-Gex_EGF-format")
  print("Writing to /White_flipped/R-Gex_EGF-format folder in output folder in EGF format...")
  # Generate R-Gex in EGF-format
  for file in reachable_instances:
    # we use the transform_hex_board.py to print in R-Gex-fromat:
    wb_rgex_egf_command = "python3 reachability_white_flipped.py --r_gex_problem " + args.output_dir + "/R-Gex/EGF-format/depth_"  + str(args.instance_depth) + "_" + file + " --white_flipped_bhex_problem " + args.output_dir + "/White_flipped/B-Hex/" + file + " > " + args.output_dir + "/White_flipped/R-Gex_EGF-format/depth_"  + str(args.instance_depth) + "_" + file
    #print(wb_rgex_egf_command)
    os.system(wb_rgex_egf_command)
  print("Complete.")
  print("======================================================================")
  # removing intermediate files folder:
  os.system("rm -r intermediate_files")
  #=====================================================================================================================================
