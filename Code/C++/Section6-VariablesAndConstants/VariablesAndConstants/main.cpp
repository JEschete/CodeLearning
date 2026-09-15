#include <iostream>

using namespace std;

int main() {
	int age{};
    double hourly_wage{23.50};
    string name{};

	cout << "Please enter your name and age, separated by a space: " << endl; 
	cin >> name >> age; 

	cout << "Your name is " << name <<
            " you make "
                << hourly_wage << " per hour at " << age
                << " years old. \nIn a standard pay period you make $"
                << hourly_wage * 80 << endl;
}

