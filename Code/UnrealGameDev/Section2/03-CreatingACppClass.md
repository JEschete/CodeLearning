We are starting by creating a C++ class in Unreal Engine to create a basic moving platform. 

We start by going to the tools menu and selecting "New C++ Class." This will open a wizard that guides us through the process of creating a new C++ class in Unreal Engine.

Because we want to place something in the world we will select "Actor" as the parent class. This allows us to create an object that can be placed and manipulated within the level.

By selecting actor we are choosing the parent class. The parent class defines the basic behavior and properties that our new class will inherit. In this case, by choosing "Actor," our moving platform will have all the fundamental characteristics of an actor, such as the ability to be placed in the world, receive updates every frame, and interact with other actors.

We then give the parent actor class a name, "MovingPlatform." This will be the name of our new C++ class that inherits from the Actor parent class.

We name it with a capital letter M and then P for "MovingPlatform," following the common C++ convention of using PascalCase for class names.

After we click create, Unreal Engine will generate the necessary C++ files for our new class. This includes a header file (.h) and a source file (.cpp) where we can define the properties and behavior of our moving platform and compile the code to make it available within the engine.

When we place the MovingPlatform from the content browser into the level, it has no visible components or behavior by default.

You have to drop assets into the details panel to add visible components, such as a static mesh, to the MovingPlatform actor. This allows us to see and interact with the platform in the level.

Now in Visual studio we can see that the MovingPlatform class has been created with its header and source files. The header file contains the class declaration, including any properties and functions, while the source file contains the implementation of those functions.

We can see there are access specifiers, they are:
- `public`: Members declared under this specifier are accessible from outside the class.
- `protected`: Members declared under this specifier are accessible within the class and by derived classes.
- `private`: Members declared under this specifier are accessible only within the class itself.

Within the methods there is the return type, which specifies the type of value the method will return. If a method does not return any value, it uses the `void` return type. For example:

```cpp
void MovePlatform(); // This method does not return any value
FVector GetPlatformLocation(); // This method returns a FVector value
```
Then we also have the following
```cpp
class OBSTACLEASSAULT_API AMovingPlatform : public AActor
```
Lets break down the class declaration:

- `class`: This keyword is used to define a new class in C++.

- `OBSTACLEASSAULT_API`: This macro is used for handling DLL export/import when the class is part of a module.

- `AMovingPlatform`: This defines a new class named `AMovingPlatform`. The `OBSTACLEASSAULT_API` macro is used for handling DLL export/import when the class is part of a module.

- `: public AActor`: This indicates that `AMovingPlatform` inherits from the `AActor` class, meaning it will have all the properties and behaviors of an actor in Unreal Engine.

The class and methods start with A because it is a convention in Unreal Engine to prefix actor classes with an A. This helps to easily identify classes that are actors within the engine.

