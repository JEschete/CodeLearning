First install Kali Linux and Ghidra.
Kali Linux for Virtualbox can be downloaded from the official Kali Linux website at https://www.kali.org/get-kali/#kali-virtual-machines

I had to increase the shipped memory allocation for the virtual machine to ensure smooth performance. As well as enable 3d acceleration, increase the number of processor cores allocated to the virtual machine, and the scaling factor for the display.

We then make a shared folder. 

I had to disable memory integrity in windows 11 to allow VirtualBox to run the virtual machine without conflicts.

Windows Virtual Machine Platform had to be disabled as well to prevent conflicts with VirtualBox.

In an admin terminal I had to type:
```
bcdedit /set hypervisorlaunchtype off
```
After running this command, I had to restart my computer for the changes to take effect.

I had to change the Graphics Controller from VMSVGA to VBoxSVGA.
There was a warning about this not being optimal, but it was necessary for proper display functionality in the virtual machine.

I also had to set the render scale to 200%

Onces the virtual box shenannigans are taken care of, I could finally start the Kali Linux virtual machine without any display or performance issues.

Now to install openJDK and Ghidra.

To install openJDK, I ran the following command in the terminal:
```
sudo apt update
sudo apt install openjdk-21-jdk
```

To verify the installation, I checked the Java version:
```
java -version
```

Next, I downloaded Ghidra from the official github repository. The repository can be found at https://github.com/NationalSecurityAgency/ghidra. After downloading, I extracted it to a suitable location.

I had to copy the extracted Ghidra folder to a suitable location, such as `/opt/ghidra`, to make it easier to run and manage.

with the following commands: 
First navigate to the downloads folder where I exptracted Ghidra: 
cd ~/Downloads
then run the following command to copy the extracted Ghidra folder to `/opt`:
sudo cp -r ghidra_12.1.2 /opt
I had previously renamed the folder. 

opt is a standard directory in Linux systems where optional or third-party software is installed. By copying Ghidra to `/opt/ghidra`, it becomes easier to manage and run the application.

To run ghidra we navigate to the installation directory and execute the `ghidraRun` script:
```
cd /opt/ghidra
./ghidraRun
```
we can make a desktop shortcut or create an alias for easier access in the future.
by running the command.
```
alias ghidra='/opt/ghidra/ghidraRun'
```
and then you can simply run `ghidra` from the terminal to start Ghidra.

Once Ghidra is running, you want to go to File and create a new project. For session1 we will set the directory to where the session1 files are in the home directory, and name the project "session1".

We drag the c1 from the session1 folder and will be detected as an elf file. An elf file is a common standard file format for executable files, object code, shared libraries, and core dumps in Unix-like operating systems.

After importing we get a summary screen. 
Dismiss the summaary screen then drag the c1 program to the CodeBrowser window to start analyzing it.

It will say that the file has not been analyzed yet. You can proceed with the analysis by clicking "Yes" or "Analyze" to let Ghidra perform its initial analysis on the file.

Once the analysis is complete, you can start exploring the disassembled code, functions, and other elements within the CodeBrowser window to understand the program's behavior.

For navigation, the top left has the Program Trees.

Program Trees: This section displays the hierarchical structure of the program being analyzed, including functions, classes, and other code elements. It allows you to quickly navigate to different parts of the code.

Symbol Tree: This section displays all the symbols in the program, such as functions, variables, and labels. It helps you quickly locate and navigate to specific symbols within the code.

Data Type Manager: This section displays all the data types used in the program, such as structures, enums, and typedefs. It allows you to manage and navigate the data types efficiently.

In the Listing window we have the disassembly for the binary. 
The first column is the address column, which shows the memory addresses of the instructions in the binary. Then the size column indicates the size of each instruction in bytes. The next column typically displays the raw bytes of the instruction, followed by the disassembled instruction itself. This layout allows you to analyze the binary at both the machine code and assembly levels.

On the right is the Decompile window, which shows a high-level representation of the disassembled code. This window allows you to understand the program's logic more easily compared to reading raw assembly instructions, as it presents the code in a C-like format.

We want to find the main function in the program, as it is typically the entry point of the application. In the Symbol Tree, you can look for a function named "main" and double-click it to navigate to its location in the Listing window. This will allow you to analyze the program's execution starting from the main function.

The functions fall between sections listed as

************************************************************** *                          FUNCTION                          * **************************************************************

To denote where a function starts and ends in the disassembly, Ghidra uses these FUNCTION headers. They help you visually separate different functions and understand the structure of the program more easily.