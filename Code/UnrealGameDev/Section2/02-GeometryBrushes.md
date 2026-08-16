Geometry Brushes
-----------------------------
Geometry brushes are used to create basic shapes and structures within the level. They are primarily used for blocking out level geometry before adding detailed meshes and assets.

The first brush we will use is the box brush, which allows us to create rectangular prisms within the level. It is useful for creating walls, floors, and other basic structures.

We do not transform it using the standard transformation tools like we do with static meshes. Instead, we adjust its dimensions and position through the brush settings in the details panel.

The default brush type is additive, which means it adds geometry to the level. There is also a subtractive brush type, which removes geometry from the level, allowing us to create hollow spaces or cutouts within existing brushes.

Next is the cylinder brush, which by default only has 8 sides, so it's more like an octagonal prism rather than a perfectly smooth cylinder. We can increase the number of sides in the brush settings to make it appear more circular.

When we play if we get a yellow warning about virtual shadow maps we can go to edit->project settings and search for shadow maps, and then change it to just shadow maps. 

The difference between virtual shadow maps and regular shadow maps is that virtual shadow maps provide higher quality shadows with more accurate details, especially for large and complex scenes. However, they can be more performance-intensive, which is why switching to regular shadow maps can help improve performance if the virtual shadow maps are not necessary for the level.

We can then add some steps with the steps brush, which allows us to create stair-like structures within the level. This is useful for creating platforms, staircases, or any other stepped geometry.

We can adjust the number of steps, their height, and depth through the brush settings in the details panel, allowing us to customize the staircase to fit our level design needs.
Additionally, we can combine multiple brushes to create more complex shapes and structures. By using a combination of additive and subtractive brushes, we can block out intricate level geometry before replacing it with detailed static meshes and assets.
