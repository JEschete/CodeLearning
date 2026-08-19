Live Coding
--------------------------

Live coding in unreal engine is a feature that allows developers to make changes to the game's code and see the results immediately without restarting the editor.

This can significantly speed up the development process, as it reduces the time spent waiting for the editor to compile and reload the game after each change.

To enable live coding in Unreal Engine, go to the "Edit" menu, select "Editor Preferences," then navigate to the "General" section and choose "Live Coding." From there, you can enable the feature and configure its settings according to your preferences.

Once live coding is enabled, you can start a live coding session by clicking the "Compile" button in the toolbar while the editor is running. Any changes made to the code will be compiled and applied immediately, allowing you to see the effects without restarting the editor.

There are some rules of thumb, because there may be some issues. 

First, if you're changing header files it's better to compile them in visual studio, otherwise there may be issues with live coding not picking up the changes correctly. 

Second, compile from visual studio at the start and end of the work session. This ensures that all changes are properly recognized and reduces the likelihood of encountering issues with live coding.

