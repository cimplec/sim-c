#include <stdio.h>

int sum(int a, int b) {

	return a + b;
}

int main() {
	int hello = sum(1, 2) + 2;
	printf("%d", sum(1, 2));

	return 0;
}