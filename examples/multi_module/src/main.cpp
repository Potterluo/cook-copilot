#include <iostream>
#include "math/calculator.h"
#include "utils/logger.h"

int main() {
    Logger logger;
    logger.log("Starting multi-module application");
    
    Calculator calc;
    int result = calc.add(10, 5);
    logger.log("10 + 5 = " + std::to_string(result));
    
    result = calc.multiply(10, 5);
    logger.log("10 * 5 = " + std::to_string(result));
    
    logger.log("Application finished");
    return 0;
}