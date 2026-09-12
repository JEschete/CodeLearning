// Will ask the user to enter their favorite number and then say "That's my
// favorite number too!"

#include <iostream>

int main() {
/*  int favorite_number;  // Declaring like this makes favorite_number hold
                        // garbage until we assign it a value.

  std::cout << "Enter your favorite number between 1 and 100: ";

  std::cin >> favorite_number;

  std::cout << "Amazing! That's my favorite number too!" << std::endl;

  return 0;*/

  /*
  All c++ programs must have a main function.The main function is the
entry point of the program. The main function is where the program
starts executing. The main function is where the program ends
  */

  /*It returns zero because zero typically indicates that the program executed
   * successfully*/

/*
Section Challenge
------------------
Create a C++ program that asks the user for their favorite number between 1 and 100, then read this number from the console. 

Suppose the user enters 24.
Then display the following to the console: 

Amazing!! That's my favorite number too!
No really!! 24 is my favorite number!
*/

    // Here instead of declaring it without initializing
    // it, we are initializing it to 0. This is a good
    // practice to avoid garbage values.
    int favorite_number = 0;  

    std::cout << "Enter your favorite number between 1 and 100: ";
    std::cin >> favorite_number;

    std::cout << "Amazing!! That's my favorite number too!" << std::endl;
    std::cout << "No really!! " << favorite_number << " is my favorite number!" << std::endl;

    std::cout << "See you later! " << std::endl;

    return 0;
}
