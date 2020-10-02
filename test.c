#include <stdio.h>

int main() {
	int x1;
	printf("Enter x coordinate of center of circle 1 ");
	scanf("%d", &x1);
	int y1;
	printf("Enter y coordinate of center of circle 1 ");
	scanf("%d", &y1);
	int r1;
	printf("Enter radius of circle 1 ");
	scanf("%d", &r1);
	int x2;
	printf("Enter x coordinate of center of circle 2 ");
	scanf("%d", &x2);
	int y2;
	printf("Enter y coordinate of center of circle 2 ");
	scanf("%d", &y2);
	int r2;
	printf("Enter radius of circle 2 ");
	scanf("%d", &r2);
	int diffx = (x1 - x2);
	int diffy = (y1 - y2);
	diffx = diffx * diffx;
	diffy = diffy * diffy;
	int diff = diffx + diffy;
	int rad1 = r1 * r1;
	int rad2 = r2 * r2;
	int sum = rad1 + rad2;
	if(sum == diff) {
	printf("The circles are orthogonal");
	}
	else {
	printf("The circles are not orthogonal");
	}

	return 0;
}