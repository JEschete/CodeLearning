#include <iostream>

/* For this challenge we will be using US dollars and cents 
Write a program that asks the user to enter the following: 
An integer representing the number of cents

You may assume that the number of cents entered is greater than or equal to zero. 

The program should then display how to provide change to the user.

In the US 
	1 dollar is 100 cents
	1 quarter is 25 cents
	1 dime is 10 cents
	1 nickle is 5 cents
	1 penny is one cent

	Here is a saple run: 
	Enter an amount in cents: 92

	You can provide this change as follows: 
	dollars: 0
	quarters: 3
	dimes: 1
	nickles: 1
	pennies: 2

	Feel free to use your own currency system. 
	Also think of how you migh solve the problem using the modulo operator.

*/

using namespace std;

int main() {

	int user_money {};
	int dollars {};
	int quarters {};
    int dimes {};
    int nickels{};
    int pennies {};

	cout << "Enter an amount in cents: ";
    cin >> user_money;

	if ((user_money % 100) == 0) {
      dollars = user_money / 100;
      user_money -= dollars * 100;
	}
	else if (((user_money % 100) != 0) && ((user_money / 100) >=1)) {
          dollars = user_money / 100;
		  user_money -= dollars * 100; 
	}
    if ((user_money % 25) == 0) {
        quarters = user_money / 25;
        user_money -= quarters * 25;
    } else if (((user_money % 25) != 0) && ((user_money / 25) >= 1)) {
        quarters = user_money / 25;
        user_money -= quarters * 25;
    }
    if ((user_money % 10) == 0) {
        dimes = user_money / 10;
      user_money -= dimes * 10;
    } else if (((user_money % 10) != 0) && ((user_money / 10) >= 1)) {
      dimes = user_money / 10;
      user_money -= dimes * 10;
    }
    if ((user_money % 5) == 0) {
        nickels = user_money / 5;
      user_money -= nickels * 5;
    } else if (((user_money % 5) != 0) && ((user_money / 5) >= 1)) {
      nickels = user_money / 5;
      user_money -= nickels * 5;
    }
    if ((user_money % 1) == 0) {
        pennies = user_money / 1;
      user_money -= pennies * 1;
    } else if (((user_money % 1) != 0) && ((user_money / 1) >= 1)) {
      pennies = user_money / 1;
      user_money -= pennies * 1;
    }

	cout << "You can provide this change as follows:" << "\n";
	cout << "Money remaining: " << user_money << endl;
    cout << "Dollars: " << dollars << endl;
    cout << "Quarters: " << quarters << endl;
    cout << "Dimes: " << dimes << endl;
    cout << "Nickels: " << nickels << endl;
    cout << "Pennies: " << pennies << endl;

    /* 
    Optimized version: 
    
    int cents {};
    int dollars {};
    int quarters {};
    int dimes {};
    int nickels {};
    int pennies {};

    cout << "Enter an amount in cents: ";
    cin >> cents;

    int remaining { cents };

    dollars = remaining / 100;
    remaining %= 100;

    quarters = remaining / 25;
    remaining %= 25;

    dimes = remaining / 10;
    remaining %= 10;

    nickels = remaining / 5;
    remaining %= 5;

    pennies = remaining;

    cout << "You can provide this change as follows:\n";
    cout << "Dollars: " << dollars << endl;
    cout << "Quarters: " << quarters << endl;
    cout << "Dimes: " << dimes << endl;
    cout << "Nickels: " << nickels << endl;
    cout << "Pennies: " << pennies << endl;

    return 0;
    */


	return 0; }