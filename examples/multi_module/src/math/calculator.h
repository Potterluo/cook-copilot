#ifndef CALCULATOR_H
#define CALCULATOR_H

#include "../utils/logger.h"

class Calculator {
private:
    Logger logger;

public:
    Calculator();
    ~Calculator();

    int add(int a, int b);
    int subtract(int a, int b);
    int multiply(int a, int b);
    int divide(int a, int b);
};

#endif // CALCULATOR_H