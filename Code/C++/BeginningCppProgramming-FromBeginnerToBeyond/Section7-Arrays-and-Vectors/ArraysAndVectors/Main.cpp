#include <iostream>
#include <array>
#include <vector>
#include <random>

using namespace std; 

int main() {
  random_device rd;
  mt19937 gen(rd());
  uniform_int_distribution<int> distrib(1, 100);

  cout << "This is a test" << endl;
  array<int, 5> nums{};
  nums[1] = 2;
  nums[0] = 5;

  for (int i = 0; i < nums.size(); i++) {
    nums[i] = distrib(gen);
    cout << nums[i] << endl;
  }

  // To reverse an array in c++
  array<int, 5> temp_nums{};
  int count{0};
  for (int i = nums.size() - 1; i >= 0; i--) {
    temp_nums[count] = nums[i];
    count++;
  }

  cout << "\n";

  nums = temp_nums;
  for (int i = 0; i < nums.size(); i++) {
    cout << nums[i] << endl;
  }

  // Reverse in place by swapping opposite elements.
  cout << "\nIn-place reversal:\n";
  for (size_t left = 0; left < nums.size() / 2; left++) {
    size_t right = nums.size() - 1 - left;
    cout << "Swapping index " << left << " (" << nums[left] << ") with index "
         << right << " (" << nums[right] << ")\n";

    int temp = nums[left];
    nums[left] = nums[right];
    nums[right] = temp;
  }

  cout << "Result:\n";
  for (int num : nums) {
    cout << num << endl;
  }

  // Multi-dimension Array
  int coords[5][3]{
      {0, 1, 2}, {5, 6, 7}, {10, 11, 12}, {15, 16, 16}, {19, 20, 21}};

  for (int i = 0; i < 5; i++) {
    for (int j = 0; j < 3; j++) {
      cout << "Coordinate " << i << ", " << j << ": " << coords[i][j] << "\n";
    }
  }

  cout << "\nRows as (x, y, z) coordinates:\n";
  for (int i = 0; i < 5; i++) {
    cout << "(" << coords[i][0] << ", " << coords[i][1] << ", " << coords[i][2]
         << ")\n";
  }

  // Vectors

  vector<char> vowls(5);  // Constructor initialization syntax
  vector<char> vowels{'a', 'e', 'i', 'o', 'u'};
  vector<int> test_scores{100, 98, 89, 85, 93};
  vector<double> hi_temperatures(
      365, 80.0);  // This method of initilization is stating create 365
                   // elements, and initilize them all to 80.0

  // Demonstrating vector growth.
  vector<int> test_scores2{100, 95, 99};  // size is 3
  
  cout << "Elements in the vector: ";
  for (int i = 0; i < test_scores2.size(); i++) {
    cout << test_scores2[i] << " ";
  }
  cout << endl; 

  test_scores2.push_back(80);             // 100, 95, 99, 80
  test_scores2.push_back(90);             // 100, 95, 99, 80, 90

  cout << "Elements in the vector: ";
  for (int i = 0; i < test_scores2.size(); i++) {
    cout << test_scores2[i] << " ";
  }
  cout << endl;

  return 0;
}