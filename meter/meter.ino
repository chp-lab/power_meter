#include <ArduinoJson.h>

#define NUM_PHASE 3
#define INTERVAL 5*60*1000

float E[NUM_PHASE];

int count = 0;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
}

String randomMessage()
{
//  String json_str = "{\"V\":[218.75,220.30,213.8],\"I\":[10.01,11.13,12.22],\"P\":[1313.81,1716.35,1698.21],\"E\":[1000,1001,1002],\"f\":[49.52,48.9,50.11],\"pf\":[0.6,0.7,0.65]}"
  
  float V[NUM_PHASE], I[NUM_PHASE], P[NUM_PHASE], f[NUM_PHASE], pf[NUM_PHASE];
  int i;

  // Voltage
  String json_str = "{\"V\":[";
  for(i = 0; i < NUM_PHASE; i++)
  {
    V[i] = 210 + random(10);
    json_str = json_str + V[i];
    if(i < NUM_PHASE - 1)
    {
      json_str = json_str + ",";
    }
//    Serial.println("V[" + String(i) + "]= " + String(V[i]) + " V");
  }

  // Current
  json_str = json_str + "],\"I\":[";
  for(i = 0; i < NUM_PHASE; i++)
  {
    I[i] = 10 + 3*random(0, 100)/100.00;
    json_str = json_str + I[i];
    if(i < NUM_PHASE - 1)
    {
      json_str = json_str + ",";
    }
//    Serial.println(I[i]);
  }


  // Power factor
  json_str = json_str + "],\"pf\":[";
  for(i = 0; i < NUM_PHASE; i++)
  {
    pf[i] = random(70, 100)/100.00;
    json_str = json_str + pf[i];
    if(i < NUM_PHASE - 1)
    {
      json_str = json_str + ",";
    }
//    Serial.println(pf[i]);
  }


  // Power in Watt
  json_str = json_str + "],\"P\":[";
  for(i = 0; i < NUM_PHASE; i++)
  {
    P[i] = I[i]*V[i]*pf[i];
    json_str = json_str + P[i];
    if(i < NUM_PHASE - 1)
    {
      json_str = json_str + ",";
    }
//    Serial.println(P[i]);
  }

  // frequency in Hz
  json_str = json_str + "],\"f\":[";
  for(i = 0; i < NUM_PHASE; i++)
  {
    f[i] = random(48, 50);
    json_str = json_str + f[i];
    if(i < NUM_PHASE - 1)
    {
      json_str = json_str + ",";
    }
//    Serial.println(f[i]);
  }

  // Energy in kWhr
  json_str = json_str + "],\"E\":[";
  for(i = 0; i < NUM_PHASE; i ++)
  {
    float interval = INTERVAL/1000.00;
    interval = interval/(60*60.00);
    E[i] = E[i] + interval*P[i]/1000.00;
    json_str = json_str + E[i];
    if(i < NUM_PHASE - 1)
    {
      json_str = json_str + ",";
    }
//    Serial.println(E[i]);
  }
  json_str = json_str + "]}";
//  Serial.println(json_str);
  return json_str;
}

void loop() {
  // put your main code here, to run repeatedly:
  String msg = randomMessage();
  Serial.println(msg);
//  Serial.print("Count=");
//  Serial.println(count);
//  count++;
  delay(INTERVAL);
}
