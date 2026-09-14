#include <iostream>
#include "main.h"

using std::cin;
using std::cout; 
using std::endl;

int main() {
	

	cout << "This code is meant to show the concepts of what we learned. " << '\n';
	cout << "So things may not be prefect because I'm just trying things." << endl; 

	cout << "Enter a value for a: ";
    cin >> a;
	
	cout << "Enter a value for b: ";
	cin >> b;

	cout << "Based on the inputs, here are the results of the following operators: " << endl; 
	cout << "The '+' operator: " << a + b << endl;
    cout << "The '-' operator: " << a - b << endl;
    cout << "The '*' operator: " << a * b << endl;
    cout << "The '/' operator (Please do not enter a 0 for now): " << static_cast<double>(a) / b << endl;
    cout << "The '%' operator: " << a % b << endl;


}