#include <stdio.h>

int main() {
	float x = 3.14;
	{
	char* x = "hello";
	{
	int x = 1;
	{
	printf("%d", x);
	printf("%c", '\n');
	}
	printf("%d", x);
	printf("%c", '\n');
	}
	printf("%s", x);
	printf("%c", '\n');
	}
	printf("%f", x);
	printf("%c", '\n');

	return 0;
}
