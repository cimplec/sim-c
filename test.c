#include <stdio.h>

int main() {
	int a = 1;
	int b = 2;
	if(a == 1 || b == 2) {
	printf("One");
	}
	else if(a == 2 && b == 1) {
	printf("Two");
	}
	else {
	printf("Otherwise");
	}

	return 0;
}