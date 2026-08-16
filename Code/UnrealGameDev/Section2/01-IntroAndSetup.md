Intro
--------------------------------
Our action plan for this section is as follows:
1. Create a new project and setup a test level. 
2. Learn C++ Basics.
3. Make moving platforms.
4. Make Rotating Platforms. 
5. Import assets and design a level. 

Project Setup
--------------------------------
For this project we will select the third-person template and set it as a C++ project.
In the bottom left of the unreal editor there is the Content Drawer, which is used to manage and organize all the assets in your project.

On the left of the content browser there is the folder hierarchy, which allows you to navigate through the different folders and locate specific assets within your project.

To the right of the content browser is the asset view, which displays the contents of the currently selected folder, allowing you to see and interact with the assets within that folder.

In the content folder we are going to create a new folder called "MyStuff"

Adding a new level
--------------------------------
To add a new level, go to the "File" menu in the Unreal Editor, select "New Level", and choose the desired level template. 

The options are:
- OpenWorld: A level designed for large, open environments with pre-configured lighting and sky.
- Empty OpenWorld: A completely empty level designed for large, open environments with no pre-placed actors.
- Basic Level: A simple level with minimal setup, suitable for small-scale projects or testing.
- Empty Level: A completely empty level with no pre-placed actors.

The actors that the basic comes with are:
In a lighting folder: 
- Directional Light: Provides a global light source, simulating sunlight.
- Exponential Height Fog: Adds atmospheric fog that changes in density based on height, enhancing the sense of depth and scale in the level.
- SkyAtmosphere: Simulates the Earth's atmosphere, providing realistic sky and lighting effects.
- SkyLight: Captures the distant parts of the level and applies ambient lighting, enhancing the overall illumination and shadows.
- SM_SkySphere: A static mesh representing the sky, often used in conjunction with the SkyAtmosphere and SkyLight to create a realistic sky environment.
- VolumetricCloud: Adds realistic volumetric clouds to the sky, enhancing the visual depth and atmosphere of the level.

Outside of the Lighting folder, the basic level also includes:
- Player Start: Defines the initial spawn location for the player character.
- Floor: A simple static mesh representing the ground plane of the level.

When we press play, we can see the player character spawn at the Player Start location and interact with the floor and other elements in the level.

Note: At this point the only method of controlleing the player character is through the default input bindings provided by the third-person template, typically using the keyboard and mouse. The controller has not been implemented, customized, or extended in any way.

So since we created a new level we need to save it, which we can do by going to the "File" menu in the Unreal Editor and selecting "Save Current Level" or by using the keyboard shortcut Ctrl+S.

Note: When we reopen the project, the level selected will not be automatically set to the one we last saved. We can change the default level by going to the "Edit" menu, selecting "Project Settings", navigating to the "Maps & Modes" section, and setting the desired level as the "Editor Startup Map" and "Game Default Map".

The editor startup map is the level that will be automatically loaded when the Unreal Editor starts. Setting the desired level as the editor startup map ensures that we begin working on the correct level each time we open the project.

The game default map is the level that will be used when the game is played, either in the editor or in a packaged build. Setting the desired level as the game default map ensures that the correct level is loaded during gameplay.

