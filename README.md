----
#### ABOUT
The Git repository for the UMUAS (2023/2024)
Currently run by: Daniel Markuza

----
#### Design Plan: 

###### Object Detection:
- Detect landing pad -> orange hexagon
- OpenCV
- **Objectives**:
	- Order the landing pad
	- Work session building model
	- Producing datasets to train the model
	- Configure Jetson Nano
		- Override Network Files (to be able to connect to the local host)
	- Set up training model on Jetson Nano
		- Connect FPV cameras
- Once done, create proper path to actually land at a landing pad (4 levels of difficulty)
###### Flight Termination: 
- Detect loss of connection with GCS
- Land "safely"
	- Least damage possible
	- Not hurting anyone
- Integrate Python into C
- Set up switch between autopilot and normal pilot
	- Pixhawk 4
	- QGroundControl
###### MISC:
- Complete lap algorithm for task 1
- **PID Tuning:**
	- Adjust 3 variables for drone to fly and work properly
	- Variables in auto pilot code


----
#### Goals (per iteration):

###### Iteration 1 (Deadline: February 26th): 
- **Object Detection:**
	- Build the initial model
	- Produce datasets
	- Train model 
- **Flight Termination**
	- Figure out how to detect loss of connection
	- Set up switch between the pilot and the autopilot
		- Talk with GCS about the button to switch between modes
	- Get started on figuring out how to get to drone to land safely
###### Iteration 2 (Deadline: March 20th):
- **Iteration 1 revisions:**
	- Communicate what we want changed
	- Revise deadlines
- **Object Detection:**
	- Path algorithm for task 2
	- set up hardware to work with software
		- FPV cameras from drone working with software
		- Set it up on CPU on board the drone
- **Flight Termination**:
	- Land safely
		- find a safe location to "crash"
		- Just land (Systems intact just lost connection)
			- Fail safe
- **MISC**:
	- Algorithm for task 1:
		- Determine how many laps are possible (battery power, and etc.)
###### Iteration 3 (Deadline: N/A):
- **PID Tunning**
- Final testing
	- Make sure object detection model works with drone
	- Make sure algorithms work with drones
	- Make flight termination system
