### What is Logidrone?
Logidrone is a tool for converting [Logisim] circuits to [Nimbatus] drones.
Logidrone might be expanded at some point to also accept other digital circuit editor files such as [Boolr].


### How to use
Logidrone has several modes, currently those modes are:

**circuit_gen**: This mode takes a circuit file and produces a drone file that contains the given curcuit.

**mask_gen**: This mode takes in a drone file and generates a mask image that you can use to specify where you want the logic gates placed on the drone.

**mask_merge**: This mode takes in a base drone file, a mask image, and a circuit file and places the circuit on the drone based on the mask image.
This mode is currently ***NOT*** finished. :'( 

### Examples
To use these examples download the repository and have a terminal or command prompt open in the src directory.

#### Circuit generation example
Lets say you have a circuit file circuit.circ that you want in Nimbatus. To create a drone with only the logic you use the following command.
```
python Logidrone.py circuit_gen -f /path/to/circuit.circ -o /path/to/my_new_drone.drn
```
This creates a drone that consists only of the drone core and the logic gates from Logisim stacked above the drone.


#### Mask generation example
Lets say you already have a drone (base.drn) that you want to extend by placing into it the circuit from circuit.circ.
To do this we must first make a mask of the drones shape and indicate where we want gates to be placed.

```
python Logidrone.py mask_gen -i /path/to/base.drn -m /path/to/mask.png
```
The mask file mask.png is an image where all empty space pixels are white and all occupied space pixels are red. You can now make empty space pixels green and use your updated mask to merge a circuit file and your drone as seen in the next example.


#### Mask merge example
Again ***this mode is NOT currently finished***, however here is how it will be used (This feature will be completed soon.).

Once you have a mask file generated from your drone and updated to show where you want to place the logic gates you can now merge them with your circuit file.

```
python Logidrone.py mask_merge -i /path/to/base.drn -m /path/to/mask_edited.png -f /path/to/circuit.circ
```

[Logisim]: http://logisim.altervista.org/
[Nimbatus]: https://www.nimbatus.ch/
[Boolr]:http://boolr.me/