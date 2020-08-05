#define NB_POSSIBLE_SENSORS 4


struct temp_sensors_s {
   uint32_t addr0;
   uint32_t addr1;
   homekit_characteristic_t *c;
}

struct temp_sensors_s temp_sensors[NB_SENSORS];


void temperature_ds18b20_cb(float currentvalue, float prevvalue, void *userdata)
{
   int id=(int)userdata;
   homekit_characteristic_t *c=temp_sensors[id].c;

   c->value.float_value = currentvalue;
   if(currentvalue != prevvalue) {
      char device[3]="tX";
      device[1]='0'+id;
      homekit_characteristic_notify(c, HOMEKIT_FLOAT(currentvalue));
      xpl_send_current_float(xpl_get_sock(), "trig", device, currentvalue);
   }
}


int ds18x20_init()
{
   for(int i=0;i<NB_POSSIBLE_SENSORS;i++) {
      temp_sensors[i]={.addr0=0, .addr1=0 }
   }
}


int ds18x20_find_addr(uint32_t _addr0, uint32_t _addr1)
{
   for(int i=0;i<NB_POSSIBLE_SENSORS;i++) {
      if(temp_sensors[i].addr0==_addr0 && temp_sensors[i].addr1==_addr1) {
         return i;
      }
   }
   return -1;
}


int ds18x20_find_next_free()
{
   for(int i=0;i<NB_POSSIBLE_SENSORS;i++) {
      if(temp_sensors[i].addr0==0 && temp_sensors[i].addr1==0) {
         return i;
      }
   }
   return -1;
}


int ds18x20_add_new_devices()
{
   uint32_t addr0, addr1;

   for(int i=0;i<MAX_SENSORS;i++) {
      if(temperature_ds18b20_get_addr_by_id_2(i, &addr0, &addr1)) {
         int id=ds18x20_find_addr(addr0, addr1);
         if(id!=-1) {
            id=ds18x20_find_next_free();
            if(id==-1) {
               break;
            }
            temp_sensors[id].addr0=addr0;
            temp_sensors[id].addr1=addr1;
            temperature_ds18b20_set_cb_by_addr_2(addr0, addr1, temperature_ds18b20_cb, (void *)i, i);
         }
      }
   }
   return 1;
}


int ds18x20_load_devices()
{
   nvs_handle_t h;

   esp_err_t ret = nvs_open("my_ds18x20", NVS_READWRITE, &h);
   if (ret != ESP_OK) {
      return 0;
   }

   ret=nvs_get_blob(h, "sensors", temp_sensors, sizeof(temp_sensors));
   if(ret==ESP_OK) {
      mvs_close(h);
      return 1;
   }
   else if(ret==ESP_ERR_NVS_NOT_FOUND) {
      if(nvs_set_blob(h, "sensors", temp_sensors, sizeof(temp_sensors))==ESP_OK) {
         nvs_commit(h);
         mvs_close(h);
         return 1;
      }
   }

   mvs_close(h);
   return 0;
}


int ds18x20_save_devices()
{
   nvs_handle_t h;

   esp_err_t ret = nvs_open("my_ds18x20", NVS_READWRITE, &h);
   if (ret != ESP_OK) {
      return 0;
   }
   if(nvs_set_blob(h, "sensors", temp_sensors, sizeof(temp_sensors))==ESP_OK) {
      nvs_commit(h);
      mvs_close(h);
      return 1;
   }
   else {
      mvs_close(h);
      return 0;
   }
}


int ds18x20_create_devices_caracteristics()
{
   for(int i=0;i<NB_POSSIBLE_SENSORS;i++) {
      if(temp_sensors[i].addr0==0 && temp_sensors[i].addr1==0) {
         temp_sensors[i].c=NEW_HOMEKIT_CHARACTERISTIC(CURRENT_TEMPERATURE, 0, NULL);
      }
   }
}


/*
temperature_ds18b20_init_2();

ds18x20_init();
ds18x20_load_devices();
ds18x20_add_new_devices();
ds18x20_save_devices();
ds18x20_create_devices_caracteristics();
*/
