#!/usr/bin/env python
# -*- coding: latin-1 -*-
## \addtogroup sdh_library_python_demo_scripts_group
#  @{

## \file
#
#  \brief 
#    Very simple demonstration of the sdh python package: Make the SDH move one finger 
#    with "pose" controller type (coordinated position control).
#    See demo-simple.__doc__ and online help ("-h" or "--help") for available options.
#    Forces use of CAN as communication.
#
#  This script contains only the very basicst use of sdh.py features.
#  For more sophisticated applications see the other demo-*.py
#  scripts, or of course the html/pdf documentation.

## 
#  @}


#######################################################################
## \anchor sdhlibrary_python_demo_simple_python_vars
#  \name   Python specific variables
#  
#  Some definitions that describe the script for python
#
#  @{

# pylint: disable-msg=W0622
## The docstring describing the purpose of the script:
__doc__ = '''
Very simple python demo script using the sdh package.
Will move first finger 3 times between current position and current position-10
using the "pose" (coordinated position) control mode.

Forces use of CAN as communication.

- Example usage:
  - Make SDH connected to CAN via ESD net 0:
    > demo-simple-can.py 

    is equivalent to 
    > demo-simple.py --can
'''

__author__    = "Dirk Osswald: dirk.osswald@de.schunk.com"
__url__       = "http://www.schunk.com"
__version__   = "$Id: demo-simple.py 6269 2010-12-03 11:46:13Z Osswald2 $"
__copyright__ = "Copyright (c) 2007 SCHUNK GmbH & Co. KG"

#  end of doxygen name group sdhlibrary_python_demo_simple_python_vars
#  @}
######################################################################

# Import the sdh.py python import module:
import sdh

######################################################################
# Command line option handling:

## Create an option parser object to parse common command line options:
parser = sdh.cSDHOptionParser( usage    =  __doc__ + "\nusage: %prog [options]",
                               revision = __version__ )

# Parse (and handle, if possible) the command line options of the script:
(options, args) = parser.parse_args()

# The parsed command line options are now stored in the options
# object. E.g. options.port is the communication port to use, either
# the default one or the one read from the -p | --port command line
# option

## An object to print script-level debug messages, if requested.
dbg = sdh.dbg.tDBG( flag=options.debug_level>0, fd=options.debug_output )
dbg << "Debug messages of script are printed like this.\n" # pylint: disable-msg=W0104

# reduce debug level for subsystems
options.debug_level-=1

#
######################################################################

#!!!!!
# force use of CAN by overwriting the user given or default options
options.usecan   = True
options.net      = 0
options.baudrate = 1000000
#!!!!!

# Create an instance "hand" of the class cSDH:
hand = sdh.cSDH( options=options.__dict__ )
dbg << "Successfully created cSDH instance\n"  # pylint: disable-msg=W0104

# Open communication to the SDH device using the interface given on the 
# command line or via default RS232 port 0 = COM1.
hand.Open()
dbg << "Successfully opened communication to SDH\n" # pylint: disable-msg=W0104

# Pack the rest of this demo into a try block so that we can recover in case of an error:
try:
    ## do some prepartions:
    # Switch to "pose" controller mode and set default velocities first:
    hand.SetController( hand.eControllerType["eCT_POSE"] )
    hand.SetAxisTargetVelocity( sdh.All, [ 40.0 ] * 7 )


    # Perform some action:
    #   get the current actual axis angles of finger 0
    faa = hand.GetFingerActualAngle( 0 )
    
    #   sometimes the actual angles are reported slightly out of range
    #   (Like -0.001 for axis 0 ). So limit the angles to the allowed range:
    faa = sdh.ToRange_a( faa, hand.GetFingerMinAngle( 0 ), hand.GetFingerMaxAngle( 0 ) );
    
    #   modify these by decrementing the proximal and the distal axis angles
    #   (make a copy fta of faa and modify that to keep actual pose available)
    fta = list(faa) 
    fta[1] -= 10
    fta[2] -= 10
    
    
    #   keep fta in range too:
    fta = sdh.ToRange_a( fta, hand.GetFingerMinAngle( 0 ), hand.GetFingerMaxAngle( 0 ) );
    
    print "Moving first finger between\n  pos %s\n  and %s" % (str(faa), str(fta))
    
    #   now move for 3 times between these two poses:
    for i in range(0,3):
        for target in (fta,faa):
    
            # set a new target angles
            hand.SetFingerTargetAngle( 0, target )
            
            # and make the finger move there:
            hand.MoveFinger( 0 )

finally:     
    # Finally close connection to SDH again, this switches the axis controllers off
    hand.Close()
    dbg << "Successfully disabled controllers of SDH and closed connection\n" # pylint: disable-msg=W0104
