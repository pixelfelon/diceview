/*
 * Polyhedral Dice Statistical Analysis (Diceview)
 * 
 * @Company
 *   Diceview Team
 * 
 * @File Name
 *   servo.ino
 * 
 * @Summary
 *   Serial servo controller.
 */
 
#include <Servo.h>

#define SPIN 3


Servo servo;

int smin = 575;
int smax = 2218;
int sang = 90;


void setup ()
{
	servo.attach(SPIN, smin, smax);
	servo.write(sang);
	Serial.begin(115200);
}

void loop ()
{
	char sbyte = '\0';
	while (!isalpha(sbyte))
	{
		if (!Serial.available())
		{
			delay(10);
		}
		sbyte = Serial.read();
	}

	switch (sbyte)
	{
		case 's':
			sang = Serial.parseInt();
			servo.write(sang);
			Serial.write('\n');
			break;
		
		case 'l':
			smin = Serial.parseInt();
			servo.detach();
			servo.attach(SPIN, smin, smax);
			servo.write(sang);
			Serial.write('\n');
			break;
		
		case 'u':
			smax = Serial.parseInt();
			servo.detach();
			servo.attach(SPIN, smin, smax);
			servo.write(sang);
			Serial.write('\n');
			break;
	}
}
