#include "calculator.h"
#include "../utils/logger.h"
Calculator::Calculator() {
}

Calculator::~Calculator() {
}

int Calculator::add(int a, int b) {
    logger.log("Doing addition: " + std::to_string(a) + " + " + std::to_string(b));
    return a + b;
}

int Calculator::subtract(int a, int b) {
    logger.log("Doing subtraction: " + std::to_string(a) + " - " + std::to_string(b));
    return a - b;
}

int Calculator::multiply(int a, int b) {
    logger.log("Doing multiplication: " + std::to_string(a) + " * " + std::to_string(b));
    return a * b;
}

int Calculator::divide(int a, int b) {
    logger.log("Doing division: " + std::to_string(a) + " / " + std::to_string(b));
    if (b == 0) {
        return 0; // 简单处理，实际应该抛出异常
    }
    return a / b;
}