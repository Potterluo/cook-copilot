#include <iostream>
#include "utils.h"
#include "calculator.hpp"

int main() {
    std::cout << "Mixed extensions project test!" << std::endl;
    
    // Test C-style function
    printWelcome();
    
    // Test C++ class
    Calculator calc;
    std::cout << "10 + 5 = " << calc.add(10, 5) << std::endl;
    std::cout << "10 - 5 = " << calc.subtract(10, 5) << std::endl;
    
    return 0;
}