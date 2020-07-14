char key = '0';
#define __R 19

int count = 0;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  Serial.println("\nUart read");
  pinMode(__R, OUTPUT);
}

void loop() {
  // put your main code here, to run repeatedly:
  if(count%2 == 0)
  {
    Serial.println(".");
  }
  else
  {
    Serial.println("*");
  }
  delay(500);
  while (Serial.available() > 0) {
    digitalWrite(__R, LOW);
    key = Serial.read();
    Serial.print(key);
    
  }
  digitalWrite(__R, HIGH);
  count++;
}
