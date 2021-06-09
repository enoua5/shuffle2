#!/usr/bin/env python3

import sys, argparse

class ShuffleInter:
  def __init__(self):
    self.allow_bracket = False
    self.p1_cards = []
    self.p2_cards = []
    self.pointer = {"x": 0, "y": 0}
    self.memory = [[0]]
  def printMem(self):
    for l in self.memory:
      for i in l:
        print(i, end=" ")
      print()
  def realign_memory(self):
    if self.pointer["y"] >= len(self.memory):
      for i in range(self.pointer["y"] + 1 - len(self.memory)):
        self.memory.append([0] * len(self.memory[0]))
        
    if self.pointer["y"] < 0:
      for i in range(-self.pointer["y"]):
        self.memory.insert(0, [0] * len(self.memory[0]))
      self.pointer["y"] = 0
        
    if self.pointer["x"] >= len(self.memory[0]):
      for line in self.memory:
        line += [0] * (self.pointer["x"] + 1 - len(line))
        
    if self.pointer["x"] < 0:
      for line in range(len(self.memory)):
        self.memory[line] = ([0] * -self.pointer["x"]) + self.memory[line]
      self.pointer["x"] = 0
        
     
      
    
class Card:
  def __init__(self, suit, value):
    if not(suit in "shdcj"):
      raise ValueError
    if value < 0:
      raise ValueError
    self.suit = suit
    self.value = value
  def print(self):
    print(self.suit + str(self.value))

def parseMemory(s):
  out = []
  lines = s.split("\n")
  
  max_line_length = 0
  for line in lines:
    parsed_line = []
    nums = line.split()
    for n in nums:
      try:
        number = int(n)
        if number > 255 or number < 0:
          print("Syntax Error: values in initial state must be in range 0-255")
          sys.exit(1)
        parsed_line.append(number)
      except ValueError:
        print("Syntax Error: invalid number in initial state definition:", n)
        sys.exit(1)
    if(len(parsed_line) > max_line_length):
      max_line_length = len(parsed_line)
    out.append(parsed_line)
  # normalize line lengths
  for line in out:
    if len(line) != max_line_length:
      line += [0] * (max_line_length - len(line))
  return out
  
  
def parsePointer(s):
  nums = s.split()
  if len(nums) != 2:
    print("Syntax Error: initial pointer position must contain 2 values")
  try:
    return {"x": int(nums[0]), "y": int(nums[1])}
  except ValueError:
    print("Syntax Error: could not parse pointer position")
    sys.exit(1)

def parseDeck(deck, allow_bracket):
  out = []
  parsing_bracket = False
  bracket_suit = ''
  bracket_num = ''
  
  for c in deck:
    point = ord(c)
    if not(parsing_bracket) and point >= 0x1f0a1 and point <= 0x1f0df:
      valid = True
      val = point % 16
      suit = "shdc"[(int(point/16)%16)-10]
      if val == 15 or val == 0:
        val = 0
        suit = 'j'
      # knight
      elif val == 12:
        valid = False
      # shift the value down to account for removing the knight
      elif val > 12:
        val -= 1
      
      if valid:
        out.append(Card(suit, val))
      
    if allow_bracket:
      if c == '[':
        if parsing_bracket:
          print("Syntax Error: unexpected token '['")
          sys.exit(1)
        else:
          parsing_bracket = True
      elif parsing_bracket:
        if c == ']':
          try:
            out.append(Card(bracket_suit, int(bracket_num)))
          except ValueError:
            print("Syntax Error: bracket card contains invalid number or suit")
            print("Suit: ", bracket_suit)
            print("Number: ", bracket_num)
            sys.exit(1)
          parsing_bracket = False
          bracket_suit = ''
          bracket_num = ''
        elif bracket_suit == '':
          bracket_suit = c
        else:
          bracket_num += c
  return out

def version():
  print("2.0.0")

def main():
  shuff = ShuffleInter()

  # parse command line arguments
  parser = argparse.ArgumentParser()
  parser.add_argument('-v', action="store_true", help="show version number")
  parser.add_argument('-b', action="store_true", help="allow bracket notation in program")
  parser.add_argument('-l', action="store_true", help="run in legacy mode, disabling all v2.0 features")
  parser.add_argument('ifile', help="file containing the program to be interpreted")
  args = parser.parse_args()
  
  if(args.v):
    version()
  if(args.b):
    if(args.l):
      print("Error: -b and -l are not compatible")
      sys.exit(1)
    shuff.allow_bracket = True
    
  # parse the file
  try:
    ifile = open(args.ifile, 'r', encoding='utf-8')
  except FileNotFoundError:
    print("Error: no such file'"+args.ifile+"'")
    sys.exit(1)
  read = ifile.read()
  ifile.close()
  
  sections = read.split("\n\n")
  
  if len(sections) != 2 and len(sections) != 4:
    print("Syntax Error: program file must have either 2 or 4 sections")
    sys.exit(1)
  elif args.l and len(sections) == 4:
    print("Syntax Error: 4 section program files are not compatible with -l flag")
  
  shuff.p1_cards = parseDeck(sections[0], args.b)
  shuff.p2_cards = parseDeck(sections[1], args.b)
  if len(sections) == 4:
    shuff.pointer = parsePointer(sections[2])
    shuff.memory = parseMemory(sections[3])
  shuff.realign_memory()
  shuff.printMem()
  print(shuff.pointer)
  
  
if __name__ == "__main__":
  main()