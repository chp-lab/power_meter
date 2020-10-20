#include <chp.h>

void setup() {
  Serial.begin(115200);
  // chp init
  chp_init();
  // set sync time from NTP server
  set_sync_time(30*1000);
  Serial.println("Sync time=" + String(get_sync_time()));
  // set upload schedule
  set_interval(60*1000);
  Serial.println("Interval=" + String(get_interval()));
}

void loop() {
  String tmp_msg;
  String msg;
  String res = "";

  // create your message
  tmp_msg = uart_read();
  // confirm msg exist
  if(tmp_msg.length() > 0)
  {
    msg = tmp_msg;
  }

  // OTA
  listen_for_fw();
  // CHP loop
  chp_loop();
  // Sync time from NTP server
  time_to_sync();

  // Check sending schedule
  if(time_to_send())
  {    
    res = influx_inline(msg);
    Serial.println("res=" + res);
    pubData(res, "influx/" + device_id());
  }
  delay(1000);
}
