#include <stdio.h>
#include "geometry.h"

struct Student 	{
	int roll_no;
	char* name;
} ;

int main() {
	int roll_no = 1;
	char* name = "Siddhartha";
	struct Student s;
	s.roll_no = roll_no;
	s.name = name;
	printf("%s", name);
	printf("%s", s.name);
	int result = square_area(3);

	return 0;
}
