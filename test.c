#include <stdio.h>

int main() {
	int a = 1;
	int b = 2;
	switch(a + b) {
	case 1:
	printf("Hello");
	break;
	case 2:
	printf("World");
	break;
	default:
	printf("Default");
	break;
	}

	return 0;
}
