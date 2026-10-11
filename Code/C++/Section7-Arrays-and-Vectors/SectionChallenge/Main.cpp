/* Section 7
   Challenge

   Write a C++ program as follows:

   Declare 2 empty vectors of integers named
   vector1 and vector2, respectively.

   Add 10 and 20 to vector1 dynamically using push_back
   Display the elements in vector1 using the at() method as well as its size using the size() method

   Add 100 and 200 to vector2 dynamically using push_back
   Display the elements in vector2 using the at() method as well as its size using the size() method

   Declare an empty 2D vector called vector_2d
   Remember, that a 2D vector is a vector of vector<int>

   Add vector1 to vector_2d dynamically using push_back
   Add vector2 to vector_2d dynamically using push_back

   Display the elements in vector_2d using the at() method

   Change vector1.at(0) to 1000

   Display the elements in vector_2d again using the at() method

   Display the elements in vector1

   What did you expect? Did you get what you expected? What do you think happened?
*/

#include <iostream>
#include <vector>
using namespace std;

int main() {
  vector<int> vector1;
  vector<int> vector2;

  vector1.push_back(10);
  vector1.push_back(20);
  cout << "Vector 1 contains: " << vector1.at(0) << " " << vector1.at(1) 
       << " and is size: " << vector1.size() << endl; 

  vector2.push_back(100);
  vector2.push_back(200);
  cout << "Vector 2 contains: " << vector2.at(0) << " " << vector2.at(1)
       << " and is size: " << vector2.size() << endl; 

  vector<vector<int>> vector_2d;
  vector_2d.push_back(vector1);
  vector_2d.push_back(vector2);

  cout << "Vector 2D contains: ";
  for (size_t i = 0; i < vector_2d.size(); i++) {
    for (size_t j = 0; j < vector_2d.at(i).size(); j++) {
      cout << vector_2d.at(i).at(j) << " ";
    }
  }
  cout << " and is size: " << vector_2d.size() << endl; 

  vector1.at(0) = 1000; 
  cout << "Vector 2D now contains: ";
  for (size_t i = 0; i < vector_2d.size(); i++) {
    for (size_t j = 0; j < vector_2d.at(i).size(); j++) {
      cout << vector_2d.at(i).at(j) << " ";
    }
  }
  cout << " and is size: " << vector_2d.size() << endl;

  cout << "Vector 1 contains: " << vector1.at(0) << " " << vector1.at(1)
       << " and is size: " << vector1.size() << endl; 

  // I expect before running that vector1 will have changed, and that vector_2d will show the original values. This is because when the vector_2d had the two sub vectors inserted, it received copies of them, and not the originals. So changing the original did not update the version in vector_2d. 

  /* Results of run: 
  Vector 1 contains: 10 20 and is size: 2
  Vector 2 contains: 100 200 and is size: 2
  Vector 2D contains: 10 20 100 200  and is size: 2
  Vector 2D now contains: 10 20 100 200  and is size: 2
  Vector 1 contains: 1000 20 and is size: 2
  */

	return 0;
}