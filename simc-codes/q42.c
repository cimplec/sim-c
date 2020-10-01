#include <math.h>
#include <stdio.h>

int main() {
	int num;
	printf("Enter a number:\t");
	scanf("%d", &num);
	int sqr = num * num;
	int temp = num;
	int n = 0;
	while(temp > 0) {
	n = n + 1;
	temp = temp / 10;
	}
	int power = pow(10, n);
	int split = sqr % power;
	if(split == num) {
	printf("Automorphic number\n");
	}
	else {
	printf("Not a Automorphic number\n");
	}

	return 0;
}