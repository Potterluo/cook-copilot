#include <iostream>
#include "utils.hh"
#include "math/math.cc"

int main() {
    std::cout << "Hello from .cc project!" << std::endl;
    
    // Test utility function
    printMessage("Testing .cc file support");
    
    // Test math function
    int result = add(5, 3);
    std::cout << "5 + 3 = " << result << std::endl;
    
    return 0;
}