UPDATE:
Currently the structure to launch a game with certain parameters and repeatedly are in place and functional. 
The prediction mechanism is not functional in any way and immediately crashes.
The next step is to fix the prediction mechanisms to make them minimally functional i.e. can at least choose random moves.
At this point I should clean up the repo, put files in actual directories and actually organize the files, add comments to code so they arent just blobs (even if its not the most complicated code idc comment everything), etc. etc.
Then you can restructure the code to be more modular so switching between prediction mechanisms is possible and start adding more features/improving existing ones.

BIG TODO: Go through all the files and assign an authorship to it
          Clean up the repo. There are many unnecessary files

TLDR - If someone says they are "working" and "dont need help" they might be lying




To use this, create a folder in TBAnalyzed that will contain the games for a certain team. 

./stripper <folder name>
--This will go through all games in the folder and create/add to a folder of that same name in "ProcessedGames"
--The html files will be deleted once all the important info is stripped (not deleting yet in case i want more info)
--This is compiled from text_stripper.c


./reader <folder name>
--This will go through the games in said folder and create a game summary of the team in "Game_Profiles"
--The battle file will not be deleted, in case the game summary becomes updated
--This is compiled from text_reader.c


python project_main.py 
--This will run the basic GUI to set parameters (what team to use, the format, etc) and play a game (currently hard coded to challenge my account)
--This will crash immediately upon the the predictor reading the team sheet.
--The program may not crash if EVERYTHING lines up perfectly, however it is not robust in any sense and CAN NOT be considered functional. 


From here, use the python script(to be created) to process the summaries and create a way to guess the leads


