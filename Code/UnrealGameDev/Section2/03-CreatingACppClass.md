We are starting by creating a C++ class in Unreal Engine to create a basic moving platform. 

We start by going to the tools menu and selecting "New C++ Class." This will open a wizard that guides us through the process of creating a new C++ class in Unreal Engine.

Because we want to place something in the world we will select "Actor" as the parent class. This allows us to create an object that can be placed and manipulated within the level.

By selecting actor we are choosing the parent class. The parent class defines the basic behavior and properties that our new class will inherit. In this case, by choosing "Actor," our moving platform will have all the fundamental characteristics of an actor, such as the ability to be placed in the world, receive updates every frame, and interact with other actors.

We then give the parent actor class a name, "MovingPlatform." This will be the name of our new C++ class that inherits from the Actor parent class.

We name it with a capital letter M and then P for "MovingPlatform," following the common C++ convention of using PascalCase for class names.

After we click create, Unreal Engine will generate the necessary C++ files for our new class. This includes a header file (.h) and a source file (.cpp) where we can define the properties and behavior of our moving platform and compile the code to make it available within the engine.

