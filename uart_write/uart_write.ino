int count = 0;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  Serial.println("\nUart write");
}

void loop() {
  // put your main code here, to run repeatedly:
  Serial.println(count);
  count++;
  delay(1000);
}
