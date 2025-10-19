#include "calculator.h"

Calculator::Calculator() {
}

Calculator::~Calculator() {
}

int Calculator::add(int a, int b) {
    return a + b;
}

int Calculator::subtract(int a, int b) {
    return a - b;
}

int Calculator::multiply(int a, int b) {
    return a * b;
}

int Calculator::divide(int a, int b) {
    if (b == 0) {
        return 0; // 简单处理，实际应该抛出异常
    }
    return a / b;
}