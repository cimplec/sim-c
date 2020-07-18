#include <stdio.h>

int sum(int a, int b) {

	return a + b;
}

int main() {
	int sum_two = 3 + sum(1, 2);
	printf("The value of 1+2+3 is = %d", sum_two);

	return 0;
}