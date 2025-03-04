import argparse

# Main:
if __name__ == '__main__':
  text = "Takes a hex board"
  parser = argparse.ArgumentParser(description=text,formatter_class=argparse.RawTextHelpFormatter)
  parser.add_argument("--input", help="stats file path")
  parser.add_argument("--output", help="output file path")
  args = parser.parse_args()


  # Now filling up the stats dictionary:
  f_stats = open(args.input, "r")
  stats_lines = f_stats.readlines()
  f_stats.close()

  f_new_file = open(args.output,"w")

  # We gather max memory and time taken:
  max_mem = 0
  cpu_time = 0
  name = ''
  time_out = 0

  stats_dict = {}

  for line in stats_lines:
    # we rest when we find the line with name:
    if ("Name" in line):
      if (name != ''):
        stats_dict[name] = (max_mem,cpu_time)
        #print(name, max_mem)
        if (time_out == 0):
          f_new_file.write(str(name) + " " + str(max_mem) + " " + str(cpu_time) + "\n")
        else:
          f_new_file.write(str(name) + " " + str(max_mem) + " TO\n")
      # creating a new name line:
      name = line.strip("\n").split(" ")[-1]
      #print(name)
      # resetting
      max_mem = 0
      cpu_time = 0
      time_out = 0
    elif ("Max Mem used" in line):
      max_mem_string = line.split(" ")[-2]
      max_mem = round(float(max_mem_string[:-1]),2)
      # gigabites or megabites:
      notation = max_mem_string[-1]
      if (notation == "G"):
        max_mem = max_mem * 1000
        max_mem = round(float(max_mem),2)
    elif ("Used CPU time" in line):
      cpu_time = line.strip("\n").split(" ")[-1]
      split_cpu_time = cpu_time.split(":")
      cpu_time = int(split_cpu_time[2]) + int(split_cpu_time[1])*60 + int(split_cpu_time[0])*3600
      if (cpu_time == 0):
        # avoiding the 0 seconds:
        cpu_time = 0.1
    elif ("State" in line):
      if ("TIMEOUT" in line):
        time_out = 1

  stats_dict[name] = max_mem
  if (time_out == 0):
    f_new_file.write(str(name) + " " + str(max_mem) + " " + str(cpu_time) + "\n")
  else:
    f_new_file.write(str(name) + " " + str(max_mem) + " TO\n")
  #f_new_file.write(str(name) + " " + str(max_mem) + " " + str(cpu_time) + "\n")
  # creating a new name line:
  f_new_file.close()
  #print(stats_dict)
