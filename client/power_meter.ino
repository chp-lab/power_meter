#include <WiFiManager.h>  
#include <ESP8266WiFi.h>
#include <ArduinoOTA.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <Time.h>

#define MODEL_NAME "GN1005B"
#define FW_VERSION "FW Version 1.0.1"
#define WIFI_TIMEOUT 60*1000
#define MQTT_SERVER "nexpie-giant.ddns.net"
#define MQTT_PORT 1883
#define MQTT_USERNAME "chp-lab"
#define MQTT_PASSWORD "atop3352"
#define MQTT_NAME     "ESP32_1"
#define TOPIC "test/powermeter"
#define MQTT_MAX_RECONNECT 10
#define NUM_PHASE 3
#define INTERVAL 5*60*1000
#define MAX_LEN 1000
#define INFLUX_DOOR "mm_"
#define LOCATION "Hatyai"
#define SYNC_TIME 60*1000
#define PREPARE 60*1000

unsigned long last_wake_up = 0;
unsigned long time_elapsed = 0;
unsigned long sync_time = SYNC_TIME;
unsigned long last_sync = 0;
bool start_up = true;

WiFiClient client;
PubSubClient mqtt(client);
WiFiManager wifiManager;
byte mac[6]; 
float E[NUM_PHASE];
String client_name = "default";
String meter_id = INFLUX_DOOR;
String location = LOCATION;
int timezone = 7 * 3600;
int dst = 0;

void callback(char* topic, byte* payload, unsigned int length) 
{
  payload[length] = '\0';
  String topic_str = topic, payload_str = (char*)payload;
  Serial.println("### [" + topic_str + "]: " + payload_str);
}

void pubData(String payload, String topic)
{
    char msg1[255];
    char ch_topic[32];
    
    payload.toCharArray(msg1, payload.length() + 1);
    topic.toCharArray(ch_topic, topic.length() + 1);
    Serial.print("Publish message: ");
    Serial.println(msg1);
    Serial.println("-----");
    
    mqtt.publish(ch_topic, msg1);
    delay(100);
}

void mqtt_connect()
{
  int count = 0;
  mqtt.setServer(MQTT_SERVER, MQTT_PORT);
  mqtt.setCallback(callback);
  Serial.print("Connecting to mqtt broker");
  while(!mqtt.connect(client_name.c_str(), MQTT_USERNAME, MQTT_PASSWORD))
  {
    Serial.print("*.");
    count = count + 1;
    if(count > MQTT_MAX_RECONNECT)
    {
      Serial.println("checking internet connection...");
      if(!wifiManager.autoConnect("EE Powermeter"))
      {
        Serial.println("Failed to connect to the AP in " + String(WIFI_TIMEOUT));
        delay(3000);
        ESP.reset(); 
      }
      else
      {
        Serial.println("WiFi connected");
      }
    }
    delay(1000);
  }
  Serial.println("Mqtt connected");
  mqtt.subscribe(TOPIC);
}

void giantOta()
{
    Serial.println("Starting ota...");
    ArduinoOTA.setHostname(client_name.c_str());
    ArduinoOTA.setPassword("admin");
    ArduinoOTA.onStart([]() 
    {
      String type;
      if (ArduinoOTA.getCommand() == U_FLASH)
      {
        type = "sketch";
      }
      else
      { // U_FS
        type = "filesystem";
      }

      // NOTE: if updating FS this would be the place to unmount FS using FS.end()
      Serial.println("Start updating " + type);
    });
    ArduinoOTA.onEnd([]()
    {
      Serial.println("\nEnd");
    });
    ArduinoOTA.onProgress([](unsigned int progress, unsigned int total)
    {
      Serial.printf("Progress: %u%%\r", (progress / (total / 100)));
    });
    ArduinoOTA.onError([](ota_error_t error) 
    {
      Serial.printf("Error[%u]: ", error);
      if (error == OTA_AUTH_ERROR) 
      {
        Serial.println("Auth Failed");
      } 
      else if (error == OTA_BEGIN_ERROR) 
      {
        Serial.println("Begin Failed");
      } 
      else if (error == OTA_CONNECT_ERROR) 
      {
        Serial.println("Connect Failed");
      }
      else if (error == OTA_RECEIVE_ERROR)
      {
        Serial.println("Receive Failed");
      }
      else if (error == OTA_END_ERROR)
      {
        Serial.println("End Failed");
      }
    });
    ArduinoOTA.begin();
    Serial.println("ota started");
}

String get_client_name()
{
  String tmp_name = "powermeter_";
  char buf[3];
  Serial.print("MAC address: ");
  WiFi.macAddress(mac);
  Serial.print("MAC: ");
  Serial.print(mac[5],HEX);
  Serial.print(":");
  Serial.print(mac[4],HEX);
  Serial.print(":");
  Serial.print(mac[3],HEX);
  Serial.print(":");
  Serial.print(mac[2],HEX);
  Serial.print(":");
  Serial.print(mac[1],HEX);
  Serial.print(":");
  Serial.println(mac[0],HEX);
  sprintf(buf, "%2X", mac[0]);
  for(byte i = 3; i < 6; i++ )
  {
    char buf[3];
    sprintf(buf, "%2X", mac[i]);
    tmp_name += buf;
  }

  Serial.println("tmp_name=" + tmp_name);
  return tmp_name;
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

void setup() {
  Serial.begin(115200);
  
  randomSeed(analogRead(0));
  
  Serial.println(MODEL_NAME);
  Serial.println(FW_VERSION);
  
  wifiManager.setTimeout(WIFI_TIMEOUT);
  client_name = get_client_name();
  meter_id = meter_id + client_name;
  Serial.println("client_name=" + client_name);
  Serial.println("meter_id=" + meter_id);
  if(!wifiManager.autoConnect(client_name.c_str()))
  {
    Serial.println("Failed to connect to the AP in " + String(WIFI_TIMEOUT));
    delay(3000);
    ESP.reset();
  }
  else
  {
    Serial.println("Ready");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
    giantOta();
    mqtt_connect();
  }
  last_wake_up =  millis();
  Serial.println("Sync time");
  configTime(timezone, dst, "pool.ntp.org", "time.nist.gov");
  while (!time(nullptr)) {
    Serial.print(".");
    delay(1000);
  }
  last_sync = millis();
  Serial.println("Success, waiting for schedule");
  delay(PREPARE);
}

String uart_read()
{
  return randomMessage();
}

String influx_inline(String j_str)
{
//  StaticJsonDocument<2000> doc;
  DynamicJsonDocument doc(2000);
  
  DeserializationError error = deserializeJson(doc, j_str);
  if (error) {
    Serial.print(F("deserializeJson() failed: "));
    Serial.println(error.c_str());
    return "falied";
  }
  /*
   * 1. V
   * 2. I
   * 3. pf
   * 4. P,
   * 5. f
   * 6. E
   */
  float V[NUM_PHASE];
  float I[NUM_PHASE];
  float pf[NUM_PHASE];
  float P[NUM_PHASE];
  float f[NUM_PHASE];
  float E[NUM_PHASE];
  int i;

  // V
  for(i = 0; i < NUM_PHASE; i++)
  {
    V[i] = doc["V"][i];
//    Serial.println("V[" + String(i) + "]=" + String(V[i]));
  }

  // I
  for(i = 0; i < NUM_PHASE; i++)
  {
    I[i] = doc["I"][i];
//    Serial.println("I[" + String(i) + "]=" + String(I[i]));
  }

  // pf
  for(i = 0; i < NUM_PHASE; i++)
  {
    pf[i] = doc["pf"][i];
//    Serial.println("pf[" + String(i) + "]=" + String(pf[i]));
  }

  // P
  for(i = 0; i < NUM_PHASE; i++)
  {
    P[i] = doc["P"][i];
//    Serial.println("P[" + String(i) + "]=" + String(P[i]));
  }

  // f
  for(i = 0; i < NUM_PHASE; i++)
  {
    f[i] = doc["f"][i];
//    Serial.println("f[" + String(i) + "]=" + String(f[i]));
  }

  // E
  for(i = 0; i < NUM_PHASE; i++)
  {
    E[i] = doc["E"][i];
//    Serial.println("E[" + String(i) + "]=" + String(E[i]));
  }

  String ts = get_time();
  String influx_msg = meter_id + ",location=" + location + " V0=" + String(V[0]) + ",V1=" + String(V[1]) + ",V2=" + String(V[2]) + ",I0=" + String(I[0]) + ",I1=" + String(I[1]) + ",I2=" + String(I[2]) + \
  ",pf0=" + String(pf[0]) + ",pf1=" + String(pf[1]) + ",pf2=" + String(pf[2]) + ",P0=" + String(P[0]) + ",P1=" + String(P[1]) + ",P2=" + String(P[2]) + ",f0=" + String(f[0]) + ",f1=" + String(f[1]) + ",f2=" + String(f[2]) + \
  ",E0=" + String(E[0]) + ",E1=" + String(E[1]) + ",E2=" + String(E[2]) + " " + ts;
//  Serial.println("influx_msg=" + influx_msg);
  return influx_msg;
}

String get_time()
{
  time_t now = time(nullptr);
  struct tm* p_tm = localtime(&now);
  String cur_ts = String(now) + "000000000";
  Serial.println(cur_ts);
  return cur_ts;
}

void loop() {
  String msg;
  String res = "";
  ArduinoOTA.handle();
  time_elapsed = millis() - last_wake_up;

  if((millis() - last_sync) > sync_time)
  {
    Serial.println("Sync time");
    configTime(timezone, dst, "pool.ntp.org", "time.nist.gov");
    last_sync = millis();
  }
  if((abs(time_elapsed) > INTERVAL) || start_up)
  {
    start_up = false;
//    Serial.println("Time elapsed=" + String(time_elapsed));
    last_wake_up = millis();
    time_elapsed = 0;
    if(!mqtt.connected())
    {
      Serial.println("mqtt client not connect");
      mqtt_connect();
    }
    mqtt.loop();
    
    msg = uart_read();
//    Serial.println("msg=" + msg);
    res = influx_inline(msg);
    Serial.println("res=" + res);
    pubData(res, "influx/" + meter_id);
  }
  delay(10);
}
