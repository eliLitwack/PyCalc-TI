#enter the filepath of the python script to be compiled
FILE_PATH = ["Your File Path"]
#
#       Py4Calc for TI 83/84, Version 0.2.3
#       By Luke Bryan
#       Updated to run in Python 3.x by Elias Litwack
#       Turns simple Python code into TI-Basic that compiles into .8xp programs for TI 83/84.
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.

#New in 0.2.3: compiler can run using python 3.x interpreters, GUI depricated
#New in 0.2: Many bug fixes, line numbers are included in warnings and errors, more useful warnings,
#new feature lets you make a line of code Python-only (with #no-ti comment),
#You can also include TI-basic in a comment, such as #ti:<some ti code here>
import sys
import os

#GUI:

GUI_MODE = False
TAB_REPLACE = "    "

def main():
	args = FILE_PATH
	global GUI_MODE
	
	print(args)
	if (len(args)==0):
		GUI_MODE=True
		root = tk.Tk()
		root.withdraw()
		inp = tkFileDialog.askopenfilename(title="Select a python script to convert")
		if (inp==''):
			print("cancelled")
			return 0
	else:
		inp=args[0]
	
	#now input file is known
	
	file=open(inp)
	prog = file.read().replace("\r","").split("\n") # Lines of code
	
	#Get a program name:
	if (prog[0][:1]=="#" and (prog[0].upper().find("NAME:")>-1 or prog[0].upper().find("PROGRAM:")>-1 )):
		outname=prog[0][prog[0].find(":")+1:]
	else:
		outname=input("What do you want to name this program?")
	fixed = format(prog)
	
	#Write the converted program in this folder:
	print("\n--Converted to TI-Basic code:--")
	print(fixed)
	print("")
	print("Making output files: "+outname+".tib, "+outname+".8xp ...")
	
	outfile=open(outname+".tib","w")
	outfile.write(fixed)
	outfile.close()
	
	#assuming the compiler tibasic.exe is in this folder:
	if (sys.platform[:3]=="win"):
		if (os.system('tibasic.exe '+outname+'.tib')): #Returns non-0, error:
			errReport("Error trying to run tibasic.exe! Make sure it is in the current folder.")
	else:
		if (os.system('wine tibasic.exe '+outname+'.tib')): #Returns non-0, error:
			errReport("Error trying to run tibasic.exe! Make sure it is in the current folder, and w.i.n.e is installed.\n"+
			"(See http://www.winehq.org/ for installer)")
	
	a=input("Done! Press enter to exit:") #pause
	return 0

def format(linesArray): #converts lines from Python to ti-basic.
	for i in range(len(linesArray)):
		linesArray[i]=linesArray[i].replace("\t",TAB_REPLACE) #Important! see idepth()
	i=0;
	linesArray.append("") # 0-indent ending so blockAddEnd won't mess up.
	while (i<len(linesArray)):
		line = linesArray[i]
		
		if isBlockStart(line,"for "):
			linesArray = blockAddEnd(linesArray, i, "End")
		elif isBlockStart(line,"if "):
			linesArray = blockAddEnd(linesArray, i, "End")
		elif isBlockStart(line,"while "):
			linesArray = blockAddEnd(linesArray, i, "End")
		elif isBlockStart(line,"repeat "): #not in python, but works on TI.
			linesArray = blockAddEnd(linesArray, i, "End")
		i+=1
	# Don't need indentations anymore, do the rest of the conversions:
	for i in range(len(linesArray)):
		linesArray[i]=convLine(linesArray[i],i+1)
	
	#Remove blanks:
	for i in range(linesArray.count("")):
		linesArray.remove("")
	
	return "\n".join(linesArray)

def convLine(line,num): #Line by line conversion.
	line = line.rstrip().lstrip() #trim indentation.
	lnum = "Line "+str(num)+": "
	
	if (replace(line,"#","") != line):
		comment = line[line.find("#"):]
		if (comment[0:6] == "#no-ti"):
			#Does not work on the ti.
			return ""
		elif (comment[0:4] == "#ti:"):
			# Only for ti:
			return comment[4:]
		else:
			line = line[:line.find("#")] # take comment off code
	
	#Errors and warnings:
	if (toolong(line)):
		print(lnum+"Warning: Text string too long to fit on a TI83/84 screen. The calculator screen is 16 characters wide, 8 characters high.")
	if (line.find("\n")>-1):
		print(lnum+"Warning: newline \\n is not allowed in TI-Basic.")
	if (line.find("'''")>-1):
		print(lnum+"Warning: ''' quotes are not allowed, you must use \" quotes on a single line for TI-Basic.")
	if (replace(line,"pow(","")!=line):
		errReport(lnum+"TI calculators don't have the pow() command, you must use a**b instead of pow(a,b).")
	if (replace(line,"import ","")!=line):
		print(lnum+"import ignored. No import statements in TI-Basic!")
		return "" # ignore import statements!
	if (replace(line,"-=","")!=line):
		errReport(lnum+"The -= operator is not allowed.\nTry +=- or a=a+-number instead.")
	if (replace(line,"def ","")!=line):
		errReport(lnum+"Functions are not supported in TI-Basic! However, you can run another program with \"prgmPRGNAME\".")
	if (replace(line,"//","")!=line):
		print(lnum+"// division converted to / division: For int division, try int(a/b).")
		line=replace(line,"//","/")
	if (replace(line,"-","")!=line):
		print(lnum+"Warning: The - is changed to negative sign on the calculator. If you wanted to subtract, use a+-b instead of a-b.")
	if (replace(line,"open(","")!=line):
		errReport(lnum+"Error: TI calculators can't use \"open(filename)\" in programs. To store text, try using variables STR0, STR1, ... STR9.")
	if (replace(line,"%","")!=line):
		errReport(lnum+"Error: TI83/84 calculators don't have Mod.\n Instead of a % b, try (a/b-int(a/b))*b instead.")
	
	# Replace excess spaces, they cause errors in the calculator:
	line=replace(line,", ",",")
	line=replace(line," + ","+")
	line=replace(line," - ","-")
	line=replace(line," +- ","+-")
	line=replace(line," * ","*")
	line=replace(line," / ","/")
	line=replace(line," == ","==")
	line=replace(line," > ",">")
	line=replace(line," < ","<")
	line=replace(line," != ","!=")
	
	
	#TODO: Arrays converted to lists?
	
	
	line=replace(line,"theta","[theta]") # variable
	line=replace(line,"**","^")
	
	line=mathReplace(line)
	
	#round, max, min already works.
	line=replace(line,"float(","(")
	line=replace(line,"len(","dim(")
	line=replace(line,"math.pi","[pi]")
	line=replace(line,"math.e","[e]")
	line=replace(line,"eval(","expr(")
	line=replace(line,"-","[neg]") # use +- instead of - operator.
	line=replace(line,"==","=")
	line=replace(line," and ","&")
	line=replace(line," or ","|")
	line=replace(line,"random.random()","rand")
	line=replace(line,"random.randint","RandInt")
	line=replace(line,"int(","iPart(")
	
	if (replace(line,"input(","") != line):
		line=inputConv(line,num)
	
	if isBlockStart(line,"for "):
		line=forConv(line,num)
	elif (isBlockStart(line,"if ")):
		line = replace(line,"if ","If ")
		line = replace(line,":",":Then")
	elif (isBlockStart(line,"while ")):
		line = replace(line,"while ","While ")
		line = replace(line,":","")
	elif (isBlockStart(line,"repeat")):
		line = replace(line,"repeat","Repeat")
		line = replace(line,":","")
	elif (isBlockStart(line,"else")):
		line = replace(line,"else:","Else")
	elif isBlockStart(line,"elif"):
		errReport(lnum+"""Error: There is no else-if command on the TI83/84. However, you can use this instead:
if <condition>:
  ...
else:
  if <condition>:
    ...
  else:
    ...""")
	elif (line.find("print ")==idepth(line)):
		line = replace(line,"print ","Disp ")
		if (line[-1] == ","):
			line = line[:-1].rstrip() # Trailing , not legal for ti basic.
	elif (replace(line,"=","")!=line): #assignment is -> on the calculator.
		eqspace = line.find("=")
		line = line[eqspace+1:].rstrip().lstrip() + "->" + line[:eqspace].rstrip().lstrip() # sto arrow.
		line = fixEQ(line)
	return replace(line,"+[neg]","-") #lastly, switch back the negative.

def fixEQ(line):
	# fix +=, *=, /=.
	# A+=1 changes to 1->A+, so fix it now.
	if (line[-1]=="+" or line[-1]=="*" or line[-1]=="/"):
		line = line[:-1].rstrip()+line[-1] # remove any spaces in "a  +" etc
		pre = line[line.find("->")+2:]
		#pre = pre[:-1].rstrip()+pre[-1]
		line= pre + "("+line[:line.find("->")]+")"+ line[line.find("->"):-1]
	return line

def inputConv(line,num):
	lnum = "Line "+str(num)+": "
	if (replace(line,"raw_input(","")!=line and line==replace(line,"=","")):
		#raw_input not assigned to variable is like Pause.
		return "Pause "
	else:
		var = line[:line.find("=")].rstrip().lstrip()
		if (len(var)>1 and var!="theta"): # might be invalid.
			print(lnum+"Warning: Program tries to store to variable \"%s\"." % var)
		prompt = line[line.find("input(")+6:]
		prompt = prompt[:prompt.find(")")]
		# Now return the TI basic input with var spaces removed:
		return "Input "+prompt+","+var

def forConv(line,num):
	lnum = "Line "+str(num)+": "
	# split "for i in range(...):"
	var = line[line.find("for ")+4:line.find(" in range")]
	#print var
	part = line[line.find("in range(")+9:] # only "...) : "
	part = part.rstrip(": ")[:-1] # remove extra " " or ":", remove last ).
	#print "'"+line+"'"
	out = part.split(",")
	if len(out)==1:
		return "For(%s,0,(%s)-1)" % (var, out[0])
	elif len(out)==2:
		return "For(%s,(%s),(%s)-1)" % (var, out[0], out[1])
	elif len(out)==3:
		return "For(%s,(%s),(%s)-1,(%s)" % (var, out[0], out[1], out[2])
	else:
		errReport(lnum+"Too many commas in for loop!")
		return "couldn't convert: "+line

def blockAddEnd(lines, startLine, endText):
	# Takes an array, line #, and end text.
	# Adds end for that indentation block.
	startInd = idepth(lines[startLine])
	if idepth(lines[startLine+1]) <= startInd:
		errReport("Expected indent after line "+str(startLine+1)+".")
	i = startLine+1
	#continue searching for the end while it's indented or it's an else line:
	while idepth(lines[i]) > startInd or (isBlockStart(lines[i],"else")):
		i+=1
	# now insert.
	lines.insert(i,endText)
	return lines

def idepth(text):
	# get indentation depth of line.
	depth=0
	line = text.replace("\t",TAB_REPLACE) #tab is 4 spaces.
	while (line[:1]==" "):
		line=line[1:]
		depth+=1
	return depth

def replace(text, changethis, tothis):
	# replaces text, but not in quotes.
	arr = text.split("\"")
	for i in range(0,len(arr),2):
		arr[i]=arr[i].replace(changethis, tothis)
	return "\"".join(arr)

def toolong(text):
	# checks for too long string:
	arr = text.split("\"")
	for i in range(1,len(arr),2):
		#print arr[i]
		if (len(arr[i]) > 16):
			return True
	return False

def parMatch(text,num): # given "(stuff()...()))", returns the parentheses block.
	lnum = "Line "+str(num)+": "
	for i in range(len(text)):
		part = text[:i-1]
		if (part.count("(")==part.count(")")):
			return part[1:-1] #without outside parentheses.
	errReport(lnum+"Invalid parentheses")

def isBlockStart(line, type):
	# Check if the line is start of a <type> block.
	# checks if it starts with <type>, and ends with ":".
	# example: isBlockStart("for i in range(8) : ","for") is true.
	return (line.find(type) == idepth(line) and line.rstrip(" ")[-1]==":")

def errReport(text):
	print(text)
	if (GUI_MODE):
		root = tk.Tk()
		root.withdraw()
		tkMessageBox.showerror("Error",text)
	sys.exit(1)

def mathReplace(line):
	line=replace(line,"math.sqrt(","[root]^2(")
	line=replace(line,"math.fabs(","abs(")
	line=replace(line,"math.sin(","sin(")
	line=replace(line,"math.cos(","cos(")
	line=replace(line,"math.tan(","tan(")
	line=replace(line,"math.asin(","asin(")
	line=replace(line,"math.acos(","acos(")
	line=replace(line,"math.atan(","atan(")
	line=replace(line,"math.sinh(","sinh(")
	line=replace(line,"math.cosh(","cosh(")
	line=replace(line,"math.tanh(","tanh(")
	line=replace(line,"math.asinh(","asinh(")
	line=replace(line,"math.acosh(","acosh(")
	line=replace(line,"math.atanh(","atanh(")
	line=replace(line,"math.log(","ln(")
	line=replace(line,"math.exp(","e^(")
	line=replace(line,"math.floor(","int(")
	line=replace(line,"math.log10(","log(")
	
	#same, but without "math." They might use
	#from math import sqrt etc...
	line=replace(line,"sqrt(","[root]^2(")
	line=replace(line,"fabs(","abs(")
	#(Redundant lines deleted)
	line=replace(line,"log(","ln(")
	line=replace(line,"exp(","e^(")
	line=replace(line,"floor(","int(")
	line=replace(line,"log10(","log(")
	
	return line

if __name__ == '__main__': main()
