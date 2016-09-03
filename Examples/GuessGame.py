#Program:GUESS
#A small guessing game.
import random #no-ti
print "Guess the number"
print "from 0 to 100"
g = int(raw_input(""))
a = random.randint(0,100)
while (g != a):
    if (g>a):
        print "Too high."
    else:
        print "Too low."
    g=int(raw_input("Guess:"))
print "Right!"
