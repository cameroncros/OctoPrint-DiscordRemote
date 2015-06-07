package com.cross.beaglesightwear;

import android.util.Log;

import com.google.android.gms.wearable.DataMap;
import com.mariux.teleport.lib.TeleportService;

public class ListenService extends TeleportService {


    @Override
    public void onCreate() {
        super.onCreate();
        Log.w("Teleport", "Teleport service penis");
        //The quick way is to use setOnGetMessageTask, and set a new task
        setOnSyncDataItemTask(new StartActivityTask());
    }

    //Task that shows the path of a received message
    public class StartActivityTask extends TeleportService.OnSyncDataItemTask {

        @Override
        protected void onPostExecute(DataMap dataMap) {
            for (String key : dataMap.keySet()) {
                String string = dataMap.getByteArray(key).toString();
                Log.w("Teleport", key + " = " + string);
            }
            setOnSyncDataItemTask(new StartActivityTask());
        }
    }


}