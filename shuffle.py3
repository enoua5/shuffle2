#!/usr/bin/env python3

import sys, argparse

class ShuffleInter:
  def __init__(self):
    self.allow_bracket = False
    self.p1_cards = []
    self.p2_cards = []
    self.pointer = {"x": 0, "y": 0}
    self.memory = [[0]]
    self.pause = 0
    self.running = True
    self.charInputBuffer = ""
    self.verbose = False
    
  def versay(self, what):
    if(self.verbose):
      print(what) 
  
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
  
  def run(self, p1c, p2c):
    if self.pause <= 0:
      if p1c.suit == "j" or p2c.suit == "j":
        self.versay("abort")
        self.running = False
        return
        
      if p1c.suit == "s":
        # pointer movement instructions
        if p2c.suit == "s":
          # right
          self.versay("right")
          self.pointer["x"] += 1
          
        elif p2c.suit == "c":
          # left
          self.versay("left")
          self.pointer["x"] -= 1
          
        if p2c.suit == "h":
          # down
          self.versay("down")
          self.pointer["y"] += 1
          
        elif p2c.suit == "d":
          # up
          self.versay("up")
          self.pointer["x"] -= 1
        # the pointer might have moved outside of the initialized ares
        self.realign_memory()
      
      elif p1c.suit == "c":
        # IO instructions
        if p2c.suit == "s":
          # input char
          self.versay("input char")
          if len(self.charInputBuffer) > 0:
            inp = self.charInputBuffer
          else:
            inp = input()
          if len(inp) > 0:
            self.memory[self.pointer["x"]][self.pointer["y"]] = ord(inp[0]) % 256
            # pop the first character and set the input buffer
            inp = inp[1:]
            self.charInputBuffer = inp
          else:
            self.memory[self.pointer["x"]][self.pointer["y"]] = 0
            
        elif p2c.suit == "c":
          # input int
          self.versay("input int")
          inp = input()
          if inp.isdigit():
            self.memory[self.pointer["x"]][self.pointer["y"]] = int(inp) % 256
          else:
            self.memory[self.pointer["x"]][self.pointer["y"]] = 0
        elif p2c.suit == "h":
          #output int
          self.versay("output int")
          print(self.memory[self.pointer["x"]][self.pointer["y"]], end="")
        
        elif p2c.suit == "d":
          # output char
          self.versay("output char")
          try:
            print(char(self.memory[self.pointer["x"]][self.pointer["y"]]), end="")
          except UnicodeEncodeError:
            print("?", end="")
            
      elif p1c.suit == "h":
        # jump instuctions
        if p2c.suit == "s":
          # if 0, skip 1
          self.versay("if 0, skip 1")
          if self.memory[self.pointer["x"]][self.pointer["y"]] == 0:
            self.pause = 1
        
        elif p2c.suit == "c":
          # if 0, skip p1c.value
          self.versay("if 0, skip value: " + str(p1c.value))
          if self.memory[self.pointer["x"]][self.pointer["y"]] == 0:
            self.pause = p1c.value
        
        elif p2c.suit == "h":
          # skip p1c.value
          self.versay("skip value: " + str(p1c.value))
          self.pause = p1c.value
        
        elif p2c.suit == "d":
          # skip 1
          self.versay("skip 1")
          self.pause = 1
      
      elif p1c.suit == "d":
        # do math
        if p2c.suit == "s":
          # sub p1c.value
          self.versay("sub " + str(p1c.value))
          self.memory[self.pointer["x"]][self.pointer["y"]] -= p1c.value
        elif p2c.suit == "c":
          # add p1c.value
          self.versay("add " + str(p1c.value))
          self.memory[self.pointer["x"]][self.pointer["y"]] += p1c.value
        if p2c.suit == "h":
          # inc
          self.versay("inc")
          self.memory[self.pointer["x"]][self.pointer["y"]] += 1
        elif p2c.suit == "d":
          # dec
          self.versay("dec")
          self.memory[self.pointer["x"]][self.pointer["y"]] -= 1
          
        self.memory[self.pointer["x"]][self.pointer["y"]] %= 256
            
    else:
      self.pause -= 1
  
  def battle(self):
    p1stakes = []
    p2stakes = []
    p1card = self.p1_cards.pop(0)
    p2card = self.p2_cards.pop(0)
    
    self.run(p1card, p2card)
    
    # compare values and determine winner of battle
    # higher card goes on bottom
    if p1card.value > p2card.value:
      self.p1_cards.append(p2card)
      self.p1_cards.append(p1card)
    elif p2card.value > p1card.value:
      self.p2_cards.append(p1card)
      self.p2_cards.append(p2card)
    # if it's a draw, go to war!
    else:
      tie_resolved = False
      while not(tie_resolved):
        if len(self.p1_cards) > 0 and len(self.p2_cards) > 0:
          # add the current cards to the stake pile
          p1stakes.append(p1card)
          p2stakes.append(p2card)
          # add the three stake cards
          for i in range(3):
            if len(self.p1_cards) > 1:
              p1stakes.append(self.p1_cards.pop(0))
            if len(self.p2_cards) > 1:
              p2stakes.append(self.p2_cards.pop(0))
              
          p1card = self.p1_cards.pop(0)
          p2card = self.p2_cards.pop(0)
          self.run(p1card, p2card)
          
          if p2card.value > p1card.value:
            self.p2_cards += p1stakes + [p1card] + p2stakes + [p2card]
            tie_resolved = True
            
          elif p1card.value > p2card.value:
            self.p1_cards += p2stakes + [p2card] + p1stakes + [p1card]
            tie_resolved = True
          
          # else continue war
          
    
  def step(self):
    if len(self.p1_cards) == 0 or len(self.p2_cards) == 0:
      self.running = False
      return
    self.battle()
        
     
      
    
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
  parser.add_argument("-s", type=int, default=-1, help="Only run S steps before stopping")
  parser.add_argument("--verbose", action="store_true", help="show plenty of runtime information")
  parser.add_argument('ifile', help="file containing the program to be interpreted")
  args = parser.parse_args()
  
  shuff.verbose = args.verbose
  
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
  
  steps = args.s
  while shuff.running and steps != 0:
    if steps > 0:
      steps -= 1
    shuff.step()
  
if __name__ == "__main__":
  main()
