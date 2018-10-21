### What is Logidrone?
Logidrone is a tool for converting [Logisim] circuits to [Nimbatus] drones.
Logidrone might be expanded at some point to also accept other digital circuit editor files such as [Boolr].


### How to use
Logidrone has several commands, currently those commands are:

**circuit_gen**: This command takes a circuit file and produces a drone file that contains the given curcuit.

**mask_gen**: This command takes in a drone file and generates a mask image that you can use to specify where you want the logic gates placed on the drone.

**mask_merge**: This command takes in a base drone file, a mask image, and a circuit file and places the circuit on the drone based on the mask image.
This command is currently ***NOT*** finished. :'( 

### Examples
To use these examples download the repository and have a terminal or command prompt open in the src directory.

#### Circuit generation example
Lets say you have a circuit file circuit.circ that you want in Nimbatus. To create a drone with only the logic from a circuit, you use the following command.
```
python Logidrone.py circuit_gen -f /path/to/circuit.circ -o /path/to/my_new_drone.drn
```
This creates a drone that consists only of the drone core and the logic gates from Logisim stacked above the drone.

Circuit from logisim:
<br/>
![alt text][logisim_circuit]
<br/>
Here we see one of the gates showing that it is wired properly in Nimbatus.
<br/>
<img src="https://github.com/houstonlucas/Logidrone/blob/master/readme_images/circuit_in_Nimbatus.png" alt="The example circuit imported into Nimbatus." width="400"/>

#### Mask generation example
Lets say you already have a drone (base.drn) that you want to extend by placing into it the circuit from circuit.circ.
To do this we must first make a mask of the drones shape and indicate where we want gates to be placed.

```
python Logidrone.py mask_gen -i /path/to/base.drn -m /path/to/mask.png
```
The mask file mask.png is an image where all empty space pixels are white and all occupied space pixels are red. You can now make empty space pixels green and use your updated mask to merge a circuit file and your drone as seen in the next example.

For example the drone shown here:
<br/>
<img src="https://github.com/houstonlucas/Logidrone/blob/master/readme_images/drone_for_mask.png" alt="An example drone for creating a mask." width="400"/>

Would result in the following mask:
<br/>
<img src="https://github.com/houstonlucas/Logidrone/blob/master/readme_images/my_mask.png" alt="The mask produced by the example drone." width="250"/>

#### Mask merge example
Again ***this mode is NOT currently finished***, however here is how it will be used (This feature will be completed soon.).

Once you have a mask file generated from your drone and updated to show where you want to place the logic gates you can now merge them with your circuit file.
Here is an example of how one might edit the mask image to indicate where the logic gates should be placed.
<br/>
<img src="https://github.com/houstonlucas/Logidrone/blob/master/readme_images/my_mask_edited.png" alt="The mask updated to show where gates can be placed." width="250"/>

```
python Logidrone.py mask_merge -i /path/to/base.drn -m /path/to/mask_edited.png -f /path/to/circuit.circ
```

[Logisim]: http://logisim.altervista.org/
[Nimbatus]: https://www.nimbatus.ch/
[Boolr]:http://boolr.me/


[logisim_circuit]: https://github.com/houstonlucas/Logidrone/blob/master/readme_images/Logisim_circuit.png "An example circuit in logisim."

[circuit_in_Nimbatus]: https://github.com/houstonlucas/Logidrone/blob/master/readme_images/circuit_in_Nimbatus.png "The example circuit imported into Nimbatus."

[drone_to_mask]: https://github.com/houstonlucas/Logidrone/blob/master/readme_images/drone_for_mask.png "An example drone for creating a mask."

[drone_mask]: https://github.com/houstonlucas/Logidrone/blob/master/readme_images/my_mask.png "The mask produced by the example drone."

[drone_mask_edited]: https://github.com/houstonlucas/Logidrone/blob/master/readme_images/my_mask_edited.png "The mask updated to show where gates can be placed."




