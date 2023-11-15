import AmbisonicsGUI

# Run the program:
w = AmbisonicsGUI.AmbisonicsGUI([[3.1415926/4, 3.1415926/4 , 1, 1, 0],
                                 [-3.1415926/4, 3.1415926/4, 1, 1, 1],
                                 [3.1415926/4, -3.1415926/4, 1, 1, 2],
                                 [-3.1415926/4, -3.1415926/4, 1, 1, 3],
                                 [3.1415926*3/4, 3.1415926*3/4 , 1, 1, 4],
                                 [-3.1415926*3/4, 3.1415926*3/4, 1, 1, 5],
                                 [3.1415926*3/4, -3.1415926*3/4, 1, 1, 6],
                                 [-3.1415926*3/4, -3.1415926*3/4, 1, 1, 7],])
w.loop()

# look into callback from tk to stop from going outside of the circle
# docstring/parameter annotations, assert statements
# pep8.org

# connect output to a dedicated input stream
