#include <stdio.h>
#include "utils.h"

int main() {
    printf("Hello from simple project!\n");
    print_message("This is a test message");
    
    int sum = add_numbers(5, 7);
    printf("5 + 7 = %d\n", sum);
    
    return 0;
}