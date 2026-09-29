// Section 6
// Challenge

/*
    Frank's Carpet Cleaning Service
    Charges:
        $25 per small room
        $35 per large room
    Sales tax rate is 6%
    Estimates are valid for 30 days

    Prompt the user for the number of small and large rooms they would like
cleaned and provide an estimate such as:

Estimate for carpet cleaning service
Number of small rooms: 3
Number of large rooms: 1
Price per small room: $25
Price per large room: $35
Cost : $110
Tax: $6.6
===============================
Total estimate: $116.6
This estimate is valid for 30 days
*/

#include <iostream>

using namespace std;

int main() {

const int validDay{30};
const float costPerSmall{25.0f};
const float costPerLarge{35.0f};
const float taxRate{0.06f};
int largeRoomsBought{0};
int smallRoomsBought{0};
float cost{0.0f};
float taxSum{0.0f};
float subTotal{0.0f};

cout << "Frank's Carpet Cleaning Service" << endl;
cout << "Charges:" << endl;
cout << "\t$" << costPerSmall << " per small room" << endl;
cout << "\t$" << costPerLarge << " per large room" << endl;
cout << "Sales tax rate is " << taxRate * 100 << "%" << endl;
cout << "Estimates are valid for " << validDay << " days." << endl;
cout << "\n" << endl;

cout << "Please enter the number of small rooms requested: ";
cin >> smallRoomsBought;

cout << " \nPlease enter the number of large rooms requested: ";
cin >> largeRoomsBought;

cout << "Estimate for carpet cleaning service" << endl;
cout << "\nNumber of small rooms: " << smallRoomsBought << endl;
cout << "Number of large rooms: " << largeRoomsBought << endl;
cout << "Price per small room: $" << costPerSmall << endl;
cout << "Price per large room: $" << costPerLarge << endl;
subTotal = (costPerSmall * smallRoomsBought) + (costPerLarge * largeRoomsBought);
cout << "Cost: $" << subTotal << endl;

taxSum = subTotal * taxRate;
cost = taxSum + subTotal;

cout << "Tax: $" << taxSum << endl;
cout << "===============================" << endl;
cout << "Total Estimate: $" << cost << endl;
cout << "This estimate is good for: " <<validDay<< " days." << endl;

}

