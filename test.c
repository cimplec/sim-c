#include <stdio.h>

int sum(int a, int b) {

	return a + b;
}

int main() {
	int hello = sum(1, 2);
	printf("The sum = %d", hello);
	exit(0);
	return 0;
}